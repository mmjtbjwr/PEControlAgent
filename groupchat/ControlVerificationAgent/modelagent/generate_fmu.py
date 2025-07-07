#!/usr/bin/env python3
from mo2fmu import mo2fmu

if __name__ == '__main__':
 #   mo2fmu("ode_exp.mo", ".", "ode_exp", None, None, None, "/opt/dymola-2021-x86_64/", "/usr/local/bin/dymola-2021-x86_64", "Modelica/Library/python_interface/dymola.egg", True, False)
    mo2fmu(
        mo='boost_converter.mo',
        outdir='H://code_dev//PIDEvaluateAgent//fmu',
        fmumodelname='boost_converter',
        load=None,
        type='cs',
        version=None,
        dymola='D://Program Files//Dymola 2023x//bin64//',
        dymolapath='D://Program Files//Dymola 2023x//bin64//dymola.exe',
        dymolaegg='D://Program Files//Dymola 2023x//Modelica//Library//python_interface//dymola.egg',
        verbose=True,
        force=True
    )