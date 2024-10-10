from math import exp, log
import numpy as np
from scipy.optimize import fsolve, brentq

from SolarPanel import SolarPanel
from sharedMethods import compute, computeArray, do_Array_Current_Calc, do_Array_Voltage_Calc, do_Current_Calc, do_Voltage_Calc

def extraction(solarPanel: SolarPanel, number_of_cells: int):
	q = 1.6e-19
	k = 1.38e-23
	T = 298
	Isc = solarPanel.isc
	Voc = solarPanel.uoc
	Imp = solarPanel.impp
	Vmp = solarPanel.umpp
	N = number_of_cells
	Pmax = Vmp*Imp
	A = solarPanel.ff/100
	if (solarPanel.ff < 1.0):
		A = solarPanel.ff
	Vt = (k*A*T*N)/q
	Rs =  (Voc/Imp) - (Vmp/Imp) + ((Vt/Imp)*log((Vt)/(Vt + Vmp)))
	I0 = Isc/(np.exp(Voc/Vt)) - np.exp(Rs*Isc/Vt)
	Ipv = I0 * (np.exp(Voc/Vt) - 1)

	#firstStep
	iter = 10000
	it = 0
	tol = 0.1
	A1 = A
	VmpC = (Vt * np.log((Ipv + I0 - Imp) / I0)) - (Rs * Imp)
	e1 = VmpC - Vmp
	Rs1 = Rs
	while it < iter and e1 > tol:
		if VmpC < Vmp:
			A1 -= 0.01
		else:
			A1 += 0.01

		Vt1 = (k * A1 * T * N) / q
		I01 = Isc / (np.exp(Voc / Vt1) - np.exp(Rs1 * Isc / Vt1))
		Ipv1 = I01 * (np.exp(Voc / Vt1) - 1)
		VmpC = (Vt1 * np.log((Ipv1 + I01 - Imp) / I01)) - (Rs1 * Imp)
		e1 = VmpC - Vmp
		it += 1
	vt1 = (k * A1 * T * N) / q
	Rs1 = (Voc / Imp) - (VmpC / Imp) + ((vt1 / Imp) * np.log(vt1 / (vt1 + VmpC)))

	#secondStep
	tolI = 0.001
	iter = 10000
	itI = 0
	I01 = Isc / (np.exp(Voc / vt1) - np.exp(Rs1 * Isc / vt1))
	Ipv1 = I01 * (np.exp(Voc / vt1) - 1)
	Rp = ((-Vmp) * (Vmp + (Rs1 * Imp))) / (Pmax - (Vmp * Ipv1) + (Vmp * I01 * (np.exp((Vmp + (Rs1 * Imp)) / vt1) - 1)))
	I02 = (Isc * (1 + Rs1 / Rp) - Voc / Rp) / (np.exp(Voc / vt1) - np.exp(Rs1 * Isc / vt1))
	Ipv2 = I02 * (np.exp(Voc / vt1) - 1) + Voc / Rp
	ImpC = Pmax / VmpC
	err = abs(Imp - ImpC)
	Rpnew = Rp
	while err > tolI and itI < iter:
		if ImpC < Imp:
			Rpnew = Rp + 0.1 * itI
		else:
			Rpnew = Rp - 0.1 * itI
		I02 = (Isc * (1 + Rs1 / Rpnew) - Voc / Rpnew) / (np.exp(Voc / vt1) - np.exp(Rs1 * Isc / vt1))
		Ipv2 = I02 * (np.exp(Voc / vt1) - 1) + Voc / Rpnew
		def eqn(ImpC):
			return Ipv2 - (I02 * (np.exp((Vmp + (Rs1 * ImpC)) / vt1) - 1)) - ImpC - (Vmp + Rs1 * ImpC) / Rpnew
		current_c = Imp
		ImpC = fsolve(eqn, current_c)[0]  # Using fsolve to solve the equation
		itI += 1
		err = abs(Imp - ImpC)

	#thirdStep
	vt_new = (k*A1*T*N)/q
	tolerance = 1e-6  # Convergence tolerance
	max_iterations = 1000  #Safety to avoid infinite loop
	# Iteratively find I
	previous_I = solarPanel.impp
	iterations = 0
	while iterations < max_iterations:
		term1 = Ipv2 - I02 * (exp((VmpC + previous_I * Rs1) / vt_new) - 1)
		term2 = (VmpC + previous_I * Rs1) / Rpnew
		new_I = term1 - term2
		if abs(new_I - previous_I) < tolerance:
			break
		previous_I = new_I
		iterations += 1
	I_solution = new_I

	#thirdStep
	tolerance = 1e-6  # Convergence tolerance
	max_iterations = 1000  #Safety to avoid infinite loop
	# Iteratively find I
	previous_V = solarPanel.uoc
	iterations = 0
	while iterations < max_iterations:
		term1 = vt_new * log(((Ipv2 + I02) - I_solution - (previous_V + I_solution * Rs1) / Rpnew) / I02)
		term2 = Rs1 * I_solution
		new_V = term1 - term2
		if abs(new_V - previous_V) < tolerance:
			break
		previous_V = new_V
		iterations += 1
	V_solution = new_V

	solarPanel.u = V_solution
	solarPanel.i = I_solution
	solarPanel.p = V_solution * I_solution
	solarPanel.a = A1
	solarPanel.i0 = I02
	solarPanel.ipv = Ipv2
	solarPanel.rs = Rs1
	solarPanel.rp = Rpnew
	return solarPanel

import matplotlib.pyplot as plt
def plotPanel(solarPanel: SolarPanel):
    # Function to compute V iteratively for a given I
	
	I_values = np.linspace(0, solarPanel.isc, 10000)  # 100 current points between 0 and I_pv
	V_values = []
	P_values = []
	q = 1.6e-19
	k = 1.38e-23
	T = 298
	N = 60
	vt_new = (k*solarPanel.a*T*N)/q
	# Calculate the voltage for each current
	for I in I_values:
		V = compute(I, solarPanel, do_Voltage_Calc)
		V_values.append(V)
	

	plt.figure(figsize=(8, 6))
	V_values[-1] = 0
	# Plot the U-I curve
	plt.plot(V_values, I_values, label='U-I Curve')
	plt.title('U-I Curve for the Solar Panel')
	plt.ylabel('Current [A]')
	plt.xlabel('Voltage [V]')
	plt.xlim(0, 50)  # Set x-axis from 0 to maximum voltage
	plt.ylim(0, 10)
	plt.grid(True)
	plt.legend()
	plt.savefig('UICurve.png', dpi=300, bbox_inches='tight')

	V_values = np.linspace(0, solarPanel.uoc, 100000)
	for V in V_values:
		I_solution = compute(V, solarPanel, do_Current_Calc, 0.0, 10000)
		P_values.append(float(V)*float(I_solution))

	P_new = [P_values[i] for i in range(len(P_values)) if P_values[i] >= 0]
	V_new = [V_values[i] for i in range(len(V_values)) if P_values[i] >= 0]
	# Plot the P-I curve
	plt.figure(figsize=(8, 6))
	plt.plot(V_new, P_new, label='Power Curve', color='r', linewidth=2)
	plt.title('Power Curve for the Solar Panel', fontsize=16, fontweight='bold')
	plt.ylabel('Power [W]', fontsize=12)
	plt.xlabel('Voltage [V]', fontsize=12)
	plt.grid(True, which='both', linestyle='--', linewidth=0.7)
	plt.savefig('PVCurve.png', dpi=300, bbox_inches='tight')
	plt.show()


def current_from_voltage(U, U_max, I_max):
    I = I_max * (1 - np.exp((U - U_max) / (0.05 * U_max)))  # Exponential decay
    return I

from scipy.optimize import curve_fit
def plotPanelGroup(index: int, max_voltage: float, max_current: float, max_power: float, group: list[SolarPanel]):
    # Function to compute V iteratively for a given I
	q = 1.6e-19
	k = 1.38e-23
	T = 298
	voc = sum([panel.uoc for panel in group])
	rs = max_voltage / max_current
	isc = min([panel.isc for panel in group])
	rp = 1 / sum(1 / panel.rp for panel in group)
	ipv = min([panel.ipv for panel in group])
	a = np.mean([panel.a for panel in group])
	V_values = np.linspace(max_voltage, voc, 100000)
	i0 = max([panel.i0 for panel in group])
	I_values = [computeArray(V,isc,voc,max_voltage,max_current, rs, rp, a, do_Array_Current_Calc) for V in V_values]
	P_values = V_values * I_values  # P = V * I
	print(max(P_values))
	plt.figure(figsize=(8, 6))
	plt.plot(V_values, I_values, label='U-I Characteristic', color='blue', linewidth=2)
	plt.title('U-I Characteristic of the Group of 20 Panels', fontsize=16, fontweight='bold')
	plt.xlabel('Voltage (V)', fontsize=12)
	plt.ylabel('Current (A)', fontsize=12)
	plt.grid(True, which='both', linestyle='--', linewidth=0.7)
	plt.savefig(f'curves/U-I_Curve{index}.png', dpi=300, bbox_inches='tight')
	plt.figure(figsize=(8, 6))
	plt.plot(V_values, P_values, label='U-I Characteristic', color='red', linewidth=2)
	plt.title('P-V Characteristic of the Group of 20 Panels', fontsize=16, fontweight='bold')
	plt.xlabel('Voltage (V)', fontsize=12)
	plt.ylabel('Power (W)', fontsize=12)
	plt.grid(True, which='both', linestyle='--', linewidth=0.7)
	plt.savefig(f'curves/P-V_Curve{index}.png', dpi=300, bbox_inches='tight')