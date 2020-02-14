import openturns as ot
import otmorris
# Define model
ot.RandomGenerator.SetSeed(1)
alpha = ot.DistFunc.rNormal(10)
beta = ot.DistFunc.rNormal(84)
gamma = ot.DistFunc.rNormal(280)
b0 = ot.DistFunc.rNormal()
model = otmorris.MorrisFunction(alpha, beta, gamma, b0)
# Number of trajectories
r = 5
# Define a k-grid level (so delta = 1/(k-1))
k = 5
morris_experiment = otmorris.MorrisExperimentGrid([k] * 20, r)
X = morris_experiment.generate()
# Evaluation of the model on the design: evaluation outside OT
Y = model(X)
# need the bounds when using X and Y
bounds = morris_experiment.getBounds()
# Evaluation of Morris effects
morris = otmorris.Morris(X, Y, bounds)
# Get mean/sigma effects
mean_effects = morris.getMeanElementaryEffects()
mean_abs_effects = morris.getMeanAbsoluteElementaryEffects()
sigma_effects = morris.getStandardDeviationElementaryEffects()
print(mean_effects, mean_abs_effects, sigma_effects, k, r)
