import numpy as np
import CoolProp as CP

def Turbine(Ti, Pi, Rp, fluid, eff):
    k = CP.PropsSI('C', 'P', Pi, 'T', Ti, fluid)
    To = Ti / (Rp ** ((k - 1) / k))
    return None


Tst = CP.AbstractState("HEOS", "Air")
PT = CP.CoolProp.generate_update_pair(CP.iP, 101325, CP.iT, 300)
print(PT)
Tst.update(PT[0],PT[1],PT[2])
k = Tst.cvmass()
print(k)
