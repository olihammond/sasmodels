# Note: model title and parameter table are inserted automatically
r"""
This model provides the scattering intensity, $I(q)$, for a lyotropic lamellar
phase where a random distribution in solution are assumed. The SLD of the head
region is taken to be different from the SLD of the tail region.

Definition
----------

The scattering intensity $I(q)$ is

.. math::

   I(q) = 2\pi\frac{\text{scale}}{2(\delta_H + \delta_T)}  P(q) \frac{1}{q^2}

The form factor $P(q)$ is

.. math::

    P(q) = \frac{4}{q^2}
        \left\lbrace
            \Delta \rho_H
            \left[\sin[q(\delta_H + \delta_T)\ - \sin(q\delta_T)\right]
            + \Delta\rho_T\sin(q\delta_T)
        \right\rbrace^2

where $\delta_T$ is *tail_length*, $\delta_H$ is *head_length*,
$\Delta\rho_H$ is the head contrast (*sld_head* $-$ *sld_solvent*),
and $\Delta\rho_T$ is tail contrast (*sld* $-$ *sld_solvent*).

The total thickness of the lamellar sheet is $\delta_H$ + $\delta_T$ + $\delta_T$ + $\delta_H$.
Note that in a non aqueous solvent the chemical "head" group may be the 
"Tail region" and vice-versa.

The 2D scattering intensity is calculated in the same way as 1D, where
the $q$ vector is defined as

.. math::

    q = \sqrt{q_x^2 + q_y^2}


References
----------

F Nallet, R Laversanne, and D Roux, J. Phys. II France, 3, (1993) 487-502

also in J. Phys. Chem. B, 105, (2001) 11081-11088

*2014/04/17 - Description reviewed by S King and P Butler.*
"""

from numpy import inf

name = "lamellar_hg"
title = "Random lamellar phase with Head and Tail Groups"
description = """\
    [Random lamellar phase with Head and Tail Groups]
        I(q)= 2*pi*P(q)/(2(H+T)*q^(2)), where
        P(q)= see manual
        layer thickness =(H+T+T+H) = 2(Head+Tail)
        sld = Tail scattering length density
        sld_head = Head scattering length density
        sld_solvent = solvent scattering length density
        background = incoherent background
        scale = scale factor
"""
category = "shape:lamellae"

# pylint: disable=bad-whitespace, line-too-long
#             ["name", "units", default, [lower, upper], "type","description"],
parameters = [["tail_length", "Ang",       15,   [0, inf],  "volume",  "Tail thickness ( total = H+T+T+H)"],
              ["head_length", "Ang",       10,   [0, inf],  "volume",  "Head thickness"],
              ["sld",         "1e-6/Ang^2", 0.4, [-inf,inf], "",       "Tail scattering length density"],
              ["sld_head",    "1e-6/Ang^2", 3.0, [-inf,inf], "",       "Head scattering length density"],
              ["sld_solvent", "1e-6/Ang^2", 6,   [-inf,inf], "",       "Solvent scattering length density"]]
# pylint: enable=bad-whitespace, line-too-long

# No volume normalization despite having a volume parameter
# This should perhaps be volume normalized?
form_volume = """
    return 1.0;
    """

Iq = """
    const double qsq = q*q;
    const double drh = sld_head - sld_solvent;
    const double drt = sld - sld_solvent;    //correction 13FEB06 by L.Porcar
    const double qT = q*tail_length;
    double Pq, inten;
    Pq = drh*(sin(q*(head_length+tail_length))-sin(qT)) + drt*sin(qT);
    Pq *= Pq;
    Pq *= 4.0/(qsq);

    inten = 2.0e-4*M_PI*Pq/qsq;

    // normalize by the bilayer thickness
    inten /= 2.0*(head_length+tail_length);

    return inten;
    """

# ER defaults to 0.0
# VR defaults to 1.0

demo = dict(scale=1, background=0,
            tail_length=15, head_length=10,
            sld=0.4, sld_head=3.0, sld_solvent=6.0,
            tail_length_pd=0.2, tail_length_pd_n=40,
            head_length_pd=0.01, head_length_pd_n=40)

#
tests = [[{'scale': 1.0, 'background': 0.0, 'tail_length': 15.0, 'head_length': 10.0,
           'sld': 0.4, 'sld_head': 3.0, 'sld_solvent': 6.0}, [0.001], [653143.9209]]]
# ADDED by: RKH  ON: 18Mar2016  converted from sasview previously, now renaming everything & sorting the docs