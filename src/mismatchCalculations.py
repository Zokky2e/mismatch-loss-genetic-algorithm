from concurrent.futures import ThreadPoolExecutor
import numpy as np
from SolarPanel import SolarPanel
from sharedMethods import compute, do_Voltage_Calc  # Import the SolarPanel class
from scipy.optimize import fsolve

def calculate_mismatch_loss(
    flattened_panels: list[SolarPanel], 
    L: int, M: int, max_values=[0.0,0.0,0.0,0.0]
) -> float:
    """
    Calculate the mismatch loss for a single series block of solar panels.
    """
    #print(max_values)
    #fake_max_values
    group1 = flattened_panels[:L]
    group2 = flattened_panels[L:]
    #print(len(group1), len(group2))
    # Use fsolve to solve for C
    ff = np.average([panel.ff for panel in flattened_panels])
    ff1 = np.average([panel.ff for panel in group1])
    ff2 = np.average([panel.ff for panel in group2])
    if (ff > 1.0):
        ff = ff/100
        ff1 = ff1/100
        ff2 = ff2/100 
    initial_guess = 1.0  # Initial guess for C
    C = fsolve(
        find_C, 
        initial_guess, 
        args=(ff)
    )
    C1 = fsolve(
        find_C, 
        initial_guess, 
        args=(ff1)
    )
    C2 = fsolve(
        find_C, 
        initial_guess, 
        args=(ff2)
    )
    #print(C, C1, C2)
    
    p_group1 = [panel.umpp*panel.impp for panel in group1]
    p_group2 = [panel.umpp*panel.impp for panel in group2]
    umpp_values = [panel.umpp for panel in flattened_panels]
    i_group1 = [panel.impp for panel in group1]
    i_group2 = [panel.impp for panel in group2]
    if (max_values[0] == 0.0):
        max_values[0] = np.mean(umpp_values)
        max_values[1] = np.mean(i_group1)
        max_values[2] = np.mean(i_group2)
        max_values[3] = np.mean([panel.impp*panel.umpp for panel in flattened_panels])

    p_ideal1 = np.sum(p_group1)
    p_ideal2 = np.sum(p_group2)
    #print(p_ideal1, p_ideal2)
    sigma_v = (np.std(umpp_values)/max_values[0])**2
    sigma_i1 = (np.std(i_group1)/max_values[1])**2
    sigma_i2 = (np.std(i_group2)/max_values[2])**2
    alfa = (1 - 1/L) * 1/M
    beta1 = (p_ideal1/max_values[3]) * (C1[0]+2) * sigma_i1
    beta2 = (p_ideal2/max_values[3]) * (C2[0]+2) * sigma_i2
    beta = 0.5 * (beta1 + beta2)
    #print(sigma_v, sigma_i1, sigma_i2, beta)
    gamma = 0.5 * (C[0]+2) * sigma_v/L * (1-1/M)
    
    #print(alfa, beta1, beta2, gamma)
    mismatch_loss = alfa * beta + gamma
    return float(mismatch_loss * 100)

def average_max_value(g1: list[SolarPanel], g2: list[SolarPanel]):
    max_values_groups = [find_max_values_of_group(g1), find_max_values_of_group(g2)]
    total_len = len(g1) + len(g2)
    avg_max_values = [0.0, 0.0, 0.0, 0.0]
    avg_max_values[0] = float(np.sum([max_values_groups[0][0] + max_values_groups[1][0]])/total_len)
    avg_max_values[1] = float(np.mean(max_values_groups[0][1]))
    avg_max_values[2] = float(np.mean(max_values_groups[1][1]))
    avg_max_values[3] = float(np.sum([(max_values_groups[0][2] + max_values_groups[1][2])])/total_len)
    return avg_max_values

def group_panels(solarPanels: list[SolarPanel], L: int) -> list[list[SolarPanel]]:
    return [solarPanels[i:i + L] for i in range(0, len(solarPanels) - len(solarPanels) % L, L)]

import time
import matplotlib.pyplot as plt
def find_max_values_of_group(groupedPanels: list[SolarPanel], group = -1) -> list[float]:
    space = 100
    max_values = [0.0,0.0,0.0] #U I P
    max_isc = min(panel.isc for panel in groupedPanels)
    min_i = min(panel.impp for panel in groupedPanels)
    if (group >= 0):
        min_i = 0
    I_values = np.linspace(min_i, max_isc, space)
    V_values = []
    P_values = []
    for I in I_values:
        v = 0
        for panel in groupedPanels:
            v+= compute(I, panel, do_Voltage_Calc, panel.umpp)
        if (v*I > max_values[2]):
            max_values = [v, I, v*I]
        if (group >= 0):
            P_values.append(v*I)
            V_values.append(v)
    if (group >= 0):
        fig, ax1 = plt.subplots()
        ax1.plot(V_values, I_values, label='U-I', color='r', linewidth=2)
        plt.title('U-I Curve & P-U Curve for the Group')
        ax1.set_ylabel('Current [A]')
        ax1.set_xlabel('Voltage [V]')
        plt.xlim(0, np.sum([panel.uoc for panel in groupedPanels])+50)
        ax1.set_ylim(0, 10)
        ax2 = ax1.twinx() 
        ax2.plot(V_values, P_values, label='P-U', color='b', linewidth=2)
        ax2.set_ylabel('Power [W]',)
        ax2.set_xlabel('Voltage [V]')
        ax2.set_ylim(0, np.sum([panel.pmpp for panel in groupedPanels])+200)
        ax1.grid(True)
        fig.legend(loc='lower right')
        ax2.grid(False)
        plt.savefig(f'curves/UICurve{group}.png', dpi=300, bbox_inches='tight')
    return [round(float(value), 5) for value in max_values]


def find_C(C, FF):
    # Fill factor formula with C
    equation = (C**2 / ((1 + C) * (C + np.log(1 + C)))) - FF
    return equation
