
from SolarPanel import SolarPanel
from exportSolarPanels import exportPanels
from mismatchCalculations import *
from sharedMethods import *
import numpy as np

def printConfiguration(
    configuration: list[list[SolarPanel]],
    L: int, M: int, config
):
    counter = 0
    cc = 0
    total_loss = 0
    print(f"{config} configuration({cc}) total mismatch lost: {round(total_loss, 4)}")
    for group in configuration:
        total_loss+= calculate_mismatch_loss(flatten_panels_recursively(group), L, M)
        for substring in group:
            print("[")
            for panel in substring: # type: ignore
                print(f"{panel.serialnumber}: {panel.impp}")
            print("],")
    print(f"mismatch loss: {total_loss:.9f}")

def initialize_first_population(
    solar_panels: list[SolarPanel], 
    L: int
    ) -> list[list[SolarPanel]]:
    configuration = group_panels(solar_panels, L)
    return configuration


def doSHUFFLEConfiguration(solarPanels: list[SolarPanel], L, M, config, output_file):
    sorted_solar_panels = np.array(solarPanels)
    np.random.shuffle(sorted_solar_panels)
    doFirstConfiguration(list(sorted_solar_panels), L, M, config, output_file)

def doIMPPConfiguration(solarPanels: list[SolarPanel], L, M, config, output_file):
    sorted_solar_panels = sorted(solarPanels, key=lambda x: x.impp, reverse=True)
    doFirstConfiguration(list(sorted_solar_panels), L, M, config, output_file)

def doUMPPConfiguration(solarPanels: list[SolarPanel], L, M, config, output_file):
    sorted_solar_panels = sorted(solarPanels, key=lambda x: x.umpp, reverse=True)
    doFirstConfiguration(sorted_solar_panels, L, M, config, output_file)

def doPMPPConfiguration(solarPanels: list[SolarPanel], L, M, config, output_file):
    sorted_solar_panels = sorted(solarPanels, key=lambda x: x.pmpp, reverse=True)
    doFirstConfiguration(sorted_solar_panels, L, M, config, output_file)

def doFirstConfiguration(solarPanels: list[SolarPanel], L, M, config, output_file):
    start_configuration = initialize_first_population(solarPanels, L)
    printConfiguration(start_configuration, L, M, config)
    exportPanels(flatten_panels_recursively(start_configuration), output_file)
    
