import datetime
import logging
import multiprocessing
from pathlib import Path
import platform

import joblib
from SolarPanel import SolarPanel
from extractingParameters import extraction
from firstConfiguration import *
from importSolarPanels import importPanels
from exportSolarPanels import exportPanels
from geneticAlgorithm import doAlgorithm
from sharedMethods import *
import numpy as np

def main():    
    # Base directory of your project
    base_dir = Path(__file__).resolve().parent.parent

    # Define input and output files with dynamically constructed paths
    input_file = base_dir / 'longi-dataset.csv'
    output_file = base_dir / 'new_solar_panels_LONGI-10000.csv'

    starting_impp_solar_panels = base_dir / 'starting_impp_solar_panels.csv'
    starting_umpp_solar_panels = base_dir / 'starting_umpp_solar_panels.csv'
    starting_pmpp_solar_panels = base_dir / 'starting_pmpp_solar_panels.csv'
    starting_sn_solar_panels = base_dir / 'starting_sn_solar_panels.csv'
    starting_shuffle_solar_panels = base_dir / 'starting_shuffle_solar_panels.csv'

    # Step 1: Import solar panel data
    solarPanels = importPanels(str(input_file))

    # Parameters for the genetic algorithm
    population_size = 1000           # Number of configurations in each generation
    generations = 10000              # Number of generations the algorithm will run
    mutation_rate = 0.2             # Probability of mutation occurring
    L = 36                          # Number of panels in series within each substring
    M = 2                           # Number of parallel substrings
    N = 1                           # Number of series blocks
    number_of_cells = 144           # Number of cells in one panel

    # logger = logging.getLogger(__name__)
    # logging.basicConfig(filename="./results_longi-test-10000.log", encoding='utf-8', level=logging.DEBUG)
    # message = f"{datetime.datetime.now()}: Starting Logging"
    # logger.info(message)
    print("Extracting variables...")
    for i, panel in enumerate(solarPanels):
        solarPanels[i] = extraction(panel, number_of_cells)
    print("Done extracting.")
    #print("Starting algorithm...")

    doIMPPConfiguration(solarPanels, L, M, "IMPP", starting_impp_solar_panels)
    doUMPPConfiguration(solarPanels, L, M, "UMPP", starting_umpp_solar_panels)
    doPMPPConfiguration(solarPanels, L, M, "PMPP", starting_pmpp_solar_panels)
    doSNConfiguration(solarPanels, L, M, "SN", starting_sn_solar_panels)
    doSHUFFLEConfiguration(solarPanels, L, M, "SHUFFLE", starting_shuffle_solar_panels)

    sorted_solar_panels = sorted(solarPanels, key=lambda x: x.impp, reverse=True)#[5:]
    #sorted_solar_panels = sorted(sorted_solar_panels, key=lambda x: x.umpp, reverse=True)#[5:]
    # n_array = np.array(solarPanels)
    # np.random.shuffle(n_array)
    # sorted_solar_panels = list(n_array)
    # sortedGroupedPanels20 = group_panels(sorted_solar_panels, 20)
    # sortedGroupedPanels24 = group_panels(sorted_solar_panels, 24)
    # sortedGroupedPanels28 = group_panels(sorted_solar_panels, 28)
    # sortedGroupedPanels32 = group_panels(sorted_solar_panels, 32)
    # sortedGroupedPanels36 = group_panels(sorted_solar_panels, 36)
    
    # L_values = [20, 24, 28, 32, 36]
    
    # all_panel_groups = [
    #     sortedGroupedPanels20[0],
    #     sortedGroupedPanels20[1],
    #     sortedGroupedPanels24[0],
    #     sortedGroupedPanels24[1],
    #     sortedGroupedPanels28[0],
    #     sortedGroupedPanels28[1],
    #     sortedGroupedPanels32[0],
    #     sortedGroupedPanels32[1],
    #     sortedGroupedPanels36[0],
    #     sortedGroupedPanels36[1],
    # ]
    # all_missmatch_values = []
    # index = 0
    # for i, L_value in enumerate(L_values):
    #     fi = i * 2
    #     si = fi + 1
    #     avg_max = average_max_value(all_panel_groups[fi], all_panel_groups[si])
    #     missmatch_value = calculate_mismatch_loss(all_panel_groups[fi]+all_panel_groups[si], L_value, 2, avg_max)
    #     all_missmatch_values.append(missmatch_value)
        
    # print(all_missmatch_values)
    
    # plt.plot(L_values, all_missmatch_values, linewidth=2)
    # plt.title('Postotak gubitka zbog nesklada za grupe panela u seriji s dvije paralele')
    # for i, l_value in enumerate(L_values):
    #     plt.plot(l_value, all_missmatch_values[i], '.', color='gold')
    #     if (i < len(L_values)//2):
    #         x = 5
    #         y = -2
    #     else:
    #         x = -65
    #         y = -2
    #     plt.annotate(f'{all_missmatch_values[i]:.6f} %',
    #         xy=(l_value, all_missmatch_values[i]), xytext=(x, y),
    #         textcoords='offset points',
    #         fontsize=10, color='black')
    # plt.ylabel('Gubitak zbog neskalda [%]')
    # plt.xlabel('Broj panela po grupi [L]')
    # plt.grid(False)
    # plt.savefig(f'curves/Pdelta.png', dpi=300, bbox_inches='tight')
        
    
    # plt.savefig(f'curves/UICurves.png', dpi=300, bbox_inches='tight')
    
    #population = doAlgorithm(sorted_solar_panels, SortType.IMPP, population_size, generations, mutation_rate, L, M)
    # print(len(population))
    # print(len(population[0]))
    # st = time.time()
    # for _ in range(1000):
    #     lt = time.time()
    #     fitness(sortedGroupedPanels, L, M)
    #     print(time.time()-lt)
    
    # print(time.time()-st)
    #print("Sorted by new calculated current (I) ", len(sortedGroupedPanels))
    #print("Max values: [Voltage, Current, Power]")
    # for i, group in enumerate(sortedGroupedPanels):
    #     max_values = find_max_values_of_group(group)
    #     print(f"{i+1}. group: {max_values}")
    # group1 = 0
    # group2 = 1
    # print(f"groups: {group1+1}({len(sortedGroupedPanels[group1])}) & {group2+1}({len(sortedGroupedPanels[group1])})")
    # if __name__ == "__main__":
    #     fitness(sortedGroupedPanels, L, M)
    # max_values_group1 = find_max_values_of_group(sortedGroupedPanels[group1])
    # max_values_group2 = find_max_values_of_group(sortedGroupedPanels[group2])
    # print(max_values_group1, max_values_group2)
    # group_for_calc = sortedGroupedPanels[group1]+sortedGroupedPanels[group2]
    # max_values = [0.0, 0.0, 0.0]
    # max_values[0] = (max_values_group1[0] + max_values_group2[0]) / 2
    # max_values[1] = (max_values_group1[1] + max_values_group2[1]) / 2
    # max_values[2] = (max_values_group1[2] + max_values_group2[2]) / 2
    # print(f"mismatch loss of group: {calculate_mismatch_loss(
    #     group_for_calc,
    #     L, M,
    #     max_values):.9f}")
    #plotPanelGroup(1,max_values[0], max_values[1], max_values[2], sortedGroupedPanels[0])
    # #Step 2: Run the genetic algorithm to find the best configuration
    # best_configuration = doAlgorithm(
    #     solar_panels=sorted_solar_panels, 
    #     sortType=SortType.IMPP,
    #     population_size=population_size, 
    #     generations=generations, 
    #     mutation_rate=mutation_rate, 
    #     L=L, 
    #     M=M, 
    # )
    
    # # for config in ss:
    # #     for substring in config:
    # #         print(calculate_mismatch_loss(flatten_panels_recursively(substring), C, L, M, N))
    # # Step 2.5: Starting configurations sorted by parameters
    # # doSHUFFLEConfiguration(sorted_solar_panels, C, L, M, N, "shuffle", starting_shuffle_solar_panels, False)
    # # doIMPPConfiguration(sorted_solar_panels, C, L, M, N, "impp", starting_impp_solar_panels, False)
    # # doUMPPConfiguration(sorted_solar_panels, C, L, M, N, "umpp", starting_umpp_solar_panels, False)
    # # doPMPPConfiguration(sorted_solar_panels, C, L, M, N, "pmpp", starting_pmpp_solar_panels, False)


    # printConfiguration(best_configuration, C, L, M, N, "Generic Algorithm", False)
    # Step 3: Flatten the nested list of groups into a single list of SolarPanel objects
    # flattened_configuration = flatten_panels_recursively(best_configuration)

    # # # # # Step 4: Export the flattened configuration to a CSV file
    # isCreated = exportPanels(flattened_configuration, output_file)

    # # # # # Step 5: Provide feedback to the user
    # if isCreated:
    #     print(f"Best configuration saved to file: {output_file}")
    # else:
    #     print("Failed to save the configuration.")

if __name__ == "__main__":
    if platform.system() == "Windows":
        multiprocessing.freeze_support()
    main()
