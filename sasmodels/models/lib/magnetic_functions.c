static double fq_core_shell(double q, double sld_core, double radius,
   double sld_solvent, double fp_n, double sld[], double thickness[])
{
  const int n = (int)(fp_n+0.5);
  double f, r, last_sld;
  r = radius;
  last_sld = sld_core;
  f = 0.;
  for (int i=0; i<n; i++) {
    f += M_4PI_3 * cube(r) * (sld[i] - last_sld) * sas_3j1x_x(q*r);
    last_sld = sld[i];
    r += thickness[i];
  }
  f += M_4PI_3 * cube(r) * (sld_solvent - last_sld) * sas_3j1x_x(q*r);
  return f;
}

static double langevin(
    double x) {
    // cotanh(x)-1\x

    if (x < 0.00001) {
        // avoid dividing by zero
        return 1.0/3.0*x;
    } else {
        return 1.0/tanh(x)-1/x;
    }
}

static double langevinoverx(
    double x) 
{
    // cotanh(x)-1\x

    if (x < 0.00001) {
        // avoid dividing by zero
        return 1.0/3.0;
    } else {
        return langevin(x)/x;
    }
}

//weighting of spin resolved cross sections to reconstruct partially polarised beam with imperfect optics using up_i/up_f.
static void set_weights(double in_spin, double out_spin, double weight[8]) //from kernel_iq.c
{
 double norm=out_spin;


   in_spin = clip(sqrt(square(in_spin)), 0.0, 1.0);//opencl has ambiguities for abs()
   out_spin = clip(sqrt(square(out_spin)), 0.0, 1.0);

   if (out_spin < 0.5){norm=1-out_spin;}

// The norm is needed to make sure that the scattering cross sections are
//correctly weighted, such that the sum of spin-resolved measurements adds up to
// the unpolarised or half-polarised scattering cross section. No intensity weighting
// needed on the incoming polariser side assuming that a user has normalised
// to the incoming flux with polariser in for SANSPOl and unpolarised beam, respectively.


   weight[0] = (1.0-in_spin) * (1.0-out_spin) / norm; // dd.real
   weight[1] = weight[0]; // dd.imag
   weight[2] = in_spin * out_spin / norm;             // uu.real
   weight[3] = weight[2];             // uu.imag
   weight[4] = (1.0-in_spin) * out_spin / norm;       // du.real
   weight[5] = weight[4];       // du.imag 
   weight[6] = in_spin * (1.0-out_spin) / norm;       // ud.real
   weight[7] = weight[6];       // ud.imag
 }



//some basic vector algebra

void SET_VEC(double *vector, double v0, double v1, double v2)
{
 vector[0] = v0;
 vector[1] = v1;
 vector[2] = v2;
}

void SCALE_VEC(double *vector, double a)
{
 vector[0] = a*vector[0];
 vector[1] = a*vector[1];
 vector[2] = a*vector[2];
}

void ADD_VEC(double *result_vec, double *vec1, double *vec2)
{
 result_vec[0] = vec1[0] + vec2[0];
 result_vec[1] = vec1[1] + vec2[1];
 result_vec[2] = vec1[2] + vec2[2];
}

static double SCALAR_VEC( double *vec1, double *vec2)
{
 return vec1[0] * vec2[0] + vec1[1] * vec2[1] + vec1[2] * vec2[2];
}

static double MAG_VEC( double v0, double v1, double v2)
{
 double vec[3];
 SET_VEC(vec, v0, v1, v2);   
 return sqrt(SCALAR_VEC(vec,vec));
}

void ORTH_VEC(double *result_vec, double *vec1, double *vec2)
{
 result_vec[0] = vec1[0] - SCALAR_VEC(vec1,vec2) / SCALAR_VEC(vec2,vec2) * vec2[0];
 result_vec[1] = vec1[1] - SCALAR_VEC(vec1,vec2) / SCALAR_VEC(vec2,vec2) * vec2[1];
 result_vec[2] = vec1[2] - SCALAR_VEC(vec1,vec2) / SCALAR_VEC(vec2,vec2) * vec2[2];
}

//transforms scattering vector q in polarisation/magnetisation coordinate system
 static void set_scatvec(double *qrot, double q,
  double cos_theta, double sin_theta,
  double alpha, double beta)
{
  double cos_alpha, sin_alpha;
  double cos_beta, sin_beta;

  SINCOS(alpha*M_PI/180, sin_alpha, cos_alpha);
  SINCOS(beta*M_PI/180, sin_beta, cos_beta);
  //field is defined along (0,0,1), orientation of detector
  //is precessing in a cone around B with an inclination of theta

  qrot[0] = q*(cos_alpha * cos_theta);
  qrot[1] = q*(cos_theta * sin_alpha*sin_beta + 
  cos_beta * sin_theta);
  qrot[2] = q*(-cos_beta * cos_theta* sin_alpha + 
  sin_beta * sin_theta);
}



//Evaluating the magnetic scattering vector (Halpern Johnson vector) for general orientation of q and collecting terms for the spin-resolved (POLARIS) cross sections. Mz is along the applied magnetic field direction, which is also the polarisation direction.
static void mag_sld(
   // 0=dd.real, 1=dd.imag, 2=uu.real, 3=uu.imag,  4=du.real, 5=du.imag,  6=ud.real, 7=ud.imag
 double x, double y, double z,
  double mxreal, double mximag, double myreal,  double myimag, double mzreal,double mzimag, double nuc, double sld[8])
{
  double vector[3];
  //The (transversal) magnetisation and hence the magnetic scattering sector is here a complex quantity. The spin-flip (magnetic) scattering amplitude is given with
  //  MperpPperpQ \pm i MperpP  (Moon-Riste-Koehler Phys Rev 181, 920, 1969) with Mperp and MperpPperpQ the
  //magnetisation scattering vector components perpendicular to the polarisation/field direction. Collecting terms in SF that are real (MperpPperpQreal + SCALAR_VEC(MperpPimag,qvector) )  and imaginary (MperpPperpQimag \pm SCALAR_VEC(MperpPreal,qvector) )
  double Mvectorreal[3];
  double Mvectorimag[3];
  double Pvector[3];
  double perpy[3];
  double perpx[3]; 

  double Mperpreal[3];
  double Mperpimag[3];
  
  const double q = sqrt(x*x + y*y + z*z);
  SET_VEC(vector, x/q, y/q, z/q); 

  //Moon-Riste-Koehler notation choose z as pointing along field/polarisation axis
  //totally different to what is used in SASview (historical reasons)
  SET_VEC(Mvectorreal, mxreal, myreal, mzreal);
  SET_VEC(Mvectorimag, mximag, myimag, mzimag);

  SET_VEC(Pvector, 0, 0, 1);
  SET_VEC(perpy, 0, 1, 0);  
  SET_VEC(perpx, 1, 0, 0);   
   //Magnetic scattering vector Mperp could be simplified like in Moon-Riste-Koehler
   //leave the generic computation just to check
  ORTH_VEC(Mperpreal, Mvectorreal, vector);
  ORTH_VEC(Mperpimag, Mvectorimag, vector);
  
  
   sld[0] = nuc - SCALAR_VEC(Pvector,Mperpreal); // dd.real => sld - D Pvector \cdot Mperp 
   sld[1] = +SCALAR_VEC(Pvector,Mperpimag); //dd.imag  = nuc_img - SCALAR_VEC(Pvector,Mperpimg); nuc_img only exist for noncentrosymmetric nuclear structures; 
   sld[2] = nuc + SCALAR_VEC(Pvector,Mperpreal);              // uu => sld + D Pvector \cdot Mperp
   sld[3] = -SCALAR_VEC(Pvector,Mperpimag); //uu.imag

   sld[4] = SCALAR_VEC(perpy,Mperpreal)+SCALAR_VEC(perpx,Mperpimag);       // du.real => real part along y + imaginary part along x
   sld[5] = SCALAR_VEC(perpy,Mperpimag)-SCALAR_VEC(perpx,Mperpreal);       // du.imag => imaginary component along y - i *real part along x
   sld[6] = SCALAR_VEC(perpy,Mperpreal)-SCALAR_VEC(perpx,Mperpimag);      // ud.real =>  real part along y - imaginary part along x
   sld[7] = SCALAR_VEC(perpy,Mperpimag)+SCALAR_VEC(perpx,Mperpreal);         // ud.imag => imaginary component along y + i * real part along x

 }