import argparse
import jinja2
import os
import tempfile
import subprocess
import shutil
import sys


def mo2fmu(
    path_mo,
    path_fmu="",
    fmuType="cs",
    version="2.0",
    libs=[],
    platforms=["static"],
    verbose=False,
):
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
    version : str, default="2.0"
        fmi version
    libs : list of str, default=[]
        List of required libraries passed to loadModel
    platforms : list of str, default=[static]
        List of target platforms
    verbose : bool, default=False
        Verbose output
    """

    assert isinstance(path_mo, str), "path_mo must be str"
    assert isinstance(path_fmu, str), "path_fmu must be str"
    assert isinstance(fmuType, str), "fmuType must be str"
    try:
        [str(x) for x in libs]
    except Exception:
        raise TypeError("libs must be a sequence of str")
    try:
        [str(x) for x in platforms]
    except Exception:
        raise TypeError("platforms must be a sequence of str")

    # check omc can be run
    try:
        cp = subprocess.run(["omc", "--version"], check=True, capture_output=True)
        if verbose:
            print("omc version:", cp.stdout.decode(), file=sys.stderr)
    except subprocess.CalledProcessError as cpe:
        print("Error occured detecting the OpenModelica compiler omc:", cpe.stdout + cpe.stderr, file=sys.stderr)
        raise cpe

    workdir = tempfile.mkdtemp()
    path_mos = os.path.join(workdir, "mo2fmu.mos")
    # assume the model name is the file name
    model_name = os.path.splitext(os.path.basename(path_mo))[0]

    tdata = """
{%- for lib in libs %}
loadModel({{ lib }}); getErrorString();
{%- endfor %}

loadFile("{{ fileName }}"); getErrorString();
buildModelFMU({{ className }}, version="{{ version }}", fmuType="{{ fmuType }}", platforms={{ platforms }}); getErrorString();
"""

    data = jinja2.Template(tdata).render(
        {
            "libs": libs,
            "fileName": os.path.abspath(path_mo).replace("\\", "\\\\"),
            "className": model_name,
            "version": version,
            "fmuType": fmuType,
            "platforms": '{"' + '`",`"'.join([str(x) for x in platforms]) + '"}',
        }
    )

    with open(path_mos, "w") as mos:
        mos.write(data)
    if verbose:
        print(data, file=sys.stderr)
    try:
        cp = subprocess.run(
            ["omc", "mo2fmu.mos"],
            capture_output=True,
            shell=sys.platform.startswith("win"),
            cwd=workdir,
            check=True,
        )
        if verbose:
            print(cp.stdout.decode(), file=sys.stderr)
    except subprocess.CalledProcessError as cpe:
        print("Error occurred running the OpenModelica compiler omc:", cpe.stdout + cpe.stderr, file=sys.stderr)
        raise cpe
    temp_fmu = os.path.join(workdir, model_name) + ".fmu"
    if not os.path.exists(temp_fmu):
        raise RuntimeError(f"omc failed to generate the FMU file {temp_fmu}")
    if path_fmu == "":
        path_fmu = os.path.join(os.getcwd(), model_name) + ".fmu"
    shutil.move(temp_fmu, path_fmu)
    shutil.rmtree(workdir)


def main():
    """
    mo2fmu entry point.
    """
    parser = argparse.ArgumentParser(description="Export a model .mo to .fmu")
    parser.add_argument("path_mo", type=str, help="Path to the source model file")
    parser.add_argument(
        "path_fmu",
        nargs="?",
        type=str,
        help="Path to the destination FMU file",
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--fmuType",
        metavar="TYPE",
        type=str,
        help="model type me|cs|me_cs",
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--version",
        metavar="VERSION",
        type=str,
        help="fmi version 1.0|2.0",
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--libs",
        metavar="LIBS",
        type=str,
        action="extend",
        nargs="+",
        help="List of required libraries passed to loadModel",
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--platforms",
        metavar="PLATFORMS",
        type=str,
        action="extend",
        nargs="+",
        help="List of target platforms",
        default=argparse.SUPPRESS,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        const=True,
        dest="verbose",
        default=argparse.SUPPRESS,
    )
    args = parser.parse_args()
    mo2fmu(**vars(args))


if __name__ == "__main__":
    main()
