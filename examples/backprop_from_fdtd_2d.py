#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
2D backpropagation (FDTD)
~~~~~~~~~~~~~~~~~~~~~~~~~
The *in silico* data set was created with the 
:abbr:`FDTD (Finite Difference Time Domain)` software `meep`_. The data
are 1D projections of a 2D refractive index phantom. The
reconstruction of the refractive index with the Rytov approximation
is in good agreement with the phantom that was used in the
simulation.

.. figure::  ../examples/backprop_from_fdtd_2d_repo.png
   :align:   center

   2D reconstruction from :abbr:`FDTD (Finite Difference Time Domain)`
   data created by `meep`_ simulations.

Download the :download:`full example <../examples/backprop_from_fdtd_2d.py>`.

.. _`meep`: http://ab-initio.mit.edu/wiki/index.php/Meep

"""
from __future__ import division, print_function


if __name__ == "__main__":
    import matplotlib.pylab as plt
    import numpy as np
    from os.path import abspath, dirname, join, split
    import sys
    import zipfile

    # Add parent directory to beginning of path variable
    DIR = dirname(abspath(__file__))
    sys.path.insert(0, split(DIR)[0])

    import odtbrain as odt

    # use jobmanager if available
    try:
        import jobmanager as jm
        jm.decorators.decorate_module_ProgressBar(odt, 
                            decorator=jm.decorators.ProgressBarOverrideCount,
                            interval=.1)
    except:
        pass


    datazip = join(dirname(__file__), "fdtd_2d_sino_A100_R13.zip")
    # Get simulation data
    arc = zipfile.ZipFile(datazip)

    angles = np.loadtxt(arc.open("fdtd_angles.txt"))
    phantom = np.loadtxt(arc.open("fdtd_phantom.txt"))
    sino_real = np.loadtxt(arc.open("fdtd_real.txt"))
    sino_imag = np.loadtxt(arc.open("fdtd_imag.txt"))
    sino = sino_real +1j*sino_imag
    # get nm, lD, res
    with arc.open("fdtd_info.txt") as info:
        cfg = {}
        for l in info.readlines():
            if l.count("=") == 1:
                key, val = l.split("=")
                cfg[key.strip()] = float(val.strip())

    print("Example: Backpropagation from 2d FDTD simulations")
    print("Refractive index of medium:", cfg["nm"])
    print("Measurement position from object center:", cfg["lD"])
    print("Wavelength sampling:", cfg["res"])
    print("Performing backpropagation.")


    ## Apply the Rytov approximation
    sinoRytov = odt.sinogram_as_rytov(sino)


    ## perform backpropagation to obtain object function f
    f = odt.backpropagate_2d( uSin=sinoRytov,
                              angles=angles,
                              res=cfg["res"],
                              nm=cfg["nm"],
                              lD=cfg["lD"]*cfg["res"]
                              )


    ## compute refractive index n from object function
    n = odt.odt_to_ri(f, res=cfg["res"], nm=cfg["nm"])


    ## compare phantom and reconstruction in plot
    fig, axes = plt.subplots(1, 3, figsize=(12,4), dpi=300)
    
    axes[0].set_title("FDTD phantom")
    axes[0].imshow(phantom, vmin=phantom.min(), vmax=phantom.max())
    sino_phase = np.unwrap(np.angle(sino), axis=1)
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("y")
    
    axes[1].set_title("phase sinogram")    
    axes[1].imshow(sino_phase, vmin=sino_phase.min(), vmax=sino_phase.max(),
                   aspect=sino.shape[1]/sino.shape[0],
                   cmap=plt.cm.coolwarm)  # @UndefinedVariable
    axes[1].set_xlabel("detector")
    axes[1].set_ylabel("angle [rad]")

    axes[2].set_title("reconstructed image")
    axes[2].imshow(n.real, vmin=phantom.min(), vmax=phantom.max())
    axes[2].set_xlabel("x")    
    axes[2].set_ylabel("y")


    # set y ticks for sinogram
    labels = np.linspace(0, 2*np.pi, len(axes[1].get_yticks()))
    labels = [ "{:.2f}".format(i) for i in labels ]
    axes[1].set_yticks(np.linspace(0, len(angles), len(labels)))
    axes[1].set_yticklabels(labels)

    plt.tight_layout()
    plt.savefig(DIR+"/backprop_from_fdtd_2d.png")