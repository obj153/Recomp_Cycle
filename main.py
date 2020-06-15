import numpy as np
import CoolProp as CP

def Turbine(Ti, Pi, Rp, fluid, eff):
    Turb_in = CP.AbstractState("HEOS", fluid)
    PT = CP.CoolProp.generate_update_pair(CP.iP, Pi, CP.iT, Ti)
    Turb_in.update(PT[0],PT[1],PT[2])
    k = Turb_in.cpmass() / Turb_in.cvmass()
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
    k = Comp_in.cpmass() / Comp_in.cvmass()
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

def HTR(Th_i, Tl_i, eff, Ph, Pl, fluid):
    Ch = CP.CoolProp.PropsSI('C', 'T', Th_i, 'P', Pl, fluid)
    Cl = CP.CoolProp.PropsSI('C', 'T', Tl_i, 'P', Ph, fluid)
    Th_o = Th_i - eff * (Th_i - Tl_i)
    Tl_inter = Tl_i
    for Th_inter in np.arange(Th_o, Th_i, 1):
        Ch_inter = CP.CoolProp.PropsSI('C', 'T', Th_inter, 'P', Pl, fluid)
        Cl_inter = CP.CoolProp.PropsSI('C', 'T', Tl_inter, 'P', Ph, fluid)
        Tl_inter = Tl_inter + Ch * 1 / Cl
        if Th_inter == Tl_inter:
            break
    Tl_o = Tl_inter
    return (Th_o, Tl_o)

def LTR(Th_i, Tl_i, eff, Ph, Pl, fluid, Rs):
    Ch = CP.CoolProp.PropsSI('C', 'T', Th_i, 'P', Pl, fluid)
    Cl = CP.CoolProp.PropsSI('C', 'T', Tl_i, 'P', Ph, fluid) * Rs
    if Ch < Cl:
        Th_o = Th_i - eff * (Th_i - Tl_i)
        Tl_inter = Tl_i
        for Th_inter in np.arange(Th_o, Th_i, 1):
            Ch_inter = CP.CoolProp.PropsSI('C', 'T', Th_inter, 'P', Pl, fluid)
            Cl_inter = CP.CoolProp.PropsSI('C', 'T', Tl_inter, 'P', Ph, fluid)
            Tl_inter = Tl_inter + Ch * 1 / Cl
            if Th_inter == Tl_inter:
                break
        Tl_o = Tl_inter
    else:
        Tl_o = Tl_i + eff * (Th_i - Tl_i)
        Th_inter = Th_i
        for Tl_inter in np.arange(Tl_o, Tl_i, -1):
            Ch_inter = CP.CoolProp.PropsSI('C', 'T', Th_inter, 'P', Pl, fluid)
            Cl_inter = CP.CoolProp.PropsSI('C', 'T', Tl_inter, 'P', Ph, fluid)
            Th_inter = Th_inter + Cl * (-1) / Ch
            if Th_inter == Tl_inter:
                break
        Th_o = Th_inter
    return (Th_o, Tl_o)

def Mixing(T1, T2, P, Rs, fluid):
    H1 = CP.CoolProp.PropsSI('H', 'T', T1, 'P', P, fluid) * Rs
    H2 = CP.CoolProp.PropsSI('H', 'T', T2, 'P', P, fluid) * (1 - Rs)
    Hf = H1 + H2
    Tf = CP.CoolProp.PropsSI('T', 'H', Hf, 'P', P, fluid)
    return Tf
        


# Recompression Loop

T1 = 32 + 273.15
T5 = 550 + 273.15
P_High = 25 * 10 ** 6
Turbine_eff = 0.8
Compressor_eff = 0.7
Heat_exchanger_eff = 0.95
fluid = "CO2"
Ans_list = []

for Rp in np.arange(1.1, 3, 0.1):
    for Rs in np.arange(0.3, 0.7, 0.05):
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
            HTR_outlet = HTR(T6, T3, Heat_exchanger_eff, P_High, P_Low, fluid)
            T7 = HTR_outlet[0]
            T4 = HTR_outlet[1]
        q_in = Heater(T4, T5, P_High, fluid)
        q_out = Cooler(T8, T1, P_Low, fluid, Rs)
        w_out = q_in - q_out
        Total_eff = w_out / q_in * 100
        Ans_list.append([Rp, Rs, Total_eff])
        print([Rp,Rs])

for i in Ans_list:
    print (i)














