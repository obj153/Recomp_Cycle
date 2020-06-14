import numpy as np
from CoolProp.CoolProp as CP

def Turbine(Ti, Pi, Rp, fluid, eff):
    k = CP.PropsSI('C', 'P', Pi, 'T', Ti, fluid)
    To = Ti / (Rp ** ((k - 1) / k))
    return None

print("Hello Git!")
k = CP.PropsSI('Cp', 'P', 101325, 'T', 300, 'Air') / CP.PropsSI('Cv', 'P', 101325, 'T', 300, 'Air')
print(k)