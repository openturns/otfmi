#!/bin/sh

set -xe

export SOURCE_DATE_EPOCH=1761951600
#aurman -S python-sphinx-renku-theme python-sphinx_rtd_theme --noconfirm --noedit

cp -r /io/* /tmp
cd /tmp
pip install . --user --break-system-packages --no-deps
~/.local/bin/mo2fmu -h
~/.local/bin/mo2fmu ./otfmi/example/file/deviation.mo ./otfmi/example/file/fmu/linux-x86_64/deviation.fmu
pythonfmu build --file ./otfmi/example/file/DeviationSlave.py --dest ./otfmi/example/file/fmu/linux-x86_64

pytest test -s
cd doc && make html BUILDDIR=~/.local/share/otfmi/doc

UID_GID=$1
if test -n "${UID_GID}"
then
  sudo cp -r ~/.local/share/*/doc/html /io
  sudo chown -R ${UID_GID} /io/html
fi
