import tempfile
import openturns as ot
import os
import platform
import subprocess
import shutil
import sys

if sys.version_info < (3, 0):
    def subprocess_run(args, capture_output=False, shell=False, cwd=None, check=False):
        proc = subprocess.Popen(args, shell=shell, cwd=cwd)
        proc.communicate()
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
    """Function to FMU export."""

    def __init__(self, function, start):
        """
        Parameters
        ----------
        function : :py:class:`openturns.Function`
            Function to export.
        start : sequence of float
            Initial input values.
        """

        self.function_ = function
        assert len(start) == function.getInputDimension(), "wrong input dimension"
        self.start_ = start
        self.workdir_ = tempfile.mkdtemp()

    def export(self, fmu_path, verbose=False):
        """
        Export to FMU file.

        Requires CMake, a C compiler and omc the OpenModelica compiler.

        Parameters
        ----------
        fmu_path : str
            Path to the generated .fmu file.
        verbose : bool
            Verbose output (default=False).
        """

        # export the function to xml
        study = ot.Study()
        study.setStorageManager(ot.XMLStorageManager(os.path.join(self.workdir_, 'function.xml')))
        study.add('function', self.function_)
        study.save()

        # the Python wrapper called by the C wrapper
        with open(os.path.join(self.workdir_, 'wrapper.py'), 'w') as py:
            py.write('import openturns as ot\n')
            py.write('import os\n')
            py.write('x = []\n')
            py.write('with open("'+os.path.join(self.workdir_, "point.in")+'", "r") as f:\n')
            py.write('    for line in f.readlines():\n')
            py.write('        x.append(float(line))\n')
            py.write('study = ot.Study()\n')
            py.write('study.setStorageManager(ot.XMLStorageManager(os.path.join("'+self.workdir_+'", "function.xml")))\n')
            py.write('study.load()\n')
            py.write('function = ot.Function()\n')
            py.write('study.fillObject("function", function)\n')
            py.write('y = function(x)\n')
            #py.write('print(x, y)\n')
            py.write('with open("'+os.path.join(self.workdir_, "point.out")+'", "w") as f:\n')
            py.write('    for v in y:\n')
            py.write('        f.write(str(v))\n')

        # the C wrapper called by modelica
        with open(os.path.join(self.workdir_, 'wrapper.c'), 'w') as c:
            c.write('#include <stdio.h>\n')
            c.write('#include <stdlib.h>\n')
            c.write('#include <string.h>\n')
            c.write('void c_func(int nin, double x[], int nout, double y[])\n{\n')
            c.write('  FILE *fptr;\n')
            c.write('  int rc;\n')
            c.write('  int i;\n')
            c.write('  static int count = 0;\n')
            # FIXME: the internal function is called 1000 times with the same input, so we need a cache
            #c.write('  printf("count=%d\\n", count);\n')
            c.write('  int same_x;\n')
            c.write('  static double prev_x['+str(self.function_.getInputDimension())+'];\n')
            c.write('  static double prev_y['+str(self.function_.getOutputDimension())+'];\n')
            c.write('  same_x = count;\n')
            c.write('  for (i = 0; i < nin; ++ i) {\n')
            c.write('    if(x[i] != prev_x[i]) same_x = 0;\n  }\n')
            c.write('  if (same_x) {\n')
            c.write('    for(i = 0; i < nout; ++ i) y[i] = prev_y[i];\n')
            c.write('  } else {\n')
            c.write('    fptr = fopen("'+os.path.join(self.workdir_, "point.in").replace("\\", "\\\\")+'", "w");\n')
            c.write('    for (i = 0; i < nin; ++ i)\n')
            c.write('      fprintf(fptr, "%lf\\n", x[i]);\n')
            c.write('    memcpy(prev_x, x, nin * sizeof(double));\n')
            c.write('    fclose(fptr);\n')
            c.write('    rc = system("python '+os.path.join(self.workdir_, "wrapper.py").replace("\\", "\\\\")+'");\n')
            c.write('    fptr = fopen("'+os.path.join(self.workdir_, "point.out").replace("\\", "\\\\")+'", "r");\n')
            c.write('    for (i = 0; i < nout; ++ i)\n')
            c.write('      rc = fscanf(fptr, "%lf", &y[i]);\n')
            c.write('    memcpy(prev_y, y, nout * sizeof(double));\n')
            c.write('    fclose(fptr);\n  }\n')
            c.write('  ++ count;\n}\n')

        # build C wrapper
        with open(os.path.join(self.workdir_, 'CMakeLists.txt'), 'w') as cm:
            cm.write('cmake_minimum_required (VERSION 2.8)\n')
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
        subprocess.run(cmake_args, capture_output=not verbose, cwd=self.workdir_, check=True)
        subprocess.run(['cmake', '--build', '.', '--config', 'Release'], capture_output=not verbose, cwd=self.workdir_, check=True)

        # the modelica wrapper
        with open(os.path.join(self.workdir_, 'wrapper.mo'), 'w') as mo:
            mo.write('model wrapper\n\n')
            mo.write('function ExternalFunc\n')
            mo.write('  input Real['+str(self.function_.getInputDimension())+'] x;\n')
            mo.write('  output Real['+str(self.function_.getOutputDimension())+'] y;\n')
            mo.write('  external "C" c_func('+str(self.function_.getInputDimension())+', x, '+str(self.function_.getOutputDimension())+', y);\n')
            mo.write('  annotation(Library="cwrapper", LibraryDirectory="'+path2uri(self.workdir_)+'");\n')
            mo.write('end ExternalFunc;\n\n')
            for input_name, input_value,  in zip(self.function_.getInputDescription(), self.start_):
                mo.write('  input Real '+input_name + '(start='+str(input_value)+');\n')
            for output_name in self.function_.getOutputDescription():
                mo.write('  output Real '+output_name + ';\n')
            mo.write('protected\n')
            mo.write('  Real output_array_zzz__['+str(self.function_.getOutputDimension())+'] = ExternalFunc({'+', '.join(self.function_.getInputDescription())+'});\n');
            mo.write('equation\n')
            for output_name, i in zip(self.function_.getOutputDescription(), range(self.function_.getOutputDimension())):
                mo.write('  '+output_name+' = output_array_zzz__['+str(i)+'];\n')
            mo.write('end wrapper;\n')

        # export the fmu
        with open(os.path.join(self.workdir_, 'mo2fmu.mos'), 'w') as mos:
            mos.write('loadFile("wrapper.mo"); getErrorString();\n')
            mos.write('translateModelFMU(wrapper, fmuType="cs"); getErrorString()\n')
        subprocess.run(['omc', 'mo2fmu.mos'], capture_output=not verbose, cwd=self.workdir_, check=True)
        shutil.move(os.path.join(self.workdir_, "wrapper.fmu"), fmu_path)

    def cleanup(self):
        """Cleanup files."""
        shutil.rmtree(self.workdir_)

