import numpy as np
import CoolProp as CP

def Turbine(Ti, Pi, Rp, fluid, eff):
    Turb_in = CP.AbstractState("HEOS", fluid)
    PT = CP.CoolProp.generate_update_pair(CP.iP, Pi, CP.iT, Ti)
    Turb_in.update(PT[0],PT[1],PT[2])
    k = Tst.cpmass() / Tst.cvmass()
    To_s = Ti / (Rp ** ((k - 1) / k))
    Po_s = Pi / Rp
    hi = CP.CoolProp.PropsSI('H', 'T', Ti, 'P', Pi, fluid)
    ho_s = CP.CoolProp.PropsSI('H', 'T', To_s, 'P', Po_s, fluid)
    ho = hi - eff * (hi - ho_s)
    Po = Po_s
    To = CP.CoolProp.PropsSI('T', 'H', ho, 'P', Po, fluid)
    return (ho, Po, To)

def Compressor(Ti, Pi, Rp, fluid, eff):
    Comp_in = CP.AbstractState("HEOS", fluid)
    PT = CP.CoolProp.generate_update_pair(CP.iP, Pi, CP.iT, Ti)
    Comp_in.update(PT[0],PT[1],PT[2])
    k = Tst.cpmass() / Tst.cvmass()
    To_s = Ti * (Rp ** ((k - 1) / k))
    Po_s = Pi * Rp
    hi = CP.CoolProp.PropsSI('H', 'T', Ti, 'P', Pi, fluid)
    ho_s = CP.CoolProp.PropsSI('H', 'T', To_s, 'P', Po_s, fluid)
    ho = ((ho_s - hi) / eff) + hi
    Po = Po_s
    To = CP.CoolProp.PropsSI('T', 'H', ho, 'P', Po, fluid)
    return (ho, Po, To)

def Heater(Ti, To, P, fluid):
    Cp = CP.CoolProp.PropsSI('C', 'T', Ti, 'P', P, fluid)
    q_in = Cp * (To - Ti)
    return q_in

def Cooler(Ti, To, P, fluid, Rs):
    Cp = CP.CoolProp.PropsSI('C', 'T', Ti, 'P', P, fluid)
    q_out = Rs * Cp * (Ti - To)
    return q_out


Tst = CP.AbstractState("HEOS", "Air")
PT = CP.CoolProp.generate_update_pair(CP.iP, 101325, CP.iT, 300)
print(PT)
Tst.update(PT[0],PT[1],PT[2])
k = Tst.cpmass() / Tst.cvmass()
print(k)

print (Turbine(550 + 273.15, 25 * 10 ** 6, 9, "CO2", 0.8))
