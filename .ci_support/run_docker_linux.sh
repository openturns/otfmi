#!/bin/sh

set -xe

export SOURCE_DATE_EPOCH=1609455600
pip install -r /io/doc/requirements.txt --break-system-packages

cp -r /io/* /tmp
cd /tmp
pip install . --user --break-system-packages
~/.local/bin/mo2fmu -h
~/.local/bin/mo2fmu ./otfmi/example/file/deviation.mo ./otfmi/example/file/fmu/linux64/deviation.fmu
pytest test -s
cd doc && make html BUILDDIR=~/.local/share/otfmi/doc

uid=$1
gid=$2
if test -n "${uid}" -a -n "${gid}"
then
  sudo cp -r ~/.local/share/*/doc/html /io
  sudo chown -R ${uid}:${gid} /io/html
fi
