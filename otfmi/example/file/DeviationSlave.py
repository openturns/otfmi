import openturns as ot
from pythonfmu.fmi2slave import Fmi2Slave, Fmi2Causality, Real


class DeviationSlave(Fmi2Slave):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__function = ot.SymbolicFunction(["E", "F", "L", "II"], ["F*L^3/(3*E*II)"])

        for var in self.__function.getInputDescription():
            setattr(self, var, 0.0)
            self.register_variable(Real(var, causality=Fmi2Causality.input))

        for var in self.__function.getOutputDescription():
            setattr(self, var, 0.0)
            self.register_variable(Real(var, causality=Fmi2Causality.output))

    def do_step(self, current_time, step_size):
        inP = [getattr(self, var) for var in self.__function.getInputDescription()]
        outP = self.__function(inP)
        for i, var in enumerate(self.__function.getOutputDescription()):
            setattr(self, var, outP[i])
        return True
