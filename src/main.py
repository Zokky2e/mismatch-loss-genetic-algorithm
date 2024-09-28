from pathlib import Path
from SolarPanel import SolarPanel
from extractingParameters import extraction
from firstConfiguration import *
from importSolarPanels import importPanels
from exportSolarPanels import exportPanels
from geneticAlgorithm import doAlgorithm
from sharedMethods import *

# Base directory of your project
base_dir = Path(__file__).resolve().parent.parent

# Define input and output files with dynamically constructed paths
input_file = base_dir / 'dataset_new.csv'
output_file = base_dir / 'new_solar_panels.csv'

starting_impp_solar_panels = base_dir / 'starting_impp_solar_panels.csv'
starting_umpp_solar_panels = base_dir / 'starting_umpp_solar_panels.csv'
starting_pmpp_solar_panels = base_dir / 'starting_pmpp_solar_panels.csv'
starting_shuffle_solar_panels = base_dir / 'starting_shuffle_solar_panels.csv'

# Step 1: Import solar panel data
solarPanels = importPanels(str(input_file))
sorted_solar_panels = sorted(solarPanels, key=lambda x: x.impp, reverse=True)[5:]

# Parameters for the genetic algorithm
population_size = 200       # Number of configurations in each generation
generations = 100          # Number of generations the algorithm will run
mutation_rate = 0.05        # Probability of mutation occurring
C = 11.8                    # Characteristic parameter related to the fill factor (FF) of the cells
L = 20                      # Number of panels in series within each substring
M = 2                       # Number of parallel substrings
N = 1                       # Number of series blocks
number_of_cells = 60        # Number of cells in one panel

print("Extracting variables...")
for i, panel in enumerate(sorted_solar_panels):
    sorted_solar_panels[i] = extraction(panel, number_of_cells)

#Step 2: Run the genetic algorithm to find the best configuration
best_configuration = doAlgorithm(
    solar_panels=sorted_solar_panels, 
    sortType=SortType.IMPP,
    population_size=population_size, 
    generations=generations, 
    mutation_rate=mutation_rate, 
    C=C, 
    L=L, 
    M=M, 
    N=N
)

# ss = reconstruct_configuration(solarPanels, L, M, N)
# for config in ss:
#     for substring in config:
#         print(calculate_mismatch_loss(flatten_panels_recursively(substring), C, L, M, N))
# Step 2.5: Starting configurations sorted by parameters
# doSHUFFLEConfiguration(sorted_solar_panels, C, L, M, N, "shuffle", starting_shuffle_solar_panels, False)
# doIMPPConfiguration(sorted_solar_panels, C, L, M, N, "impp", starting_impp_solar_panels, False)
# doUMPPConfiguration(sorted_solar_panels, C, L, M, N, "umpp", starting_umpp_solar_panels, False)
# doPMPPConfiguration(sorted_solar_panels, C, L, M, N, "pmpp", starting_pmpp_solar_panels, False)


printConfiguration(best_configuration, C, L, M, N, "Generic Algorithm", False)
# # Step 3: Flatten the nested list of groups into a single list of SolarPanel objects
flattened_configuration = flatten_panels_recursively(best_configuration)

# # Step 4: Export the flattened configuration to a CSV file
isCreated = exportPanels(flattened_configuration, output_file)

# # Step 5: Provide feedback to the user
if isCreated:
    print(f"Best configuration saved to file: {output_file}")
else:
    print("Failed to save the configuration.")
