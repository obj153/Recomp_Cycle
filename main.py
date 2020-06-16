import numpy as np
import CoolProp as CP

def heat_ratio(T, P, fluid):
    condition = CP.AbstractState("HEOS", fluid)
    PT = CP.CoolProp.generate_update_pair(CP.iP, P, CP.iT, T)
    condition.update(PT[0],PT[1],PT[2])
    k = condition.cpmass() / condition.cvmass()
    return k

def Turbine(Ti, Pi, Rp, fluid, eff):
    Po_s = Pi / Rp
    dP = (Pi - Po_s) / 100.0
    T_inter = Ti
    print (dP)
    for i in range(101):
        P_inter = Pi - dP * i
        Rp_inter = P_inter / (P_inter - dP)
        k = heat_ratio(T_inter, P_inter, fluid)
        T_inter = T_inter / (Rp_inter ** ((k - 1) / k))
    To_s = T_inter
    hi = CP.CoolProp.PropsSI('H', 'T', Ti, 'P', Pi, fluid)
    ho_s = CP.CoolProp.PropsSI('H', 'T', To_s, 'P', Po_s, fluid)
    ho = hi - eff * (hi - ho_s)
    Po = Po_s
    To = CP.CoolProp.PropsSI('T', 'H', ho, 'P', Po, fluid)
    return (ho, Po, To)

def Compressor(Ti, Pi, Rp, fluid, eff):
    Po_s = Pi * Rp
    dP = (Po_s - Pi) / 100.0
    T_inter = Ti
    for i in range(101):
        P_inter = Pi + dP * i
        Rp_inter = (P_inter + dP) / P_inter
        k = heat_ratio(T_inter, P_inter, fluid)
        T_inter = T_inter * (Rp_inter ** ((k - 1) / k))
    To_s = T_inter
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
    hh_i = CP.CoolProp.PropsSI('H', 'T', Th_i, 'P', Pl, fluid)
    hh_o = CP.CoolProp.PropsSI('H', 'T', Th_o, 'P', Pl, fluid)
    hl_i = CP.CoolProp.PropsSI('H', 'T', Tl_i, 'P', Ph, fluid)
    hl_o = hh_i + hl_i - hh_o
    Tl_o = CP.CoolProp.PropsSI('T', 'H', hl_o, 'P', Pl, fluid)
    return (Th_o, Tl_o)

def LTR(Th_i, Tl_i, eff, Ph, Pl, fluid, Rs):
    Ch = CP.CoolProp.PropsSI('C', 'T', Th_i, 'P', Pl, fluid)
    Cl = CP.CoolProp.PropsSI('C', 'T', Tl_i, 'P', Ph, fluid) * Rs
    if Ch < Cl:
        Th_o = Th_i - eff * (Th_i - Tl_i)
        hh_i = CP.CoolProp.PropsSI('H', 'T', Th_i, 'P', Pl, fluid)
        hh_o = CP.CoolProp.PropsSI('H', 'T', Th_o, 'P', Pl, fluid)
        hl_i = CP.CoolProp.PropsSI('H', 'T', Tl_i, 'P', Ph, fluid)
        hl_o = hh_i + hl_i - hh_o
        Tl_o = CP.CoolProp.PropsSI('T', 'H', hl_o, 'P', Pl, fluid)
    else:
        Tl_o = Tl_i + eff * (Th_i - Tl_i)
        hh_i = CP.CoolProp.PropsSI('H', 'T', Th_i, 'P', Pl, fluid)
        hl_o = CP.CoolProp.PropsSI('H', 'T', Tl_o, 'P', Pl, fluid)
        hl_i = CP.CoolProp.PropsSI('H', 'T', Tl_i, 'P', Ph, fluid)
        hh_o = hh_i + hl_i - hl_o
        Th_o = CP.CoolProp.PropsSI('T', 'H', hh_o, 'P', Pl, fluid)
    return (Th_o, Tl_o)

def Mixing(T1, T2, P, Rs, fluid):
    H1 = CP.CoolProp.PropsSI('U', 'T', T1, 'P', P, fluid) * Rs
    H2 = CP.CoolProp.PropsSI('U', 'T', T2, 'P', P, fluid) * (1 - Rs)
    Hf = H1 + H2
    Tf = CP.CoolProp.PropsSI('T', 'U', Hf, 'P', P, fluid)
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

for Rp in np.arange(1, 10.1, 0.5):
    for Rs in np.arange(0.1, 1, 0.1):
        Turbine_outlet = Turbine(T5, P_High, Rp, fluid, Turbine_eff)
        P_Low = Turbine_outlet[1]
        T6 = Turbine_outlet[2]
        MC_outlet = Compressor(T1, P_Low, Rp, fluid, Compressor_eff)
        T2 = MC_outlet[2]
        T7 = T2
        T7_old = 0
        while True:
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
            if abs(T7 - T7_old) < 1:
                break
        h1 = CP.CoolProp.PropsSI('H', 'T', T1, 'P', P_Low, fluid)
        h2 = CP.CoolProp.PropsSI('H', 'T', T2, 'P', P_High, fluid)
        h3 = CP.CoolProp.PropsSI('H', 'T', T3, 'P', P_High, fluid)
        h4 = CP.CoolProp.PropsSI('H', 'T', T4, 'P', P_High, fluid)
        h5 = CP.CoolProp.PropsSI('H', 'T', T5, 'P', P_High, fluid)
        h6 = CP.CoolProp.PropsSI('H', 'T', T6, 'P', P_Low, fluid)
        h8 = CP.CoolProp.PropsSI('H', 'T', T8, 'P', P_Low, fluid)
        q_in = h5 - h4
        w_t = h5 - h6
        w_mc = Rs * (h2 - h1)
        w_rc = (1 - Rs) * (h3 - h8)
        w_out = - (w_t - w_mc - w_rc)
        Total_eff = w_out / q_in * 100
        Ans_list.append([Rp, 1 - Rs, Total_eff])
        print([Rp,Rs, q_in, w_out, Total_eff])

for i in Ans_list:
    print (i)














