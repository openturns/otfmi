import argparse
import jinja2
from pathlib import Path
import tempfile
import subprocess
import shutil
import sys


def mo2fmu(
    path_mo,
    path_fmu=None,
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
    path_mo : str or path-like
        Path to the source model file
    path_fmu : str or path-like, default=None
        Path to the destination FMU file
        If not provided write it in the current directory
    fmuType : str, default="cs"
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

    p_mo = Path(path_mo)
    assert p_mo.exists(), f"model file {path_mo} does not exist"
    # assume the model name is the file name
    model_name = p_mo.stem
    p_fmu = Path.cwd() / (model_name + ".fmu") if path_fmu is None else Path(path_fmu)
    if not isinstance(fmuType, str):
        raise TypeError("fmuType must be of type str")

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

    workdir = Path(tempfile.mkdtemp())
    path_mos = workdir / "mo2fmu.mos"
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
            "fileName": str(p_mo.resolve()).replace("\\", "\\\\"),
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
            cwd=workdir,
            check=True,
        )
        if verbose:
            print(cp.stdout.decode(), file=sys.stderr)
    except subprocess.CalledProcessError as cpe:
        print("Error occurred running the OpenModelica compiler omc:", cpe.stdout + cpe.stderr, file=sys.stderr)
        raise cpe
    temp_fmu = workdir / (model_name + ".fmu")
    assert temp_fmu.exists(), f"omc failed to generate the FMU file {temp_fmu}"
    shutil.move(temp_fmu, p_fmu)
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
