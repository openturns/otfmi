#!/usr/bin/env python

import tempfile
import openturns as ot
import os
import subprocess
import shutil

class FunctionExporter(object):
    """Function to FMU export."""

    def __init__(self, function, name, start):
        """
        Parameters
        ----------
        function : :py:class:`openturns.Function`
            Function to export
        name : str
            FMI model name
        start : sequence of float
            Initial input values
        """

        self.function_ = function
        self.name_ = name
        assert len(start) == function.getInputDimension(), "wrong input dimension"
        self.start_ = start
        self.workdir_ = tempfile.mkdtemp()
        print('workdir=', self.workdir_)

    def export(self, fmu_path):
        """
        Export to FMU file.

        Parameters
        ----------
        fmu_path : str
            Path to the generated .fmu file
        """

        study = ot.Study()
        study.setStorageManager(ot.XMLStorageManager(os.path.join(self.workdir_, 'function.xml')))
        study.add('function', self.function_)
        study.save()

        with open(os.path.join(self.workdir_, self.name_ + '.mo'), 'w') as mo:
            mo.write('model '+self.name_+'\n\n')

            mo.write('function ExternalFunc1\n')
            for input_name in self.function_.getInputDescription():
                mo.write('  input Real '+input_name+';\n')
            for output_name in self.function_.getOutputDescription():
                mo.write('  output Real '+output_name + ';\n')
            mo.write('  external "C" '+output_name + ' = ext_ExternalFunc1('+', '.join([input_var for input_var in self.function_.getInputDescription()])+');\n')
            mo.write('  annotation(Library="'+self.name_+'", LibraryDirectory="file://'+self.workdir_+'");\n')
            mo.write('end ExternalFunc1;\n\n')

            for input_name, input_value,  in zip(self.function_.getInputDescription(), self.start_):
                mo.write('  input Real '+input_name + '(start='+str(input_value)+');\n')
            for output_name in self.function_.getOutputDescription():
                mo.write('  output Real '+output_name + ';\n')
            mo.write('equation\n')
            mo.write('  ' + self.function_.getOutputDescription()[0] + ' = ExternalFunc1('+ ', '.join(self.function_.getInputDescription())+');\n');
            #mo.write('  y=(F*L*L*L)/(3.0*E*I);\n');
            mo.write('end '+self.name_+';\n')

        with open(os.path.join(self.workdir_, self.name_ + '.c'), 'w') as c:
            c.write('#include <stdio.h>\n')
            c.write('#include <stdlib.h>\n')
            c.write('double ext_ExternalFunc1('+', '.join(['double ' + input_var for input_var in self.function_.getInputDescription()])+'){\n')
            for output_name in self.function_.getOutputDescription():
                c.write('  double '+output_name + ';\n')
            c.write('  FILE *fptr;\n')
            c.write('  int ret;\n')
            c.write('  fptr = fopen("'+os.path.join(self.workdir_, "point.in")+'", "w");\n')
            for input_name, input_value,  in zip(self.function_.getInputDescription(), self.start_):
              c.write('  fprintf(fptr,"%lf\\n", '+str(input_value)+');\n')
            c.write('  fclose(fptr);\n')
            c.write('  ret = system("python '+os.path.join(self.workdir_, "wrapper.py")+'");\n')
            c.write('  fptr = fopen("'+os.path.join(self.workdir_, "point.out")+'", "w");\n')
            for output_name in self.function_.getOutputDescription():
                c.write('  fscanf(fptr, "%lf", &'+output_name+');\n')
            c.write('  fclose(fptr);\n')
            c.write('  return '+self.function_.getOutputDescription()[0]+';}\n')

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
            py.write('print(x, y)\n')
            py.write('with open("'+os.path.join(self.workdir_, "point.out")+'", "w") as f:\n')
            py.write('    for v in y:\n')
            py.write('        f.write(str(v))\n')

        with open(os.path.join(self.workdir_, 'mo2fmu.mos'), 'w') as mos:
            mos.write('loadFile("'+self.name_ + '.mo"); getErrorString();\n')
            mos.write('translateModelFMU('+self.name_ + ', version="2.0", fmuType="cs"); getErrorString()\n')

        cc = os.environ.get('CC', 'gcc')
        cp = subprocess.run(' '.join([cc, '-c', '-o', self.name_ + '.o ', self.name_ + '.c']), cwd=self.workdir_, shell=True, check=True)
        ar = os.environ.get('AR', 'ar')
        cp = subprocess.run(' '.join([ar, 'rcs' , 'lib'+self.name_+'.a', self.name_ + '.o']), cwd=self.workdir_, shell=True, check=True)
        cp = subprocess.run('omc mo2fmu.mos', cwd=self.workdir_, shell=True, check=True)
        shutil.move(os.path.join(self.workdir_, self.name_ +".fmu"), fmu_path)

    def cleanup(self):
        """Cleanup files."""
        shutil.rmtree(self.workdir_)

