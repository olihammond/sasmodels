# pylint: disable=line-too-long
r"""
Calculates the scattering for a generalized Guinier/power law object.
This is an empirical model that can be used to determine the size
and dimensionality of scattering objects, including asymmetric objects
such as rods or platelets, and shapes intermediate between spheres
and rods or between rods and platelets.

Definition
----------

The following functional form is used

.. math::
    I(q) = \frac{G}{Q^s} \ \exp{\left[ \frac{-Q^2R_g^2}{3-s} \right]} \textrm{ for } Q \leq Q_1
    \\
    I(q) = D / Q^m \textrm{ for } Q \geq Q_1

This is based on the generalized Guinier law for such elongated objects
(see the Glatter reference below). For 3D globular objects (such as spheres), $s = 0$
and one recovers the standard Guinier formula.
For 2D symmetry (such as for rods) $s = 1$,
and for 1D symmetry (such as for lamellae or platelets) $s = 2$.
A dimensionality parameter ($3-s$) is thus defined, and is 3 for spherical objects,
2 for rods, and 1 for plates.

Enforcing the continuity of the Guinier and Porod functions and their derivatives yields

.. math::
    Q_1 = \frac{1}{R_g} \sqrt{(m-s)(3-s)/2}

and

.. math::
    D = G \ \exp{ \left[ \frac{-Q_1^2 R_g^2}{3-s} \right]} \ Q_1^{m-s}
      = \frac{G}{R_g^{m-s}} \ \exp{\left[  -\frac{m-s}{2} \right]} \left( \frac{(m-s)(3-s)}{2} \right)^{\frac{m-s}{2}}


Note that the radius-of-gyration for a sphere of radius R is given by $R_g = R \sqrt(3/5)$.

The cross-sectional radius-of-gyration for a randomly oriented cylinder
of radius R is given by $R_g = R / \sqrt(2)$.

The cross-sectional radius-of-gyration of a randomly oriented lamella
of thickness $T$ is given by $R_g = T / \sqrt(12)$.

For 2D data: The 2D scattering intensity is calculated in the same way as 1D,
where the q vector is defined as

.. math::
    q = \sqrt{q_x^2+q_y^2}


Reference
---------

A Guinier, G Fournet, Small-Angle Scattering of X-Rays, John Wiley and Sons, New York, (1955)

O Glatter, O Kratky, Small-Angle X-Ray Scattering, Academic Press (1982)
Check out Chapter 4 on Data Treatment, pages 155-156.
"""

from numpy import inf, sqrt, power, exp

name = "guinier_porod"
title = "Guinier-Porod function"
description = """\
         I(q) = scale/q^s* exp ( - R_g^2 q^2 / (3-s) ) for q<= ql
         = scale/q^m*exp((-ql^2*Rg^2)/(3-s))*ql^(m-s) for q>=ql
                        where ql = sqrt((m-s)(3-s)/2)/Rg.
                        List of parameters:
                        scale = Guinier Scale
                        s = Dimension Variable
                        Rg = Radius of Gyration [A] 
                        m = Porod Exponent
                        background  = Background [1/cm]"""

category = "shape-independent"

# pylint: disable=bad-whitespace, line-too-long
#             ["name", "units", default, [lower, upper], "type","description"],
parameters = [["rg", "Ang", 60.0, [0, inf], "", "Radius of gyration"],
              ["s",  "",    1.0,  [0, inf], "", "Dimension variable"],
              ["m",  "",    3.0,  [0, inf], "", "Porod exponent"]]
# pylint: enable=bad-whitespace, line-too-long

# pylint: disable=C0103
def Iq(q, rg, s, m):
    """
    @param q: Input q-value
    """
    n = 3.0 - s

    # Take care of the singular points
    if rg <= 0.0:
        return 0.0
    if (n-3.0+m) <= 0.0:
        return 0.0

    # Do the calculation and return the function value
    q1 = sqrt((n-3.0+m)*n/2.0)/rg
    if q < q1:
        iq = (1.0/power(q, (3.0-n)))*exp((-q*q*rg*rg)/n)
    else:
        iq = (1.0/power(q, m))*exp(-(n-3.0+m)/2.0)*power(((n-3.0+m)*n/2.0),
                                                         ((n-3.0+m)/2.0))/power(rg, (n-3.0+m))
    return iq

Iq.vectorized = False  # Iq accepts an array of q values

def Iqxy(qx, qy, *args):
    """
    @param qx:   Input q_x-value
    @param qy:   Input q_y-value
    @param args: Remaining arguments
    """
    return Iq(sqrt(qx ** 2 + qy ** 2), *args)

Iqxy.vectorized = False # Iqxy accepts an array of qx, qy values

demo = dict(scale=1.5, background=0.5, rg=60, s=1.0, m=3.0)

oldname = "GuinierPorodModel"
oldpars = dict(scale='scale', background='background', s='dim', m='m', rg='rg')

tests = [[{'scale': 1.5, 'background':0.5}, 0.04, 5.290096890253155]]
