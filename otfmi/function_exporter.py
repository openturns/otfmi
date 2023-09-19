from .mo2fmu import mo2fmu
import glob
import jinja2
import tempfile
import openturns as ot
import os
import re
import subprocess
import shutil
import sys
import dill

dill.settings["recurse"] = True


def path2uri(path):
    try:
        # python >=3.4, or using backport
        import pathlib

        return pathlib.Path(path).as_uri()
    except ImportError:
        return "file://" + path.replace("\\", "/").replace("C:/", "/C:/")


class FunctionExporter(object):
    """
    Fonction export.

    Parameters
    ----------
    function : :py:class:`openturns.Function`
        Function to export.
    start : sequence of float
        Initial input values.
    """

    def __init__(self, function, start=None):
        assert hasattr(function, "getInputDimension"), "not an openturns function"
        self.function_ = function
        if start is not None:
            try:
                [float(x) for x in start]
            except Exception:
                raise TypeError("start must be a sequence of float")
            assert len(start) == function.getInputDimension(), "wrong input dimension"
        self.start_ = start
        self.workdir = tempfile.mkdtemp()
        self._xml_path = os.path.join(self.workdir, "function.xml")

    def _export_xml(self):
        """
        Export the OpenTurns function as xml.

        Parameters
        ----------
        """
        study = ot.Study()
        study.setStorageManager(ot.XMLStorageManager(self._xml_path))
        study.add("function", self.function_)
        study.save()

    def _write_cwrapper_process(self):
        """
        Write the C wrapper.

        Parameters
        ----------
        """
        with open(self._xml_path, "rb") as f:
            xml_data = f.read()

        field = hasattr(self.function_, "getOutputMesh")
        flat_size = self.function_.getOutputDimension()
        if field:
            flat_size *= self.function_.getOutputMesh().getVerticesNumber()

        tdata = """
#define _XOPEN_SOURCE 500
#define  _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#ifdef _WIN32
#include <io.h>
#include <direct.h>
#define R_OK 4
#define access _access
#define mkdir(dir, mod) _mkdir(dir)
#else
#include <unistd.h>
#endif
unsigned char xml_data[] = { {{ xml_data_bin }} };
void c_func(int nin, double x[], int nout, double y[]) {
  FILE *fptr;
  int rc;
  int i;
  static int count = 0;
  static int hits = 0;
  static int findex = 0;
  int same_x;
  static double prev_x[{{ input_dim }}];
  static double prev_y[{{ flat_size }}];
  same_x = count;
  for (i = 0; i < nin; ++ i) {
    if(x[i] != prev_x[i]) same_x = 0;
  }
  if (!same_x) {
    /* reset the node index */
    findex = 0;
    /*printf("count=%d hits=%d\\n", count, hits);*/
    char workdir[] = "{{ workdir }}";
    if (access(workdir, R_OK) == -1)
      mkdir(workdir, 0733);
    fptr = fopen("{{ path_point_in }}", "w");
    for (i = 0; i < nin; ++ i)
      fprintf(fptr, "%lf\\n", x[i]);
    fclose(fptr);
    char xml_path[] = "{{ path_function_xml }}";
    if (access(xml_path, R_OK) == -1) {
      fptr = fopen(xml_path, "wb");
      fwrite (xml_data, sizeof(char), sizeof(xml_data), fptr);
      fclose(fptr);
    }
    char py_path[] = "{{ path_wrapper_py }}";
    if (access(py_path, R_OK) == -1) {
      fptr = fopen(py_path, "w");
      fprintf(fptr, "import openturns as ot\\n");
      fprintf(fptr, "study = ot.Study()\\n");
      fprintf(fptr, "study.setStorageManager(ot.XMLStorageManager(r\\\"%s\\\"))\\n", xml_path);
      fprintf(fptr, "study.load()\\n");
      fprintf(fptr, "function = ot.{{ function_type }}()\\n");
      fprintf(fptr, "study.fillObject(\\\"function\\\", function)\\n");
      fprintf(fptr, "x = []\\n");
      fprintf(fptr, "with open(r\\"{{ path_point_in }}\\", \\"r\\") as f:\\n");
      fprintf(fptr, "    for line in f.readlines():\\n");
      fprintf(fptr, "        x.append(float(line))\\n");
      fprintf(fptr, "y = function(x)\\n");
{% if field %}
      fprintf(fptr, "y = y.asPoint()\\n");
{% endif %}
      fprintf(fptr, "with open(r\\"{{ path_point_out }}\\", \\"w\\") as f:\\n");
      fprintf(fptr, "    for v in y:\\n");
      fprintf(fptr, "        f.write(str(v)+\\"\\\\n\\")\\n");
      fclose(fptr);
    }
    rc = system("python3 {{ path_wrapper_py }} > {{ path_error_log }} 2>&1");
    if (rc != 0)
      printf("otfmi: error running \\"python {{ path_wrapper_py }}\\" rc=%d\\n", rc);
    fptr = fopen("{{ path_point_out }}", "r");
    for (i = 0; i < {{ flat_size }}; ++ i)
      rc = fscanf(fptr, "%lf", &y[i]);
    fclose(fptr);

    memcpy(prev_x, x, nin * sizeof(double));
    memcpy(prev_y, y, {{ flat_size }} * sizeof(double));
  }
  else
    ++ hits;
    memcpy(y, prev_y + findex, nout * sizeof(double));
{% if field %}
  /* for the same x we must return at each call the value of the next node. TODO: interpolate wrt t? */
  findex = (findex + 1) % {{ n_pt }};
{% endif %}
  ++ count;
}

"""

        data = jinja2.Template(tdata).render(
            {
                "xml_data_bin": ",".join(
                    ["0x{:02x}".format(byte) for byte in xml_data]
                ),
                "input_dim": self.function_.getInputDimension(),
                "flat_size": flat_size,
                "workdir": self.workdir.replace("\\", "\\\\"),
                "field": field,
                "n_pt": self.function_.getOutputMesh().getVerticesNumber()
                if field
                else 0,
                "function_type": "PointToFieldFunction" if field else "Function",
                "path_point_in": os.path.join(self.workdir, "point.in").replace(
                    "\\", "\\\\"
                ),
                "path_point_out": os.path.join(self.workdir, "point.out").replace(
                    "\\", "\\\\"
                ),
                "path_wrapper_py": os.path.join(self.workdir, "wrapper.py").replace(
                    "\\", "\\\\"
                ),
                "path_error_log": os.path.join(self.workdir, "error.log").replace(
                    "\\", "\\\\"
                ),
                "path_function_xml": os.path.join(self.workdir, "function.xml").replace(
                    "\\", "\\\\"
                ),
            }
        )
        with open(os.path.join(self.workdir, "wrapper.c"), "w") as c:
            c.write(data)

        # write CMakeLists
        data = """
cmake_minimum_required (VERSION 3.13)
set (CMAKE_BUILD_TYPE "Release" CACHE STRING "build type")
project (wrapper C)
if (POLICY CMP0091)
  cmake_policy (SET CMP0091 NEW)
endif()
# openmodelica uses -Bstatic on Linux
add_library (cwrapper STATIC wrapper.c)
set_target_properties (cwrapper PROPERTIES POSITION_INDEPENDENT_CODE ON
                                           ARCHIVE_OUTPUT_DIRECTORY_RELEASE ${CMAKE_BINARY_DIR}
                                           LIBRARY_OUTPUT_DIRECTORY_RELEASE ${CMAKE_BINARY_DIR}
                                           RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_BINARY_DIR}
                                           MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
if (MSVC)
  target_compile_definitions(cwrapper PRIVATE _CRT_SECURE_NO_WARNINGS)
endif()
"""
        with open(os.path.join(self.workdir, "CMakeLists.txt"), "w") as cm:
            cm.write(data)

    def _write_cwrapper_capi(self):
        """
        Write the C wrapper with Python C API.

        Parameters
        ----------
        """
        with open(self._xml_path, "rb") as f:
            xml_data = f.read()

        field = hasattr(self.function_, "getOutputMesh")
        flat_size = self.function_.getOutputDimension()
        if field:
            flat_size *= self.function_.getOutputMesh().getVerticesNumber()

        tdata = """
#define _XOPEN_SOURCE 500
#define  _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#ifdef _WIN32
#include <io.h>
#include <direct.h>
#define R_OK 4
#define access _access
#define mkdir(dir, mod) _mkdir(dir)
#else
#include <unistd.h>
#endif
#include <Python.h>
unsigned char xml_data[] = { {{ xml_data_bin }} };

#ifdef _WIN32
__declspec(dllexport)
#endif
void c_func(int nin, double x[], int nout, double y[])
{
  FILE *fptr;
  static int count = 0;
  PyObject *pName = NULL;
  static PyObject *pFunc = NULL;
  PyObject *pX = NULL;
  PyObject *pY = NULL;
  PyObject *pValue = NULL;
  PyObject *pModule = NULL;
  int i;
  if (!pFunc)
  {
    char workdir[] = "{{ workdir }}";
    if (access(workdir, R_OK) == -1)
      mkdir(workdir, 0733);
    char xml_path[] = "{{ path_function_xml }}";
    if (access(xml_path, R_OK) == -1)
    {
      fptr = fopen(xml_path, "wb");
      fwrite (xml_data, sizeof(char), sizeof(xml_data), fptr);
      fclose(fptr);
    }
    char py_path[] = "{{ path_wrapper_py }}";
    if (access(py_path, R_OK) == -1) {
      fptr = fopen(py_path, "w");
      fprintf(fptr, "import openturns as ot\\n");
      fprintf(fptr, "study = ot.Study()\\n");
      fprintf(fptr, "xml_path = r\\\"%s\\\"\\n", xml_path);
      fprintf(fptr, "study.setStorageManager(ot.XMLStorageManager(xml_path))\\n");
      fprintf(fptr, "study.load()\\n");
      fprintf(fptr, "function = ot.{{ function_type }}()\\n");
      fprintf(fptr, "study.fillObject(\\\"function\\\", function)\\n");
      fprintf(fptr, "def wrap_evaluate_python(x):\\n");
      fprintf(fptr, "    y = function(list(x))\\n");
      //fprintf(fptr, "    print(x, y)\\n");
{% if field %}
      fprintf(fptr, "    y = y.asPoint()\\n");
{% endif %}
      fprintf(fptr, "    return y\\n");
      fclose(fptr);
    }
    Py_Initialize();
    if (PyErr_Occurred())
    {
       PyErr_Print();
       return;
    }
    pName = PyUnicode_FromString(py_path);
    if (PyErr_Occurred())
    {
       PyErr_Print();
       return;
    }
    PyObject* sys = PyImport_ImportModule("sys");
    PyObject* sys_path = PyObject_GetAttrString(sys, "path");
    PyObject* folder_path = PyUnicode_FromString(workdir);
    PyList_Append(sys_path, folder_path);
    PyObject* wrapper_name = PyUnicode_FromString("wrapper");
    pModule = PyImport_Import(wrapper_name);
    if (PyErr_Occurred())
    {
       PyErr_Print();
       return;
    }
    Py_DECREF(pName);

    pFunc = PyObject_GetAttrString(pModule, "wrap_evaluate_python");
    if (PyErr_Occurred())
    {
       PyErr_Print();
       return;
    }
  }

  //printf("-- pFunc=%x\\n", pFunc);
  if (pFunc)
  {
    pX = PyTuple_New(nin);
    for (i = 0; i < nin; ++i)
    {
      pValue = PyFloat_FromDouble(x[i]);
      PyTuple_SetItem(pX, i, pValue);
      //printf("-- x=%g\\n", x[i]); fflush(stdout);
    }
    pY = PyObject_CallOneArg(pFunc, pX);
    if (PyErr_Occurred())
    {
       PyErr_Print();
       return;
    }
    for (i = 0; i < nout; ++i)
    {
      // OT returns a Point
      pValue = PySequence_GetItem(pY, i);
      y[i] = PyFloat_AsDouble(pValue);
      Py_DECREF(pValue);
      //printf("-- y=%g\\n", y[i]); fflush(stdout);
    }
  }

  ++ count;
}
"""
        data = jinja2.Template(tdata).render(
            {
                "xml_data_bin": ",".join(
                    ["0x{:02x}".format(byte) for byte in xml_data]
                ),
                "input_dim": self.function_.getInputDimension(),
                "flat_size": flat_size,
                "workdir": self.workdir.replace("\\", "\\\\"),
                "field": field,
                "n_pt": self.function_.getOutputMesh().getVerticesNumber()
                if field
                else 0,
                "function_type": "PointToFieldFunction" if field else "Function",
                "path_point_in": os.path.join(self.workdir, "point.in").replace(
                    "\\", "\\\\"
                ),
                "path_point_out": os.path.join(self.workdir, "point.out").replace(
                    "\\", "\\\\"
                ),
                "path_wrapper_py": os.path.join(self.workdir, "wrapper.py").replace(
                    "\\", "\\\\"
                ),
                "path_error_log": os.path.join(self.workdir, "error.log").replace(
                    "\\", "\\\\"
                ),
                "path_function_xml": os.path.join(self.workdir, "function.xml").replace(
                    "\\", "\\\\"
                ),
            }
        )
        with open(os.path.join(self.workdir, "wrapper.c"), "w") as c:
            c.write(data)

        # write CMakeLists
        data = """
cmake_minimum_required (VERSION 3.13)
set (CMAKE_BUILD_TYPE "Release" CACHE STRING "build type")
project (wrapper C)
if (POLICY CMP0091)
  cmake_policy (SET CMP0091 NEW)
endif()

# link dynamically for Python
add_library (cwrapper SHARED wrapper.c)

find_package (Python 3.8 COMPONENTS Development REQUIRED)
target_link_libraries(cwrapper PRIVATE Python::Python)

set_target_properties (cwrapper PROPERTIES MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>"
                                           ARCHIVE_OUTPUT_DIRECTORY_RELEASE ${CMAKE_BINARY_DIR}
                                           LIBRARY_OUTPUT_DIRECTORY_RELEASE ${CMAKE_BINARY_DIR}
                                           RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_BINARY_DIR})
if (MSVC)
  target_compile_definitions(cwrapper PRIVATE _CRT_SECURE_NO_WARNINGS)
endif()
"""
        with open(os.path.join(self.workdir, "CMakeLists.txt"), "w") as cm:
            cm.write(data)

    def _build_cwrapper(self, verbose):
        """
        Build C wrapper.

        Requires CMake, a C compiler.

        Parameters
        ----------
        verbose : bool
            Verbose output (default=False).
        """
        cmake_args = ["cmake", "."]
        if sys.platform.startswith("win"):
            # bits = platform.architecture()[0]
            # vsplat = {"64bit": "x64", "32bit": "x86"}[bits]
            cmake_args.insert(1, "-DCMAKE_GENERATOR_PLATFORM=x64")
        subprocess.run(
            cmake_args, capture_output=not verbose, cwd=self.workdir, check=True
        )
        subprocess.run(
            ["cmake", "--build", ".", "--config", "Release"],
            capture_output=not verbose,
            cwd=self.workdir,
            check=True,
        )

    def _set_input_output(self):
        """
        Define the inputs and outputs in Modelica language..

        Parameters
        ----------
        """
        string = ""
        if self.start_ is None:
            for input_name in self.function_.getInputDescription():
                string = (
                    string + "  input Real " + re.sub(r"\W", "_", input_name) + " ;\n"
                )
        else:
            for (
                input_name,
                input_value,
            ) in zip(self.function_.getInputDescription(), self.start_):
                string = (
                    string
                    + "  input Real "
                    + re.sub(r"\W", "_", input_name)
                    + "(start="
                    + str(input_value)
                    + ");\n"
                )
        for output_name in self.function_.getOutputDescription():
            string = string + "  output Real " + re.sub(r"\W", "_", output_name) + ";\n"
        return string

    def _set_connector(self):
        """
        Define the inputs and outputs as OMEdit connectors.

        Parameters
        ----------
        """
        list_input_position = sorted(
            [
                (ii + 1) // 2 * 20 * (-1) ** ii
                for ii in range(len(self.function_.getInputDescription()))
            ],
            reverse=True,
        )
        list_output_position = sorted(
            [
                (ii + 1) // 2 * 20 * (-1) ** ii
                for ii in range(len(self.function_.getOutputDescription()))
            ],
            reverse=True,
        )

        string = ""
        for ii in range(len(self.function_.getInputDescription())):
            input_name = self.function_.getInputDescription()[ii]
            underscore_input_name = re.sub(r"\W", "_", input_name)
            y_origin = list_input_position[ii]
            string = (
                string
                + """  Modelica.Blocks.Interfaces.RealInput {}\n
                annotation(Placement(visible = true,\n
                transformation(origin={{-106, {}}}, extent={{{{-20, -20}}
                , {{20, 20}}}}),\n
                iconTransformation(origin={{-106, {}}}, extent={{{{-10,
                -10}}, {{10, 10}}}})));\n""".format(
                    underscore_input_name, y_origin, y_origin
                )
            )

        for ii in range(len(self.function_.getOutputDescription())):
            output_name = self.function_.getOutputDescription()[ii]
            underscore_output_name = re.sub(r"\W", "_", output_name)
            y_origin = list_output_position[ii]
            string = (
                string
                + """  Modelica.Blocks.Interfaces.RealOutput {}\n
                annotation(Placement(visible = true, transformation(
                origin={{106, {}}}, extent = {{{{-20, -20}}, {{20,
                20}}}}),\n
                iconTransformation(origin={{106, {}}}, extent={{{{-10,
                -10}}, {{10, 10}}}})));\n""".format(
                    underscore_output_name, y_origin, y_origin
                )
            )
        return string

    def _write_modelica_wrapper(self, className, dirName, gui, move):
        """
        Write the Modelica model importing Cfunction.

        Parameters
        ----------
        className : str
            The model prefix, used as name for the file and the model itself.
        dirName : str
            Name of the folder required by the user
        gui : bool
            If True, define the input/output connectors.
            The model cannot be exported as FMU in command line if gui=True.
        move : bool
            Move the model from temporary folder to user folder
        """
        link_dir = dirName if move else self.workdir
        _ = link_dir
        tdata = """
model {{ className }}

function ExternalFunc
input Real[{{ input_dim }}] x;
output Real[{{ output_dim }}] y;
external "C" c_func({{ input_dim }}, x, {{ output_dim }}, y);
annotation(Library="cwrapper", LibraryDirectory="{{ link_dir }}");
end ExternalFunc;

{{ io_vars }}

protected
  Real output_array_zzz__[{{ output_dim }}] = ExternalFunc({ {{ inputs }} });

equation
{%- for output in outputs %}
  {{ output }} = output_array_zzz__[{{ loop.index }}];
{%- endfor %}

end {{ className }};

"""
        data = jinja2.Template(tdata).render(
            {
                "className": className,
                "input_dim": self.function_.getInputDimension(),
                "output_dim": self.function_.getOutputDimension(),
                "link_dir": path2uri(dirName) if move else path2uri(self.workdir),
                "io_vars": self._set_connector() if gui else self._set_input_output(),
                "inputs": ", ".join(
                    [
                        re.sub(r"\W", "_", name)
                        for name in self.function_.getInputDescription()
                    ]
                ),
                "outputs": [
                    re.sub(r"\W", "_", name)
                    for name in self.function_.getOutputDescription()
                ],
            }
        )
        with open(os.path.join(self.workdir, className + ".mo"), "w") as mo:
            mo.write(data)

    def export_model(self, model_path, gui=False, verbose=False, binary=True, mode="process", move=True):
        """
        Export to model file (.mo).

        Requires CMake, a C compiler.

        Parameters
        ----------
        model_path : str
            Path to the generated .mo file.
            The model name is taken from the base name.
        gui : bool
            If True, define the input/output connectors.
                In this case, given start values ARE NOT TAKEN INTO ACCOUNT.
            If False, input and outputs are defined in Modelica code.
                In this case only, the model can be exported as FMU using OMC command line.
        verbose : bool
            Verbose output (default=False).
        binary : bool
            Whether to generate binaries or source (default=True)
        mode : 'process' or 'capi'
            Use either a Python process or the Python C API to evaluate the model.
        move : bool
            Move the model from temporary folder to user folder (default=True)
        """

        assert isinstance(model_path, str), "model_path must be str"
        rawClassName, extension = os.path.splitext(os.path.basename(model_path))
        className = rawClassName[0].upper() + rawClassName[1:]
        assert extension == ".mo", "Invalid model"
        dirName = os.path.expanduser(os.path.dirname(model_path))

        self._export_xml()
        if mode == "process":
            self._write_cwrapper_process()
        else:
            self._write_cwrapper_capi()
        if binary:
            self._build_cwrapper(verbose)
        self._write_modelica_wrapper(className, dirName, gui, move)

        if move:
            list_file = [className + extension]
            if binary:
                # licwrapper.a/.so, cwrapper.lib/dll
                list_file += glob.glob(os.path.join(self.workdir, "*cwrapper*"))
            else:
                list_file += ["wrapper.c", "CMakeLists.txt"]
            for file in list_file:
                src = os.path.join(self.workdir, file)
                dest = os.path.join(dirName, file)
                shutil.move(src, dest)
            shutil.rmtree(self.workdir)

    def export_fmu(self, fmu_path, fmuType="me", verbose=False):
        """
        Export the Modelica model as FMU.

        Requires CMake, a C compiler and omc the OpenModelica compiler.
        If the model does not already exist, or if the existing model uses
        OMEdit connectors, the model is (re)created.

        Parameters
        ----------
        fmu_path : str
            Path to the generated .fmu file.
        fmuType : str
            model type, either me (model exchange), cs (co-simulation),
            me_cs (both model exchange and co-simulation)
        verbose : bool
            Verbose output (default=False).
        """

        rawClassName, extension = os.path.splitext(os.path.basename(fmu_path))
        className = rawClassName[0].upper() + rawClassName[1:]
        # name starting with lower case causes connection issues in OMEdit
        assert extension == ".fmu", "Please give a FMU name as argument :)"
        dirName = os.path.expanduser(os.path.dirname(fmu_path))
        model_path = fmu_path.replace("fmu", "mo")
        if not os.path.exists(self.workdir):
            os.makedirs(self.workdir)
        self.export_model(model_path, gui=False, verbose=verbose, move=False)

        path_mo = os.path.join(self.workdir, className + ".mo")
        path_fmu = os.path.join(self.workdir, className + extension)
        mo2fmu(path_mo, path_fmu=path_fmu, fmuType=fmuType, verbose=verbose)

        shutil.move(
            os.path.join(self.workdir, className + extension),
            os.path.join(dirName, className + extension),
        )
        shutil.rmtree(self.workdir)
