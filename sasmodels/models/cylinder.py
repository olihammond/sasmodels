# cylinder model
# Note: model title and parameter table are inserted automatically
r"""
The form factor is normalized by the particle volume V = \piR^2L.

Definition
----------

The output of the 2D scattering intensity function for oriented cylinders is
given by (Guinier, 1955)

.. math::

    P(q,\alpha) = \frac{\text{scale}}{V} F^2(q) + \text{background}

where

.. math::

    F(q) = 2 (\Delta \rho) V
           \frac{\sin \left(\tfrac12 qL\cos\alpha \right)}
                {\tfrac12 qL \cos \alpha}
           \frac{J_1 \left(q R \sin \alpha\right)}{q R \sin \alpha}

and $\alpha$ is the angle between the axis of the cylinder and $\vec q$, $V$
is the volume of the cylinder, $L$ is the length of the cylinder, $R$ is the
radius of the cylinder, and $\Delta\rho$ (contrast) is the scattering length
density difference between the scatterer and the solvent. $J_1$ is the
first order Bessel function.

To provide easy access to the orientation of the cylinder, we define the
axis of the cylinder using two angles $\theta$ and $\phi$. Those angles
are defined in :num:`figure #cylinder-angle-definition`.

.. _cylinder-angle-definition:

.. figure:: img/cylinder_angle_definition.jpg

    Definition of the angles for oriented cylinders.

.. figure:: img/cylinder_angle_projection.jpg

    Examples of the angles for oriented cylinders against the detector plane.

NB: The 2nd virial coefficient of the cylinder is calculated based on the
radius and length values, and used as the effective radius for $S(q)$
when $P(q) \cdot S(q)$ is applied.

The output of the 1D scattering intensity function for randomly oriented
cylinders is then given by

.. math::

    P(q) = \frac{\text{scale}}{V}
        \int_0^{\pi/2} F^2(q,\alpha) \sin \alpha\ d\alpha + \text{background}

The $\theta$ and $\phi$ parameters are not used for the 1D output.

Validation
----------

Validation of the code was done by comparing the output of the 1D model
to the output of the software provided by the NIST (Kline, 2006).
The implementation of the intensity for fully oriented cylinders was done
by averaging over a uniform distribution of orientations using

.. math::

    P(q) = \int_0^{\pi/2} d\phi
        \int_0^\pi p(\theta, \phi) P_0(q,\alpha) \sin \theta\ d\theta


where $p(\theta,\phi)$ is the probability distribution for the orientation
and $P_0(q,\alpha)$ is the scattering intensity for the fully oriented
system, and then comparing to the 1D result.

References
----------

None

"""

import numpy as np
from numpy import pi, inf

name = "cylinder"
title = "Right circular cylinder with uniform scattering length density."
description = """
     f(q,alpha) = 2*(sld - sld_solvent)*V*sin(qLcos(alpha)/2))
                /[qLcos(alpha)/2]*J1(qRsin(alpha))/[qRsin(alpha)]

            P(q,alpha)= scale/V*f(q,alpha)^(2)+background
            V: Volume of the cylinder
            R: Radius of the cylinder
            L: Length of the cylinder
            J1: The bessel function
            alpha: angle between the axis of the
            cylinder and the q-vector for 1D
            :the ouput is P(q)=scale/V*integral
            from pi/2 to zero of...
            f(q,alpha)^(2)*sin(alpha)*dalpha + background
"""
category = "shape:cylinder"

#             [ "name", "units", default, [lower, upper], "type", "description"],
parameters = [["sld", "4e-6/Ang^2", 4, [-inf, inf], "",
               "Cylinder scattering length density"],
              ["sld_solvent", "1e-6/Ang^2", 1, [-inf, inf], "",
               "Solvent scattering length density"],
              ["radius", "Ang", 20, [0, inf], "volume",
               "Cylinder radius"],
              ["length", "Ang", 400, [0, inf], "volume",
               "Cylinder length"],
              ["theta", "degrees", 60, [-inf, inf], "orientation",
               "In plane angle"],
              ["phi", "degrees", 60, [-inf, inf], "orientation",
               "Out of plane angle"],
             ]

source = ["lib/J1c.c", "lib/gauss76.c", "cylinder.c"]

def ER(radius, length):
    """
        Return equivalent radius (ER)
    """
    ddd = 0.75 * radius * (2 * radius * length + (length + radius) * (length + pi * radius))
    return 0.5 * (ddd) ** (1. / 3.)

# parameters for demo
demo = dict(scale=1, background=0,
            sld=6, sld_solvent=1,
            radius=20, length=300,
            theta=60, phi=60,
            radius_pd=.2, radius_pd_n=9,
            length_pd=.2, length_pd_n=10,
            theta_pd=10, theta_pd_n=5,
            phi_pd=10, phi_pd_n=5)

# For testing against the old sasview models, include the converted parameter
# names and the target sasview model name.
oldname = 'CylinderModel'
oldpars = dict(theta='cyl_theta', phi='cyl_phi', sld='sldCyl', sld_solvent='sldSolv')


qx, qy = 0.2 * np.cos(2.5), 0.2 * np.sin(2.5)
tests = [[{}, 0.2, 0.042761386790780453],
         [{}, [0.2], [0.042761386790780453]],
         [{'theta':10.0, 'phi':10.0}, (qx, qy), 0.03514647218513852],
         [{'theta':10.0, 'phi':10.0}, [(qx, qy)], [0.03514647218513852]],
        ]
del qx, qy  # not necessary to delete, but cleaner
# ADDED by:  RKH  ON: 18Mar2016 renamed sld's etc
