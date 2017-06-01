#!/bin/sh

# rebuild fmu for a specific openmodelica version on a specific distro

set -e

usage()
{
  echo "Usage: ${0} model.mo [model.fmu]"
  exit 1
}

test $# -ge 1 || usage

mofile=`readlink -f ${1}`

# assume the model name is the file name
modelname=`basename ${mofile} | cut -d '.' -f 1`

if test $# -eq 2
then
  fmufile=`readlink -f ${2}`
else
  fmufile=`echo ${mofile} | cut -d '.' -f 1`.fmu
fi

temp_dir=`mktemp -d`

cd ${temp_dir}

cat > mo2fmu.mos <<EOF
loadFile("${mofile}");
getErrorString();
translateModelFMU(deviation, version="2.0", fmuType="cs");
getErrorString();
EOF

omc mo2fmu.mos

cp -v ${modelname}.fmu ${fmufile}
