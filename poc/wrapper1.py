import pyfmi

model = pyfmi.load_fmu('wrapper1.fmu')
model.initialize()
model.reset()
res = model.simulate(options={'silent_mode': True})
print(model.get_model_variables().keys())
print(res['y0'][-1])
