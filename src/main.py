import datetime
import logging
import multiprocessing
from pathlib import Path
import platform
from SolarPanel import SolarPanel
from extractingParameters import extraction
from firstConfiguration import *
from importSolarPanels import importPanels
from exportSolarPanels import exportPanels
from geneticAlgorithm import doAlgorithm
import numpy as np

def main():
    # Define input and output files with dynamically constructed paths
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename="./results_longi-test-10000.log", 
        encoding='utf-8', level=logging.DEBUG)
    message = f"{datetime.datetime.now()}: Starting Logging"
    logger.info(message)
    if platform.system() == "Windows":
        base_dir = Path(__file__).resolve().parent.parent
        input_file = base_dir / 'longi-dataset.csv'
        output_file = base_dir / 'new_solar_panels_LONGI-10000.csv'
    else:
        input_file = 'longi-dataset.csv'
        output_file = 'new_solar_panels_LONGI-10000.csv'

    # Step 1: Import solar panel data
    solarPanels = importPanels(str(input_file))
    # Parameters for the genetic algorithm
    population_size = 1000              # Number of configurations in each generation
    generations = 10000                 # Number of generations the algorithm will run
    mutation_rate = 0.2                 # Probability of mutation occurring
    number_of_cells = 144               # Number of cells in one panel
    L = 36                              # Number of panels in series within each substring
    M = 2                               # Number of parallel substrings
    
    #Step 2: Extracting and aproximating panel characteristics
    print("Extracting variables...")
    for i, panel in enumerate(solarPanels):
        solarPanels[i] = extraction(panel, number_of_cells)
    print("Done extracting.")
    sorted_solar_panels = sorted(solarPanels, key=lambda x: x.impp, reverse=True)
    
    # #Step 3: Run the genetic algorithm to find the best configuration
    print("Starting algorithm...")
    best_configuration = doAlgorithm(
        solar_panels=sorted_solar_panels,
        sortType=SortType.IMPP,
        population_size=population_size,
        generations=generations,
        mutation_rate=mutation_rate, 
        L=L, M=M)
    # Step 4: Export the flattened configuration to a CSV file
    flattened_configuration = flatten_panels_recursively(best_configuration)
    isCreated = exportPanels(flattened_configuration, output_file)
    #Step 5: Provide feedback to the user
    if isCreated:
        print(f"Best configuration saved to file: {output_file}")
    else:
        print("Failed to save the configuration.")

if __name__ == "__main__":
    if platform.system() == "Windows":
        multiprocessing.freeze_support()
    main()