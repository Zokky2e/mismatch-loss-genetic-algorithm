# print("Old panel:")
# print(sortedGroupedPanels[group1][0])
# sortedGroupedPanels[group1][0].pmpp = 230.0
# sortedGroupedPanels[group1][0].uoc = 35.4
# sortedGroupedPanels[group1][0].isc = 8.6
# sortedGroupedPanels[group1][0].umpp = 29.1
# sortedGroupedPanels[group1][0].impp = 7.93
# sortedGroupedPanels[group1][0] = extraction(sortedGroupedPanels[group1][0], 60)
# print("New panel:")
# print(sortedGroupedPanels[group1][0])
import numpy as np
from math import exp, log
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
import warnings
from SolarPanel import SolarPanel
my_array = [7, 8, 10, 15, 16, 7, 8, 10, 11, 12]

print (np.std(my_array)**2)

av = np.average(my_array)
n = len(my_array)
my_sum = np.sum([(el - av)**2  for el in my_array])
print(my_sum/n)

# with ThreadPoolExecutor() as ex:
#     futures = [
#         ex.submit(compute, I, panel, do_Voltage_Calc, ) for i, panel in enumerate(groupedPanels)
#     ]
#     for future in futures:
#         v+= future.result()

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

warnings.filterwarnings('ignore', 'The iteration is not making good progress')
def computeArray(constant, isc, voc, vmax, imax, rs, rp, a, calc_function, max_iterations: int=1000):
    def equations(vars):
        I_L, I_0, a = vars
        eq1 = isc - I_L + I_0 * (np.exp((isc/a * rs/a)) - 1) + (isc * rs) / rp
        eq2 = - I_L + I_0 * (np.exp(voc / a) - 1) + voc / rp
        eq3 = imax - I_L + I_0 * (np.exp(vmax/a + imax * (rs/a)) - 1) + (vmax + imax * rs) / rp
        return [eq1, eq2, eq3]
    initial_guess = [isc, 1e-10, 1]
    solution = fsolve(equations, initial_guess)
    I_L, I_0, a_new = solution # type: ignore
    tolerance = 1e-6
    prev_value = 0.0  # Initial guess for voltage
    iterations = 0
    while iterations < max_iterations:
        new_value = calc_function(constant, prev_value, I_L, I_0, rs, rp, a_new)
        if abs(new_value - prev_value) < tolerance:
            break
        prev_value = new_value
        iterations += 1
    return new_value
    
def do_Array_Voltage_Calc(constant: float, prev_value: float, ipv, i0, rs, rp, a):
    q = 1.6e-19
    k = 1.38e-23
    T = 298
    Vt = (k*a*T*144)/q
    def safe_log(x, min_value=1e-10):
        return log(max(x, min_value))
    log_value = ((ipv + i0) - constant - (prev_value + constant * rs) / rp) / i0
    term1 = Vt * safe_log(log_value)
    term2 = rs * constant
    return term1 - term2

def do_Array_Current_Calc(constant: float, prev_value: float, ipv, i0, rs, rp, a):
    exp_term = np.clip(((constant + prev_value * rs) / a), -700, 700)
    term1 = ipv - i0 * (exp(exp_term)-1)
    term2 = (constant + prev_value * rs) / rp
    return term1 - term2

def current_from_voltage(U, U_max, I_max):
    I = I_max * (1 - np.exp((U - U_max) / (0.05 * U_max)))  # Exponential decay
    return I
