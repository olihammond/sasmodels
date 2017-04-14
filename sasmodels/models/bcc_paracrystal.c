static double
_sq_bcc(double qa, double qb, double qc, double dnn, double d_factor)
{
    // Rewriting equations for efficiency, accuracy and readability, and so
    // code is reusable between 1D and 2D models.
    const double a1 = +qa - qc + qb;
    const double a2 = +qa + qc - qb;
    const double a3 = -qa + qc + qb;

    const double half_dnn = 0.5*dnn;
    const double arg = 0.5*square(half_dnn*d_factor)*(a1*a1 + a2*a2 + a3*a3);

#if 1
    // Numerator: (1 - exp(a)^2)^3
    //         => (-(exp(2a) - 1))^3
    //         => -expm1(2a)^3
    // Denominator: prod(1 - 2 cos(xk) exp(a) + exp(a)^2)
    //         => exp(a)^2 - 2 cos(xk) exp(a) + 1
    //         => (exp(a) - 2 cos(xk)) * exp(a) + 1
    const double exp_arg = exp(-arg);
    const double Sq = -cube(expm1(-2.0*arg))
        / ( ((exp_arg - 2.0*cos(half_dnn*a1))*exp_arg + 1.0)
          * ((exp_arg - 2.0*cos(half_dnn*a2))*exp_arg + 1.0)
          * ((exp_arg - 2.0*cos(half_dnn*a3))*exp_arg + 1.0));
#else
    // Alternate form, which perhaps is more approachable
    const double sinh_qd = sinh(arg);
    const double cosh_qd = cosh(arg);
    const double Sq = sinh_qd/(cosh_qd - cos(half_dnn*a1))
                    * sinh_qd/(cosh_qd - cos(half_dnn*a2))
                    * sinh_qd/(cosh_qd - cos(half_dnn*a3));
#endif

    return Sq;
}


// occupied volume fraction calculated from lattice symmetry and sphere radius
static double
_bcc_volume_fraction(double radius, double dnn)
{
    return 2.0*sphere_volume(sqrt(0.75)*radius/dnn);
}

static double
form_volume(double radius)
{
    return sphere_volume(radius);
}


static double Iq(double q, double dnn,
  double d_factor, double radius,
  double sld, double solvent_sld)
{
    // translate a point in [-1,1] to a point in [0, 2 pi]
    const double phi_m = M_PI;
    const double phi_b = M_PI;
    // translate a point in [-1,1] to a point in [0, pi]
    const double theta_m = M_PI_2;
    const double theta_b = M_PI_2;

    double outer_sum = 0.0;
    for(int i=0; i<150; i++) {
        double inner_sum = 0.0;
        const double theta = Gauss150Z[i]*theta_m + theta_b;
        double sin_theta, cos_theta;
        SINCOS(theta, sin_theta, cos_theta);
        const double qc = q*cos_theta;
        const double qab = q*sin_theta;
        for(int j=0;j<150;j++) {
            const double phi = Gauss150Z[j]*phi_m + phi_b;
            double sin_phi, cos_phi;
            SINCOS(phi, sin_phi, cos_phi);
            const double qa = qab*cos_phi;
            const double qb = qab*sin_phi;
            const double fq = _sq_bcc(qa, qb, qc, dnn, d_factor);
            inner_sum += Gauss150Wt[j] * fq;
        }
        inner_sum *= phi_m;  // sum(f(x)dx) = sum(f(x)) dx
        outer_sum += Gauss150Wt[i] * inner_sum * sin_theta;
    }
    outer_sum *= theta_m;
    const double Sq = outer_sum/(4.0*M_PI);
    const double Pq = sphere_form(q, radius, sld, solvent_sld);

    return _bcc_volume_fraction(radius, dnn) * Pq * Sq;
}


static double Iqxy(double qx, double qy,
    double dnn, double d_factor, double radius,
    double sld, double solvent_sld,
    double theta, double phi, double psi)
{
    double q, zhat, yhat, xhat;
    ORIENT_ASYMMETRIC(qx, qy, theta, phi, psi, q, xhat, yhat, zhat);
    const double qa = q*xhat;
    const double qb = q*yhat;
    const double qc = q*zhat;

    q = sqrt(qa*qa + qb*qb + qc*qc);
    const double Pq = sphere_form(q, radius, sld, solvent_sld);
    const double Sq = _sq_bcc(qa, qb, qc, dnn, d_factor);
    return _bcc_volume_fraction(radius, dnn) * Pq * Sq;
}