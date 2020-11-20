import pyfmi

model = pyfmi.load_fmu('wrapper2.fmu')
model.initialize()
res = model.simulate(options={'silent_mode': True})
print(model.get_model_variables().keys())
print(res['y0'][-1])

