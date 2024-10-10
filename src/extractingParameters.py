from math import exp, log
import numpy as np
from scipy.optimize import fsolve, brentq
import matplotlib.pyplot as plt
from SolarPanel import SolarPanel
from sharedMethods import compute, do_Current_Calc, do_Voltage_Calc

def extraction(solarPanel: SolarPanel, number_of_cells: int):
	q = 1.6e-19
	k = 1.38e-23
	T = 298
	Isc, Voc, Imp, Vmp = solarPanel.isc, solarPanel.uoc, solarPanel.impp, solarPanel.umpp
	N, Pmax = number_of_cells, Vmp*Imp
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
		ImpC = fsolve(eqn, current_c)[0]
		itI += 1
		err = abs(Imp - ImpC)

	#thirdStep
	vt_new = (k*A1*T*N)/q
	tolerance = 1e-6
	max_iterations = 1000
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

	#forthStep
	tolerance = 1e-6
	max_iterations = 1000
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

	solarPanel.u, solarPanel.i, solarPanel.p = V_solution, I_solution, V_solution * I_solution
	solarPanel.a, solarPanel.i0, solarPanel.ipv, = A1, I02, Ipv2
	solarPanel.rs, solarPanel.rp = Rs1, Rpnew
	return solarPanel

def plotPanel(solarPanel: SolarPanel):
	I_values = np.linspace(0, solarPanel.isc, 10000)
	V_values = []
	P_values = []
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
	plt.xlim(0, 50)
	plt.ylim(0, 10)
	plt.grid(True)
	plt.legend()
	plt.savefig('UICurve.png', dpi=300, bbox_inches='tight')

	V_values = np.linspace(0, solarPanel.uoc, 10000)
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
