#!/bin/sh

# Export a modelica model (.mo) file to FMU (.fmu)

set -e

usage()
{
  echo "Usage: ${0} source.mo [destination.fmu]"
  exit 1
}

test $# -ge 1 || usage

mofile=`readlink -f ${1}`

# assume the model name is the file name
modelname=`basename ${mofile} | cut -d '.' -f 1`

if test $# -eq 2
then
  destination=`readlink -f ${2}`
else
  destination=${PWD}
fi

# export fmu in temp dir
temp_dir=`mktemp -d` && cd ${temp_dir} && cat > mo2fmu.mos <<EOF
loadFile("${mofile}"); getErrorString();
translateModelFMU(${modelname}, version="2.0", fmuType="cs"); getErrorString();
EOF
omc mo2fmu.mos

mv ${modelname}.fmu ${destination}

