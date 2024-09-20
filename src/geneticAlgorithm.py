import numpy as np
import random
from SolarPanel import SolarPanel
from exportSolarPanels import exportPanels
from sharedMethods import SortType
from mismatchCalculations import *
from sharedMethods import *

def fitness(configuration: list[list[list[SolarPanel]]], C: float, L: int, M: int) -> float:
    """
    Calculate the fitness of the configuration based on minimizing mismatch losses.
    """
    total_loss = 0.0
    for series_block in configuration:
        for substring in series_block:
            flattened_substring = flatten_panels_recursively(substring)
            block_loss = calculate_mismatch_loss(flattened_substring, C, L, M, 1)  # N = 1 because we calculate per block
            total_loss += block_loss
    fitness_score = 1 / (total_loss + 1e-6)  # Adding a small value to prevent division by zero
    return float(fitness_score)

def shuffleArray(array: list[SolarPanel], sortType: SortType) -> list[SolarPanel]:
    """
    Randomly shuffle the array of SolarPanel objects using numpy.
    """
    np_array = np.array(array)
    match sortType:
        case SortType.SHUFFLE:
            np.random.shuffle(np_array)
        case SortType.IMPP:
            np_array = sorted(np_array.copy(), key=lambda x: x.impp, reverse=True)
        case SortType.UMPP:
            np_array = sorted(np_array.copy(), key=lambda x: x.umpp, reverse=True)
        case SortType.PMPP:
            np_array = sorted(np_array.copy(), key=lambda x: x.pmpp, reverse=True)
    return list(np_array)

def initialize_population(
    solar_panels: list[SolarPanel], 
    L: int, M: int, N: int, population_size: int,
    sortType: SortType
) -> list[list[list[list[SolarPanel]]]]:
    """
    Create a population of random configurations. Each configuration consists of N series blocks,
    each containing M parallel substrings, and each substring has L panels in series.
    """
    population = []
    panels_per_configuration = L * M * N
    configurations_per_set = len(solar_panels) // panels_per_configuration
    for _ in range(population_size):
        copied_panels = shuffleArray(solar_panels.copy(), sortType)
        configuration = []
        for _ in range(configurations_per_set):
            single_configuration = []
            for _ in range(N):
                series_block = []
                for _ in range(M):
                    substring = copied_panels[:L]
                    copied_panels = copied_panels[L:]
                    series_block.append(substring)
                single_configuration.append(series_block)
            configuration.append(single_configuration)
        population.append(configuration)
    return population

def selection(
    population: list[list[list[list[SolarPanel]]]], 
    C: float, L: int, M: int, N: int
) -> list[list[list[list[SolarPanel]]]]:
    """
    Select the top sets of configurations based on their fitness score.
    Each set uses all the solar panels.
    """
    sorted_population = sorted(population, key=lambda config: fitness(config, C, L, M), reverse=True)
    retain_length = len(population) // 2
    selected_population = sorted_population[:retain_length]
    return selected_population

def crossover(
    all_panels: list[SolarPanel],
    parent1: list[list[list[SolarPanel]]], 
    parent2: list[list[list[SolarPanel]]],
    L: int, M: int, N: int, configurations_per_set: int
) -> list[list[list[SolarPanel]]]:
    """
    Perform crossover between two parent sets to produce a child set.
    Ensures no duplicate panels across the child set.
    Handles cases where we run out of panels by discarding incomplete configurations.
    """
    crossover_point = np.random.randint(1, configurations_per_set)
    child_set = parent1[:crossover_point] + parent2[crossover_point:]

    child_set_panels = flatten_panels_recursively(child_set)
    used_serial_numbers = {panel.serialnumber for panel in child_set_panels}
    missing_panels = [panel for panel in all_panels if panel.serialnumber not in used_serial_numbers]
    required_panels = L * M * N * len(child_set)
    total_panels = len(all_panels)
    if total_panels < required_panels:
        full_configs_possible = total_panels // (L * M * N)
        child_set = child_set[:full_configs_possible]
    for panel in missing_panels:
        added = False
        for config in child_set:
            for series_block in config:
                for substring in series_block:
                    if isinstance(substring, list) and len(substring) < L:
                        substring.append(panel)
                        added = True
                        break
                if added:
                    break
            if added:
                break
    child_set_panels = flatten_panels_recursively(child_set)
    used_serial_numbers = {panel.serialnumber for panel in child_set_panels}
    missing_panels = [panel for panel in all_panels if panel.serialnumber not in used_serial_numbers]
    child_set_panels = swap_duplicate(child_set_panels, missing_panels)
    return reconstruct_configuration(child_set_panels, L, M, N)

def mutate(
    configurations: list[list[list[SolarPanel]]], 
    mutation_rate: float, L: int, M: int, N: int
) -> list[list[list[SolarPanel]]]:
    """
    Mutate a set of configurations by swapping panels within substrings our within groups.
    Ensures no duplicate panels within the set.
    """
    all_panels = flatten_panels_recursively(configurations)
    if np.random.rand() < mutation_rate:
        i, j = np.random.choice(len(all_panels), 2, replace=False)
        all_panels[i], all_panels[j] = all_panels[j], all_panels[i]
    return reconstruct_configuration(all_panels, L, M, N)

def doAlgorithm(
    solar_panels: list[SolarPanel], 
    sortType: SortType = SortType.SHUFFLE,
    population_size: int = 50, 
    generations: int = 100, 
    mutation_rate: float = 0.05, 
    L: int = 18, 
    M: int = 2, 
    N: int = 2, 
    C: float = 1.0
):
    configurations_per_set = len(solar_panels) // (L * M * N)
    population = initialize_population(solar_panels, L, M, N, population_size, sortType)
    top_sets = []   
    for generation in range(generations):
        population = selection(population, C, L, M, N)
        offspring = []
        while len(offspring) <= population_size - len(population):
            parent1, parent2 = random.sample(population, 2)
            child = crossover(solar_panels, parent1, parent2, L, M, N, configurations_per_set)       
            child = mutate(child, mutation_rate, L, M, N)
            offspring.append(child)
        population.extend(offspring)
        if len(population) > population_size:
            population = population[:population_size]
        top_sets.extend(population)
        top_sets = sorted(population, key=lambda config: fitness(config, C, L, M), reverse=True)[:10]
        total_loss = 0.0  
        for series_block in top_sets[0]:
            for substring in series_block:
                flattened_substring = flatten_panels_recursively(substring)
                block_loss = calculate_mismatch_loss(flattened_substring, C, L, M, 1)
                total_loss += block_loss
        print(f"Generation {generation + 1}: Lowest mismatch = {round(total_loss, 4)}")
    winner = max(top_sets, key=lambda config: fitness(config, C, L, M))
    dup = has_duplicate_panels(flatten_panels_recursively(winner))
    print(f"Winner has {dup} duplicates.")
    return winner

