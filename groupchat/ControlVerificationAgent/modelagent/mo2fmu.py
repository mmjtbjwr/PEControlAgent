import platform
import sys
import os
from pathlib import Path, PurePosixPath
import shutil
from pyvirtualdisplay.smartdisplay import SmartDisplay as Xvfb
import click
import spdlog as spd

def mo2fmu(mo, outdir, fmumodelname, load, type, version, dymola, dymolapath, dymolaegg, verbose, force):
    """
    mo2fmu converts a .mo file into a .fmu

    mo2fmu -v foo.mo .
    """
    logger = spd.ConsoleLogger('Logger', False, True, True)
    has_dymola=False
    # Changement du PYTHONPATH
    try:
        sys.path.append(str(Path(dymola) / Path(dymolaegg)))
        logger.info("add {} to sys path".format(Path(dymola) / Path(dymolaegg)))
        if not (Path(dymola) / Path(dymolaegg)).is_file():
            logger.error("dymola egg {} does not exist".format(
                Path(dymola) / Path(dymolaegg)))
        import dymola
        from dymola.dymola_interface import DymolaInterface
        from dymola.dymola_exception import DymolaException
        has_dymola = True
        logger.info("dymola is available in {}/{}".format(
            dymola, dymolaegg) )
    except ImportError as e:
        logger.info(
            "dymola module is not available, has_dymola: {}".format(has_dymola))
        pass  # module doesn't exist, deal with it.
    if not has_dymola:
        logger.error("dymola is not available, mo2fmu failed")
        return False

    dymola = None
    try:
        fmumodelname = Path(fmumodelname if fmumodelname else mo).stem
        if verbose:
            logger.info("convert {} to {}.fmu".format(mo, fmumodelname))

        if (Path(outdir)/Path(fmumodelname+'.fmu')).is_file() and force:
            logger.warn(
                "{}.fmu exists, dymola will overwrite it".format(Path(outdir)/fmumodelname))
        elif (Path(outdir)/Path(fmumodelname+'.fmu')).is_file():
            logger.warn(
                "{}.fmu exists, dymola will not overwrite it, use `--force` or `-f` to overwrite it.".format(Path(outdir)/fmumodelname))
            return False

        # Instantiate the Dymola interface and start Dymola
        dymola = DymolaInterface(dymolapath=dymolapath, showwindow=False)
        dymola.ExecuteCommand("Advanced.EnableCodeExport = false;")
        dymola.ExecuteCommand("Advanced.CompileWith64=2;")
        if load:
            for package in load:
                if verbose:
                    logger.info("load modelica package {}".format(package))
                dymola.openModel(package, changeDirectory=False)
        dymola.openModel(mo, changeDirectory=False)
        result = dymola.translateModelFMU(
            Path(mo).stem, modelName=fmumodelname, fmiType=type)
        print("result:", result)
        if not result:
            log = dymola.getLastErrorLog()
            logger.error("Simulation failed. Below is the translation log.")
            logger.info(log)
            return False
        if verbose:
            logger.info("{} file successfully generated".format(fmumodelname))
        fmu_path = Path(outdir) / Path(fmumodelname + '.fmu')
        assert(fmu_path.is_file())
        return str(fmu_path)
    except DymolaException as ex:
        logger.error(str(ex))
        return False
    finally:
        if dymola is not None:
            dymola.close()
            dymola = None