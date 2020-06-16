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

T1 = 32 + 273.15
T5 = 550 + 273.15
P_High = 25 * 10 ** 6
Turbine_eff = 0.8
Compressor_eff = 0.7
Heat_exchanger_eff = 0.95
fluid = "CO2"

Ans_list=[]
Rp_list = [1,1.5,2,3,4,5,6,7,10,15]

for Rp in Rp_list:
    Turbine_outlet = Turbine(T5, P_High, Rp, fluid, Turbine_eff)
    P_Low = Turbine_outlet[0]
    MC_outlet = Compressor(T1, P_Low, Rp, fluid, Compressor_eff)
    print (["Turbine", Turbine_outlet, "Compressor", MC_outlet, Rp])
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

