'''dnpTools
Collection of tools and functions useful to process DNP-NMR data
'''

import inspect
import numpy as np


from .mrProperties import gmrProperties
from .mrProperties import radicalProperties

def mrProperties(nucleus, *args):
    '''Return magnetic resonance property of specified isotope.
    This function is model after the Matlab function gmr written by Mirko Hrovat
    https://www.mathworks.com/matlabcentral/fileexchange/12078-gmr-m-nmr-mri-properties

    Reference: R.K.Harris et. al., Pure and Applied Chemistry, 2001, 73:1795-1818.
    Electron value comes from 1998 CODATA values, http://physics.nist.gov/cuu/Constants .
       or  http://physics.nist.gov/PhysRefData/codata86/codata86.html
       or  http://www.isis.rl.ac.uk/neutronSites/constants.htm
    Xenon gyromagnetic ratio was calculated from 27.661 MHz value from Bruker's web site.

    Args:

        nucleus: String defining the nucleus e.g. 1H, 13C, etc.

        args: If numerical value is given, it is interpreted as the B0 value in Tesla and Larmor frequency is returned. As string the following values are valid:

        gamma: Return Gyromagnetic Ration [radians/T/s]
        spin: Spin number of selected nucleus [1]
        qmom: Quadrupole moment [fm^2} (100 barns)
        natAbundance: Natural abundance [%]
        relSensitivity: Relative sensitiviy with respect to 1H at constant B0
        moment: Magnetic dipole moment in terms of the nuclear magneton, uN, |u|/uN = |gamma|*hbar[I(I + 1)]^1/2/uN , hbar=h/2pi.
        qlw: quadrupolar line-width factor as defined by: Qlw = Q^2(2I + 3)/[I^2(2I � 1)]

    Returns:

        .. code-block:: python

            dnp.dnpTools.mrProperties('1H')
            26.7522128                          # 1H Gyromagnetic Ratio (10^7r/Ts)

            dnp.dnpTools.mrProperties('1H', 0.35)
            14902114.17018196                   # 1H Larmor Frequency at 0.35 T (Hz)

            dnp.dnpTools.mrProperties('2H', 'qmom')
            0.286                               # Nuclear Quadrupole Moment (fm^2)

            value = dnp.dnpTools.mrProperties('6Li', 'natAbundance')
            7.59                                # Natural Abundance (%)

            value = dnp.dnpTools.mrProperties('6Li', 'relSensitivity')
            0.000645                            # Relative sensitivity


    '''

    if isinstance(nucleus, str):
        if nucleus in gmrProperties:
            gmr = gmrProperties.get(nucleus)[1]
        else:
            print("Isotope doesn't exist in list")
            return
    else:            
        print("ERROR: String expected")            

    if len(args) == 0:
        return gmr

    elif len(args) == 1:

        if isinstance(args[0], str):
            if args[0] == 'gamma':
                return gmrProperties.get(nucleus)[1]

            if args[0] == 'spin':
                return gmrProperties.get(nucleus)[0]

            elif args[0] == 'qmom':
                return gmrProperties.get(nucleus)[2]

            elif args[0] == 'natAbundance':
                return gmrProperties.get(nucleus)[3]

            elif args[0] == 'relSensitivity':
                return gmrProperties.get(nucleus)[4]

            elif args[0] == 'moment':
                return gmrProperties.get(nucleus)[5]

            elif args[0] == 'qlw':
                return gmrProperties.get(nucleus)[6]

            else:
                print("Keyword not recognize")

        else:
            vLarmor = args[0] * gmr * 1e7 / 2 / np.pi
            return vLarmor

    elif len(args) == 2:

        if args[1] == True:
            print(" ")
            print("Nucleus                    : ", nucleus)
            print("Spin                       : ", gmrProperties.get(nucleus)[0])
            print("Gyromagnetic Ratio [kHz/T] : %5.2f" %(gmrProperties.get(nucleus)[1]*10/2/np.pi))
            print("Natural Abundance      [%%] : %5.2f" %(gmrProperties.get(nucleus)[3] ) )
            print("")

    elif len(args) > 2:
        print("Too many input arguments")


def getRadicalProperties(name):
    '''Return properties of different radicals

    Args:

    Returns:

    '''

    if isinstance(name, str):
        if name in radicalProperties:
            giso = radicalProperties.get(name)[0]
        else:
            print("Radical doesn't exist in list")
            return
    else:            
        print("ERROR: String expected")            
    
    return giso

def getDnpProperties(radical,mwFrequency,dnpNucleus):
    '''Calculate DNP Properties
    Only for liquid state currently
    Only S = 0.5 currently

    Args:
        Type of radical
        mwFreguency
        Type of nucleus for DNP
    Returns:

    '''


    # http://physics.nist.gov/constants
    mub = 9.27400968e-24
    planck = 6.62606957e-34

    # Get radical properties
    glist = radicalProperties.get(radical)[0]
    nucleus = radicalProperties.get(radical)[1]
    Alist = radicalProperties.get(radical)[2]

    # Get g-value
    g = np.array(glist)
    giso = np.sum(g)/g.size

    B0 = mwFrequency*planck/giso/mub

    # Get hyperfine coupling
    A = np.array(Alist)
    Aiso = np.sum(A)/A.size

    if nucleus != None:
        print("Do nothing for now")
        nucSpin = mrProperties(nucleus,'spin')




    else:
        nucSpin = 0
        B = B0

     



    print("")
    print("Input Parameters: ")
    print("Radical                  : ", radical)
    print("giso                     : ", giso)
    print("Nucleus                  : ", nucleus)
    print("Nuc Spin                 : ", nucSpin)
    print("Aiso               [MHz] : ", Aiso)
    print("")
    print("Predicted Field Values for DNP: ")
    print("B0 (no hyperfine)    [T] : ", B0)

