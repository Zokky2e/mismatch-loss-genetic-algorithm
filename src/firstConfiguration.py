
from SolarPanel import SolarPanel
from exportSolarPanels import exportPanels
from mismatchCalculations import *
from sharedMethods import *
import numpy as np

def printConfiguration(
    top_iteration: list[list[list[SolarPanel]]],
    C: float, L: int, M: int, N: int, config, printSerialNumbers
):
    counter = 0
    cc = 0
    total_loss = 0
    for series_block in top_iteration:
            for substring in series_block:
                cc += 1
                flattened_substring = flatten_panels_recursively(substring)
                block_loss = calculate_mismatch_loss(flattened_substring, C, L, M, 1)
                total_loss += block_loss
    print(f"{config} configuration({cc}) total mismatch lost: {round(total_loss, 4)}")
    for configuration in top_iteration:
        counter += 1
        print(f"{counter}. configuration mismatch loss: {round(calculate_mismatch_loss(flatten_panels_recursively(configuration), C, L, M , N),6)}")
        if(printSerialNumbers):
            for group in configuration:
                print(f"{counter}. group mismatch loss: {round(calculate_mismatch_loss(flatten_panels_recursively(group), C, L, M , N),6)}")
                for substring in group:
                    print("[")
                    for panel in substring: # type: ignore
                        print(f"{panel.serialnumber}: {panel.impp}")
                    print("],")


def initialize_first_population(
    solar_panels: list[SolarPanel], 
    L: int, N: int, M: int
    ) -> list[list[list[SolarPanel]]]:
    panels_per_configuration = L * M * N
    configurations_per_set = len(solar_panels) // panels_per_configuration
    configuration = []
    for _ in range(configurations_per_set):
        single_configuration = []
        for _ in range(N):
            series_block = []
            for _ in range(M):
                substring = solar_panels[:L]
                solar_panels = solar_panels[L:]
                series_block.append(substring)
            single_configuration.append(series_block)
        configuration.append(single_configuration)

    return configuration


def doSHUFFLEConfiguration(solarPanels: list[SolarPanel], C, L, M, N, config, output_file, printSerialNumbers):
    sorted_solar_panels = np.array(solarPanels)
    np.random.shuffle(sorted_solar_panels)
    doFirstConfiguration(list(sorted_solar_panels), C, L, M, N, config, output_file, printSerialNumbers)

def doIMPPConfiguration(solarPanels: list[SolarPanel], C, L, M, N, config, output_file, printSerialNumbers):
    sorted_solar_panels = sorted(solarPanels, key=lambda x: x.impp, reverse=True)
    doFirstConfiguration(list(sorted_solar_panels), C, L, M, N, config, output_file, printSerialNumbers)

def doUMPPConfiguration(solarPanels: list[SolarPanel], C, L, M, N, config, output_file, printSerialNumbers):
    sorted_solar_panels = sorted(solarPanels, key=lambda x: x.umpp, reverse=True)
    doFirstConfiguration(sorted_solar_panels, C, L, M, N, config, output_file, printSerialNumbers)

def doPMPPConfiguration(solarPanels: list[SolarPanel], C, L, M, N, config, output_file, printSerialNumbers):
    sorted_solar_panels = sorted(solarPanels, key=lambda x: x.pmpp, reverse=True)
    doFirstConfiguration(sorted_solar_panels, C, L, M, N, config, output_file, printSerialNumbers)

def doFirstConfiguration(solarPanels: list[SolarPanel], C, L, M, N, config, output_file, printSerialNumbers):
    start_configuration = initialize_first_population(solarPanels, L, M, N)
    printConfiguration(start_configuration, C, L, M, N, config, printSerialNumbers)
    exportPanels(flatten_panels_recursively(start_configuration), output_file)
    
