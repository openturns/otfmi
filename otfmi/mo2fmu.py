import argparse
import os
import tempfile
import subprocess
import shutil
import sys

def mo2fmu(path_mo, path_fmu='', fmuType="cs", libs=[], verbose=False):
    """
    Export a model .mo to .fmu.
    
    Parameters
    ----------
    path_mo : str
        Path to the source model file
    path_fmu : str, default=None
        Path to the destination FMU file
        If not provided write it in the current directory
    fmuType : str
        model type, either me (model exchange), cs (co-simulation),
        me_cs (both model exchange and co-simulation)
    libs : list of str, default=[]
        List of required libraries passed to loadModel
    verbose : bool, default=False
        Verbose output
    """

    assert isinstance(path_mo, str), 'path_mo must be str'
    assert isinstance(path_fmu, str), 'path_fmu must be str'
    assert isinstance(fmuType, str), 'fmuType must be str'
    try:
        [str(x) for x in libs]
    except Exception:
        raise TypeError('libs must be a sequence of str')

    workdir = tempfile.mkdtemp()
    path_mos = os.path.join(workdir, 'mo2fmu.mos')
    # assume the model name is the file name
    model_name = os.path.splitext(os.path.basename(path_mo))[0]
    with open(path_mos, 'w') as mos:
        for lib in libs:
             mos.write('loadModel('+lib+'); getErrorString();\n')
        mos.write('loadFile("' + os.path.abspath(path_mo).replace("\\", "\\\\") + '"); getErrorString();\n')
        mos.write('translateModelFMU(' + model_name + ', version="2.0", fmuType="' + fmuType + '"); getErrorString();\n')
    if verbose:
        with open(path_mos) as mos:
            print(mos.read())
    subprocess.run(['omc', 'mo2fmu.mos'], capture_output=not verbose, shell=sys.platform.startswith('win'), cwd=workdir, check=True)
    temp_fmu = os.path.join(workdir, model_name) + '.fmu'
    if path_fmu == '':
        path_fmu = os.path.join(os.getcwd(), model_name) + '.fmu'
    shutil.move(temp_fmu, path_fmu)
    shutil.rmtree(workdir)


def main():
    """
    mo2fmu entry point.
    """
    parser = argparse.ArgumentParser(description='Export a model .mo to .fmu')
    parser.add_argument('path_mo', type=str, help='Path to the source model file')
    parser.add_argument('path_fmu', nargs='?', type=str, help='Path to the destination FMU file', default=argparse.SUPPRESS)
    parser.add_argument('--fmuType', metavar='TYPE', type=str, help='model type me|cs|me_cs', default=argparse.SUPPRESS)
    parser.add_argument('--libs', metavar='LIBS', type=str, action="extend", nargs="+", help='List of required libraries passed to loadModel', default=argparse.SUPPRESS)
    parser.add_argument('-v', '--verbose', action='store_const', const=True, dest='verbose', default=argparse.SUPPRESS)
    args = parser.parse_args()
    mo2fmu(**vars(args))


if __name__ == '__main__':
    main()
