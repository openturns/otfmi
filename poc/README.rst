This folder gather experiments made in attempt to use an OpenTURNS function inside an OpenModelica-built FMU via Python.

- On windows it seems OpenModelica stuck with the static msvc runtime so we cannot link to a third-party lib like Python, or use C++.
- On Linux its possible to use a dynamic lib, but it would need to edit the rpath of the open fmu Makefile,
  instead its possible to copy it into a new ~/.openmodelica/binaries/model_name folder (rpath is set there)
- It it possible to hack the LDFLAGS of the fmu by adding link flags to the .mo, e.g.: Library="cwrapper -Wl,-rpath=..."
- Building the xml function once via the Python C API for an OpenTURNS function maybe be faster than
  running a Python process that loads the xml and evaluates the function by file exchange.
- Building a very basic cache of size 1 is as the modelica solver continuously calls the function for each time step
  for vector functions.
- For field functions we must return at each call with the same input the next value in the field, what's missing is the interpolation.
