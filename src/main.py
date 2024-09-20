from pathlib import Path
from SolarPanel import SolarPanel
from firstConfiguration import *
from importSolarPanels import importPanels
from exportSolarPanels import exportPanels
from geneticAlgorithm import doAlgorithm
from sharedMethods import *

# Base directory of your project
base_dir = Path(__file__).resolve().parent.parent

# Define input and output files with dynamically constructed paths
input_file = base_dir / 'dataset.csv'
output_file = base_dir / 'new_solar_panels.csv'
starting_impp_solar_panels = base_dir / 'starting_impp_solar_panels.csv'
starting_umpp_solar_panels = base_dir / 'starting_umpp_solar_panels.csv'
starting_pmpp_solar_panels = base_dir / 'starting_pmpp_solar_panels.csv'

# Step 1: Import solar panel data
solarPanels = importPanels(str(input_file))

# Parameters for the genetic algorithm
population_size = 2000       # Number of configurations in each generation
generations = 2000           # Number of generations the algorithm will run
mutation_rate = 0.25        # Probability of mutation occurring
C = 11.8                    # Characteristic parameter related to the fill factor (FF) of the cells
L = 18                      # Number of panels in series within each substring
M = 2                       # Number of parallel substrings
N = 2                       # Number of series blocks

#Step 2: Run the genetic algorithm to find the best configuration
best_configuration = doAlgorithm(
    solar_panels=solarPanels, 
    sortType=SortType.SHUFFLE,
    population_size=population_size, 
    generations=generations, 
    mutation_rate=mutation_rate, 
    C=C, 
    L=L, 
    M=M, 
    N=N
)
# Step 1.5: Starting configurations sorted by parameters
doIMPPConfiguration(solarPanels, C, L, M, N, "impp", starting_impp_solar_panels, False)
doUMPPConfiguration(solarPanels, C, L, M, N, "umpp", starting_umpp_solar_panels, False)
doPMPPConfiguration(solarPanels, C, L, M, N, "pmpp", starting_pmpp_solar_panels, False)


printConfiguration(best_configuration, C, L, M, N, "Generic Algorithm", False)
# Step 3: Flatten the nested list of groups into a single list of SolarPanel objects
flattened_configuration = flatten_panels_recursively(best_configuration)

# Step 4: Export the flattened configuration to a CSV file
isCreated = exportPanels(flattened_configuration, output_file)

# Step 5: Provide feedback to the user
if isCreated:
    print(f"Best configuration saved to file: {output_file}")
else:
    print("Failed to save the configuration.")
