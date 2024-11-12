#!/bin/sh

set -xe

export SOURCE_DATE_EPOCH=1609455600
aurman -S python-sphinx-renku-theme python-sphinx_rtd_theme --noconfirm --noedit

cp -r /io/* /tmp
cd /tmp
pip install . --user --break-system-packages
~/.local/bin/mo2fmu -h
~/.local/bin/mo2fmu ./otfmi/example/file/deviation.mo ./otfmi/example/file/fmu/linux-x86_64/deviation.fmu
pythonfmu build --file ./otfmi/example/file/DeviationSlave.py --dest ./otfmi/example/file/fmu/linux-x86_64

pytest test -s
cd doc && make html BUILDDIR=~/.local/share/otfmi/doc

uid=$1
gid=$2
if test -n "${uid}" -a -n "${gid}"
then
  sudo cp -r ~/.local/share/*/doc/html /io
  sudo chown -R ${uid}:${gid} /io/html
fi
