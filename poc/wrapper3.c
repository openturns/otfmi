#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

PyObject *ot_func = NULL;

void load_ot_func()
{
  if (!ot_func)
  {
    Py_Initialize();
    int rc = PyRun_SimpleString("import openturns as ot; study = ot.Study('/tmp/function.xml')");
    assert(rc == 0);
    rc = PyRun_SimpleString("f = ot.Function(); study.load(); study.fillObject('function', f)");
    assert(rc == 0);
    (void)rc;
    PyObject * main_module = PyImport_ImportModule("__main__");
    assert(main_module);
    PyObject * main_dict = PyModule_GetDict(main_module);
    assert(main_dict);
    ot_func = PyDict_GetItemString(main_dict, "f");
    assert(ot_func);
  }
}

void c_func(int nin, double x[], int nout, double y[])
{
  load_ot_func();
  PyObject * py_x = PyTuple_New(nin);
  assert(py_x);
  for (int i = 0; i < nin; ++ i)
    PyTuple_SetItem(py_x, i, PyFloat_FromDouble(x[i]));
  PyObject *py_y = PyObject_CallFunctionObjArgs(ot_func, py_x, NULL);
  assert(py_y);
  Py_XDECREF(py_x);
  assert(PySequence_Length(py_y) == nout);
  for (int i = 0; i < nout; ++ i)
    y[i] = PyFloat_AsDouble(PySequence_GetItem(py_y, i));
  Py_XDECREF(py_y);
}
