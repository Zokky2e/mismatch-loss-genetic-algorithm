import math
import numpy as np
from scipy.optimize import fsolve

from SolarPanel import SolarPanel

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
	Vt = (k*A*T*N)/q
	Rs =  (Voc/Imp) - (Vmp/Imp) + ((Vt/Imp)*math.log((Vt)/(Vt + Vmp)))
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
	solarPanel.a = A1
	solarPanel.i0 = I02
	solarPanel.ipv = Ipv2
	solarPanel.rs = Rs1
	solarPanel.rp = Rpnew
	return solarPanel
