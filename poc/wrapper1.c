#include <stdio.h>
#include <stdlib.h>

void c_func(int nin, double x[], int nout, double y[])
{
  double E = x[0];
  double F = x[1];
  double L = x[2];
  double I = x[3];
  y[0] = F*L*L*L/(3.0*E*I);
}

