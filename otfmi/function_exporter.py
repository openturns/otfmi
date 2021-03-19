import tempfile
import openturns as ot
import os
import platform
import re
import subprocess
import shutil
import sys
import dill
dill.settings['recurse'] = True

# py<37 has no capture_output keyword (py<3 has no subprocess.run at all)
if sys.version_info < (3, 7):
    def subprocess_run(args, capture_output=False, shell=False, cwd=None, check=False):
        stdout = subprocess.PIPE if capture_output else None
        proc = subprocess.Popen(args, shell=shell, cwd=cwd)
        outs, errs = proc.communicate()
        rc = proc.poll()
        if check and rc != 0:
            raise RuntimeError('process exited with code '+str(rc))
        return (rc == 0)

    subprocess.run = subprocess_run

def path2uri(path):
    try:
        # python >=3.4, or using backport
        import pathlib
        return pathlib.Path(path).as_uri()
    except ImportError:
        return 'file://'+path.replace('\\', '/').replace('C:/', '/C:/')


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
        assert hasattr(function, 'getInputDimension'), 'not an openturns function'
        self.function_ = function
        if start is not None:
            try:
                [float(x) for x in start]
            except Exception:
                raise TypeError('start must be a sequence of float')
            assert len(start) == function.getInputDimension(), 'wrong input dimension'
        self.start_ = start
        self.workdir = tempfile.mkdtemp()
        self._xml_path = os.path.join(self.workdir, 'function.xml')

    def _export_xml(self):
        """
        Export the OpenTurns function as xml.

        Parameters
        ----------
        """
        study = ot.Study()
        study.setStorageManager(ot.XMLStorageManager(self._xml_path))
        study.add('function', self.function_)
        study.save()

    def _write_cwrapper(self):
        """
        Write the C wrapper.

        Parameters
        ----------
        """
        with open(self._xml_path, 'rb') as f:
            xml_data = f.read()

        field = hasattr(self.function_, 'getOutputMesh')
        flat_size = self.function_.getOutputDimension()
        if field:
            n_pt = self.function_.getOutputMesh().getVerticesNumber()
            flat_size *= n_pt

        with open(os.path.join(self.workdir, 'wrapper.c'), 'w') as c:
            c.write('#define _XOPEN_SOURCE 500\n')
            c.write('#define  _POSIX_C_SOURCE 200809L\n')
            c.write('#include <stdio.h>\n')
            c.write('#include <stdlib.h>\n')
            c.write('#include <string.h>\n')
            c.write('#include <sys/stat.h>\n')
            c.write('#ifdef _WIN32\n#include <io.h>\n#include <direct.h>\n#define R_OK 4\n#define access _access\n#else\n#include <unistd.h>\n#endif\n')
            c.write('unsigned char xml_data[] = { ' + ','.join(['0x{:02x}'.format(byte) for byte in xml_data]) + '};\n')
            c.write('void c_func(int nin, double x[], int nout, double y[])\n{\n')
            c.write('  FILE *fptr;\n')
            c.write('  int rc;\n')
            c.write('  int i;\n')
            c.write('  static int count = 0;\n')
            c.write('  static int hits = 0;\n')
            if field:
                c.write('  static int findex = 0;\n')
            #c.write('  printf("count=%d hits=%d\\n", count, hits);\n')
            c.write('  int same_x;\n')
            c.write('  static double prev_x['+str(self.function_.getInputDimension())+'];\n')
            c.write('  static double prev_y['+str(flat_size)+'];\n')
            c.write('  same_x = count;\n')
            c.write('  for (i = 0; i < nin; ++ i) {\n')
            c.write('    if(x[i] != prev_x[i]) same_x = 0;\n  }\n')
            c.write('  if (!same_x) {\n')
            if field:
                c.write('    findex = 0;\n')
            c.write('    memcpy(prev_x, x, nin * sizeof(double));\n')
            c.write('    char workdir[] = "' + self.workdir.replace("\\", "\\\\") + '";\n')
            c.write('    if (access(workdir, R_OK) == -1)\n#ifdef _WIN32\n      _mkdir(workdir);\n#else\n      mkdir(workdir, 0733);\n#endif\n')
            c.write('    fptr = fopen("'+os.path.join(self.workdir, "point.in").replace("\\", "\\\\")+'", "w");\n')
            c.write('    for (i = 0; i < nin; ++ i)\n')
            c.write('      fprintf(fptr, "%lf\\n", x[i]);\n')
            c.write('    fclose(fptr);\n')
            c.write('    char xml_path[] = "'+os.path.join(self.workdir, 'function.xml').replace("\\", "\\\\")+'";\n')
            c.write('    if (access(xml_path, R_OK) == -1) {\n')
            c.write('      fptr = fopen(xml_path, "wb");\n')
            c.write('      fwrite (xml_data, sizeof(char), sizeof(xml_data), fptr);\n')
            c.write('      fclose(fptr); }\n')
            c.write('    char py_path[] = "'+os.path.join(self.workdir, 'wrapper.py').replace("\\", "\\\\")+'";\n')
            c.write('    if (access(py_path, R_OK) == -1) {\n')
            c.write('      fptr = fopen(py_path, "w");\n')
            c.write('      fprintf(fptr, "import openturns as ot\\nstudy = ot.Study()\\n");\n')
            c.write('      fprintf(fptr, "study.setStorageManager(ot.XMLStorageManager(\\\"%s\\\"))\\n", xml_path);\n')
            c.write('      fprintf(fptr, "study.load()\\n");\n')
            if field:
                c.write('      fprintf(fptr, "function = ot.PointToFieldFunction()\\n");\n')
            else:
                c.write('      fprintf(fptr, "function = ot.Function()\\n");\n')
            c.write('      fprintf(fptr, "study.fillObject(\\\"function\\\", function)\\n");\n')
            c.write('      fprintf(fptr, "x = []\\n");\n')
            c.write('      fprintf(fptr, "with open(\\"'+os.path.join(self.workdir, "point.in").replace("\\", "\\\\")+'\\", \\"r\\") as f:\\n");\n')
            c.write('      fprintf(fptr, "    for line in f.readlines():\\n");\n')
            c.write('      fprintf(fptr, "        x.append(float(line))\\n");\n')
            c.write('      fprintf(fptr, "y = function(x)\\n");\n')
            if field:
                c.write('      fprintf(fptr, "y = y.asPoint()\\n");\n')
            c.write('      fprintf(fptr, "with open(\\"'+os.path.join(self.workdir, 'point.out').replace("\\", "\\\\")+'\\", \\"w\\") as f:\\n");\n')
            c.write('      fprintf(fptr, "    for v in y:\\n");\n')
            c.write('      fprintf(fptr, "        f.write(str(v)+\\"\\\\n\\")\\n");\n')
            c.write('      fclose(fptr); };\n')
            c.write('    rc = system("python '+os.path.join(self.workdir, 'wrapper.py').replace("\\", "\\\\")+'> '+os.path.join(self.workdir, 'error.log').replace("\\", "\\\\")+' 2>&1");\n')
            c.write('    if (rc != 0) printf("otfmi: error running \\"python '+os.path.join(self.workdir, 'wrapper.py').replace("\\", "\\\\")+ '\\" rc=%d\\n", rc);\n')
            c.write('    fptr = fopen("'+os.path.join(self.workdir, 'point.out').replace("\\", "\\\\")+'", "r");\n')
            c.write('    for (i = 0; i < ' + str(flat_size) + '; ++ i)\n')
            c.write('      rc = fscanf(fptr, "%lf", &prev_y[i]);\n')
            c.write('    fclose(fptr);\n')
            c.write('  }\n')
            c.write('  else ++ hits;\n')
            if field:
                c.write('  for (i = 0; i < nout; ++ i) y[i] = prev_y[i + (findex % ' + str(n_pt) + ')];\n')
                c.write('  ++ findex;\n')
            else:
                c.write('  for (i = 0; i < nout; ++ i) y[i] = prev_y[i];\n')
            c.write('  ++ count;\n}\n')

    def _build_cwrapper(self, verbose):
        """
        Build C wrapper.

        Requires CMake, a C compiler.

        Parameters
        ----------
        verbose : bool
            Verbose output (default=False).
        """
        with open(os.path.join(self.workdir, 'CMakeLists.txt'), 'w') as cm:
            cm.write('cmake_minimum_required (VERSION 3.2)\n')
            cm.write('set (CMAKE_BUILD_TYPE "Release" CACHE STRING "build type")\n')
            cm.write('project (wrapper C)\n')
            cm.write('if (POLICY CMP0091)\n  cmake_policy (SET CMP0091 NEW)\nendif()\n')
            # openmodelica uses -Bstatic on Linux
            cm.write('add_library (cwrapper STATIC wrapper.c)\n')
            cm.write('set_target_properties (cwrapper PROPERTIES POSITION_INDEPENDENT_CODE ON MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")\n')
            cm.write('set_target_properties (cwrapper PROPERTIES ARCHIVE_OUTPUT_DIRECTORY_RELEASE ${CMAKE_BINARY_DIR} LIBRARY_OUTPUT_DIRECTORY_RELEASE ${CMAKE_BINARY_DIR} RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_BINARY_DIR})\n')
            cm.write('if (MSVC)\n  target_compile_definitions(cwrapper PRIVATE _CRT_SECURE_NO_WARNINGS)\nendif()\n')
        cmake_args=['cmake', '.']
        if sys.platform.startswith('win') and platform.architecture()[0] == '64bit':
            cmake_args.insert(1, '-DCMAKE_GENERATOR_PLATFORM=x64')
        subprocess.run(cmake_args, capture_output=not verbose, cwd=self.workdir, check=True)
        subprocess.run(['cmake', '--build', '.', '--config', 'Release'], capture_output=not verbose, cwd=self.workdir, check=True)

    def _set_input_output(self):
        """
        Define the inputs and outputs in Modelica language..

        Parameters
        ----------
        """
        string = ""
        if self.start_ is None:
            for input_name in self.function_.getInputDescription():
                string = string + '  input Real ' + re.sub(
                    r'\W', '_', input_name) + ' ;\n'
        else:
            for input_name, input_value,  in zip(
                    self.function_.getInputDescription(), self.start_):
                string = string + '  input Real ' + re.sub(r'\W', '_',
                    input_name) + '(start='+ str(input_value) + ');\n'
        for output_name in self.function_.getOutputDescription():
            string = string + '  output Real ' + re.sub(r'\W', '_',
                output_name) + ';\n'
        return string


    def _set_connector(self):
        """
        Define the inputs and outputs as OMEdit connectors.

        Parameters
        ----------
        """
        list_input_position = sorted(
                [(ii + 1) // 2 * 20 * (-1)**ii for ii in range(len(
                    self.function_.getInputDescription()))], reverse=True)
        list_output_position = sorted(
            [(ii + 1) // 2 * 20 * (-1)**ii for ii in range(len(
                self.function_.getOutputDescription()))], reverse=True)

        string = ""
        for ii in range(len(self.function_.getInputDescription())):
            input_name = self.function_.getInputDescription()[ii]
            underscore_input_name = re.sub(r'\W', '_', input_name)
            y_origin = list_input_position[ii]
            string = string + """  Modelica.Blocks.Interfaces.RealInput {}\n   
                annotation(Placement(visible = true,\n
                transformation(origin={{-106, {}}}, extent={{{{-20, -20}}
                , {{20, 20}}}}),\n
                iconTransformation(origin={{-106, {}}}, extent={{{{-10,
                -10}}, {{10, 10}}}})));\n""".format(
                    underscore_input_name, y_origin, y_origin)

        for ii in range(len(self.function_.getOutputDescription())):
            output_name = self.function_.getOutputDescription()[ii]
            underscore_output_name = re.sub(r'\W', '_', output_name)
            y_origin = list_output_position[ii]
            string = string + """  Modelica.Blocks.Interfaces.RealOutput {}\n
                annotation(Placement(visible = true, transformation(
                origin={{106, {}}}, extent = {{{{-20, -20}}, {{20,
                20}}}}),\n
                iconTransformation(origin={{106, {}}}, extent={{{{-10,
                -10}}, {{10, 10}}}})));\n""".format(
                    underscore_output_name, y_origin, y_origin)
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
        """
        with open(os.path.join(
                self.workdir, '{}.mo'.format(className)), 'w') as mo:
            mo.write('model '+ className + '\n\n')
            mo.write('function ExternalFunc\n')
            mo.write('  input Real['+str(self.function_.getInputDimension())+'] x;\n')
            mo.write('  output Real['+str(self.function_.getOutputDimension())+'] y;\n')
            mo.write('  external "C" c_func('+str(self.function_.getInputDimension())+', x, '+str(self.function_.getOutputDimension())+', y);\n')
            if move:
                mo.write('  annotation(Library="cwrapper",                LibraryDirectory="' + path2uri(dirName)+'");\n')
            else:
                mo.write('  annotation(Library="cwrapper",                   LibraryDirectory="' + path2uri(self.workdir)+'");\n')
            mo.write('end ExternalFunc;\n\n')

            if gui:
                mo.write(self._set_connector())
            else:
                mo.write(self._set_input_output())

            mo.write('protected\n')
            mo.write('  Real output_array_zzz__['+str
                (self.function_.getOutputDimension())+'] = ExternalFunc({'
                +', '.join([re.sub(r'\W', '_', name) for name in
                    self.function_.getInputDescription()])+'});\n');
            mo.write('equation\n')
            for output_name, i in zip(self.function_.getOutputDescription(), range(self.function_.getOutputDimension())):
                mo.write('  ' + re.sub(r'\W', '_', output_name) + ' = output_array_zzz__[' + str(i + 1) + '];\n')
            mo.write('end '+ className + ';\n')

    def export_model(self, model_path, gui=False, verbose=False,
            move=True):
        """
        Export to model file.

        Requires CMake, a C compiler.

        Parameters
        ----------
        model_path : str
            Path to the generated .model file.
            The model name is taken from the base name.
        gui : bool
            If True, define the input/output connectors. 
                In this case, given start values ARE NOT TAKEN INTO ACCOUNT.
            If False, input and outputs are defined in Modelica code.
                In this case only, the model can be exported as FMU using OMC command line. 
        verbose : bool
            Verbose output (default=False).
        move : bool
            Move the model from temporary folder to user folder (default=True)
        """

        assert isinstance(model_path, str), 'model_path must be str'
        rawClassName, extension = os.path.splitext(
            os.path.basename(model_path))
        className = rawClassName[0].upper() + rawClassName[1:]
        assert extension=='.mo', 'Invalid model'
        dirName = os.path.expanduser(os.path.dirname(model_path))

        self._export_xml()
        self._write_cwrapper()
        self._build_cwrapper(verbose)
        self._write_modelica_wrapper(className, dirName, gui, move)
        
        if move:
            list_file = [
                "function.xml", "libcwrapper.a", "wrapper.c",
                className + extension]
            for file in list_file:
                shutil.move(os.path.join(self.workdir, file),
                            os.path.join(dirName, file))
            shutil.rmtree(self.workdir)

    def export_fmu(self, fmu_path, fmuType='me', verbose=False):
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
            model type, either me (model exchange), cs (co-simulation), me_cs (both model exchange and co-simulation)
        verbose : bool
            Verbose output (default=False).
        """

        rawClassName, extension = os.path.splitext(os.path.basename(fmu_path))
        className = rawClassName[0].upper() + rawClassName[1:]
        # name starting with lower case causes connection issues in OMEdit
        assert extension=='.fmu', 'Please give a FMU name as argument :)'
        dirName = os.path.expanduser(os.path.dirname(fmu_path))
        model_path = fmu_path.replace("fmu", "mo")
        if not os.path.exists(self.workdir):
            os.makedirs(self.workdir)
        self.export_model(model_path, gui=False, verbose=verbose, move=False)

        with open(os.path.join(self.workdir, 'mo2fmu.mos'), 'w') as mos:
            mos.write(
                'loadFile("{}.mo"); getErrorString();\n'.format(className))
            mos.write('translateModelFMU(' + className + ', fmuType="' + fmuType + '"); getErrorString()\n')
        subprocess.run(['omc', 'mo2fmu.mos'], capture_output=not verbose, cwd=self.workdir, check=True)
        
        shutil.move(
            os.path.join(self.workdir, className + extension),
            os.path.join(dirName, className + extension))
        shutil.rmtree(self.workdir)
