#!/bin/sh

# Export a modelica model (.mo) file to FMU (.fmu)

set -e

usage()
{
  echo "Usage: ${0} source.mo [destination]"
  exit 1
}

test $# -ge 1 || usage

mofile=`readlink -f ${1}`

# assume the model name is the file name
modelname=`basename ${mofile} | cut -d '.' -f 1`

temp_dir=`mktemp -d` && cat > ${temp_dir}/mo2fmu.mos <<EOF
loadFile("${mofile}"); getErrorString();
translateModelFMU(${modelname}, version="2.0", fmuType="cs"); getErrorString();
EOF

# output file in current dir or parent of destination
if test $# -eq 2
then
  cd `dirname ${2}`
fi

omc ${temp_dir}/mo2fmu.mos


