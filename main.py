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

def HTR(Th_i, Tl_i, eff):
    Th_o = Th_i - eff * (Th_i - Tl_i)
    Tl_o = Tl_i + Th_o - Th_i
    return (Th_o, Tl_o)

def LTR(Th_i, Tl_i, eff, Ph, Pl, fluid, Rs):
    Ch = CP.CoolProp.PropsSI('C', 'T', Th_i, 'P', Ph, fluid)
    Cl = CP.CoolProp.PropsSI('C', 'T', Tl_i, 'P', Pl, fluid) * Rs
    if Ch < Cl:
        Th_o = Th_i - eff * (Th_i - Tl_i)
        Tl_o = Tl_i + Ch * (Th_i - Th_o) / Cl
    else:
        Tl_o = Tl_i + eff * (Th_i - Tl_i)
        Th_o = Th_i - Cl * (Tl_o - Tl_i) / Ch
    return (Th_o, Tl_o)

def Mixing(T1, T2, P, Rs, fluid):
    H1 = CP.CoolProp.PropsSI('H', 'T', T1, 'P', P, fluid) * Rs
    H2 = CP.CoolProp.PropsSI('H', 'T', T2, 'P', P, fluid) * (1 - Rs)
    Hf = H1 + H2
    Tf = CP.CoolProp.PropsSI('T', 'H', Hf, 'P', P, fluid)
    return Tf
        

Tst = CP.AbstractState("HEOS", "Air")
PT = CP.CoolProp.generate_update_pair(CP.iP, 101325, CP.iT, 300)
print(PT)
Tst.update(PT[0],PT[1],PT[2])
k = Tst.cpmass() / Tst.cvmass()
print(k)


print (Turbine(550 + 273.15, 25 * 10 ** 6, 9, "CO2", 0.8))
print (Mixing(300, 400, 10131500, 0.5, "CO2"))


# Recompression Loop

T1 = 32 + 273.15
T5 = 550 + 273.15
P_High = 25 * 10 ** 6
Turbine_eff = 0.8
Compressor_eff = 0.7
Heat_exchanger_eff = 0.95
fluid = "CO2"
Ans_list = []

for Rp in range(0, 15, 0.2):
    for Rs in range(0, 1, 0.05):
        Turbine_outlet = Turbine(T5, P_High, Rp, fluid, Turbine_eff)
        P_Low = Turbine_outlet[1]
        T6 = Turbine_outlet[2]
        MC_outlet = Compressor(T1, P_Low, Rp, fluid, Compressor_eff)
        T2 = MC_outlet[2]
        T7 = T6
        T7_old = 0
        while (abs(T7 - T7_old) > 1):
            LTR_outlet = LTR(T7, T2, Heat_exchanger_eff, P_High, P_Low, fluid, Rs)
            T8 = LTR_outlet[0]
            T3b = LTR_outlet[1]
            RC_outlet = Compressor(T8, P_Low, Rp, fluid, Compressor_eff)
            T3a = RC_outlet[2]
            T3 = Mixing(T3b, T3a, P_High, Rs, fluid)
            T7_old = T7
            HTR_outlet = HTR(T6, T3, Heat_exchanger_eff)
            T7 = HTR_outlet[0]
            T4 = HTR_outlet[1]
        q_in = Heater(T4, T5, P_High, fluid)
        q_out = Cooler(T8, T1, P_Low, fluid)
        w_out = q_in - q_out
        Total_eff = w_out / q_in * 100
        Ans_list.append([Rp, Rs, Total_eff])

print Ans_list














