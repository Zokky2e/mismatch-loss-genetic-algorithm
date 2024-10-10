from enum import Enum
from SolarPanel import SolarPanel
from math import exp, log
import numpy as np

#Types of sort in genetic algorithm
class SortType(Enum):
    SHUFFLE = 0,
    IMPP = 1,
    UMPP = 2,
    PMPP = 3

def swap_duplicate(child_panels: list[SolarPanel], unused_panels: list[SolarPanel]) -> list[SolarPanel]:
    new_child_panels: list[SolarPanel] = child_panels.copy()
    seen_serials = set()
    for i, panel in enumerate(child_panels):
        if panel.serialnumber in seen_serials:
            unused_panel = unused_panels.pop(0)
            new_child_panels[i] = unused_panel
        seen_serials.add(new_child_panels[i].serialnumber)
    return new_child_panels

def has_duplicate_panels(panels: list[SolarPanel]) -> int:
    seen_serials = set()
    count = 0
    for panel in panels:
        if panel.serialnumber in seen_serials:
            count += 1
        seen_serials.add(panel.serialnumber)
    return count

def flatten_panels_recursively(nested_list) -> list[SolarPanel]:
    flat_list = []
    for item in nested_list:
        if isinstance(item, SolarPanel):
            flat_list.append(item)
        elif isinstance(item, (list, np.ndarray)):
            flat_list.extend(flatten_panels_recursively(item))
        else:
            print(f"Error: Found a non-SolarPanel object: {type(item)}")
    return flat_list

def reconstruct_configuration(
flattened_list: list[SolarPanel], 
L: int, M: int, N: int
) -> list[list[list[SolarPanel]]]:
    expected_total_panels_per_configuration = L * M * N
    child: list[list[list[SolarPanel]]] = []
    index = 0
    total_configurations_count = len(flattened_list)//expected_total_panels_per_configuration
    for _ in range(total_configurations_count):
        config = []
        for _ in range(N):
            series_block: list[list[SolarPanel]] = []
            for _ in range(M):
                substring: list[SolarPanel] = flattened_list[index:index + L]
                index += L
                series_block.append(substring)
            config.append(series_block)
        child.append(config)
    return child

def compute(I, solarPanel: SolarPanel, calc_function, start_value=0.0, max_iterations: int=1000):
    tolerance = 1e-3
    prev_value = start_value  # Initial guess for voltage
    iterations = 0
    while iterations < max_iterations:
        new_value = calc_function(I, prev_value, solarPanel)
        if abs(new_value - prev_value) < tolerance:
            break
        prev_value = new_value
        iterations += 1
    return new_value
    
def do_Voltage_Calc(constant: float, prev_value: float, solarPanel:SolarPanel):
    q = 1.6e-19
    k = 1.38e-23
    T = 298
    Vt = (k*solarPanel.a*T*144)/q
    def safe_log(x, min_value=1e-10):
        return log(max(x, min_value))
    log_value = ((solarPanel.ipv + solarPanel.i0) - constant - (prev_value + constant * solarPanel.rs) / solarPanel.rp) / solarPanel.i0
    term1 = Vt * safe_log(log_value)
    term2 = solarPanel.rs * constant
    return term1 - term2
    
def do_Current_Calc(constant: float, prev_value: float, solarPanel:SolarPanel):
    q = 1.6e-19
    k = 1.38e-23
    T = 298
    Vt = (k*solarPanel.a*T*144)/q
    term1 = solarPanel.ipv - solarPanel.i0 * (exp((constant + prev_value * solarPanel.rs) / Vt) - 1)
    term2 = (constant + prev_value * solarPanel.rs) / solarPanel.rp
    return term1 - term2
    
def do_Rp_Calc(constant: float, prev_value: float, solarPanel:SolarPanel):
    q = 1.6e-19
    k = 1.38e-23
    T = 298
    Vt = (k*solarPanel.a*T*144)/q
    term1 = solarPanel.ipv - solarPanel.i0 * (exp((constant + prev_value * solarPanel.rs) / Vt) - 1)
    term2 = (constant + prev_value * solarPanel.rs) / solarPanel.rp
    return term1 - term2
    
    
from scipy.optimize import fsolve
import warnings
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


