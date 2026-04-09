#!/bin/sh

set -xe

export SOURCE_DATE_EPOCH=1761951600

cp -r /io/* /tmp
cd /tmp
pip install . --user --break-system-packages --no-deps

~/.local/bin/mo2fmu -h
pytest test -s

pip install -r doc/requirements.txt --break-system-packages
cd doc && make html BUILDDIR=~/.local/share/otfmi/doc

UID_GID=$1
if test -n "${UID_GID}"
then
  sudo chown -R ${UID_GID} ~/.local/share/*/doc/html
  sudo cp -pr ~/.local/share/*/doc/html /io
fi

