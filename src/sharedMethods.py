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

def group_panels(solarPanels: list[SolarPanel], L: int) -> list[list[SolarPanel]]:
    return [solarPanels[i:i + L] for i in range(0, len(solarPanels) - len(solarPanels) % L, L)]

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

def compute(constant, solarPanel: SolarPanel, calc_function, start_value=0.0, max_iterations: int=1000):
    tolerance = 1e-3
    prev_value = start_value  # Initial start guess
    iterations = 0
    while iterations < max_iterations:
        new_value = calc_function(constant, prev_value, solarPanel)
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
