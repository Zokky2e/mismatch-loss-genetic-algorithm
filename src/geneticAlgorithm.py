import datetime
import logging
import numpy as np
import random
from joblib import Parallel, delayed
from typing import List
from SolarPanel import SolarPanel
from exportSolarPanels import exportPanels
from sharedMethods import SortType
from mismatchCalculations import *
from sharedMethods import *

def fitness(configuration: list[list[SolarPanel]], L: int, M: int) -> float:
    """
    Calculate the fitness of the configuration based on minimizing mismatch losses.
    """
    total_loss = 0.0
    index = 0
    while (index+1 < len(configuration)):
        g1 = configuration[index]
        g2 = configuration[index+1]
        avg_max_values = average_max_value(g1, g2)
        flattened_group1 = flatten_panels_recursively(g1)
        flattened_group2 = flatten_panels_recursively(g2)
        flattened_group = flattened_group1 + flattened_group2
        group_loss = calculate_mismatch_loss(flattened_group, L, M, avg_max_values)
        total_loss += group_loss
        index += 2
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
    L: int, M: int, population_size: int,
    sortType: SortType
) -> list[list[list[SolarPanel]]]:
    """
    Create a population of random configurations. Each configuration consists of N series blocks,
    each containing M parallel substrings, and each substring has L panels in series.
    """
    population = []
    panels_per_configuration = L * M
    configurations_per_set = len(solar_panels) // panels_per_configuration
    for _ in range(population_size):
        copied_panels = shuffleArray(solar_panels.copy(), sortType)
        configuration = group_panels(copied_panels, L)
        np_array = np.array(configuration)
        np.random.shuffle(np_array)
        configuration = list(np_array)
        for i, _ in enumerate(configuration):
            configuration[i] = list(configuration[i])
        population.append(configuration)
    return population

def selection(
    population: list[list[list[SolarPanel]]], 
    L: int, M: int
) -> list[list[list[SolarPanel]]]:
    """
    Select the top sets of configurations based on their fitness score.
    Each set uses all the solar panels.
    """
    # Parallel execution of fitness calculation
    fitness_scores = Parallel(n_jobs=-1, backend="loky")(
        delayed(fitness)(config, L, M) for config in population
    )
    # Combine fitness with the population for sorting
    population_with_fitness: List = list(zip(fitness_scores, population))
    population_with_fitness.sort(key=lambda x: x[0], reverse=True)
    
    retain_length = len(population) // 2
    selected_population = [x[1] for x in population_with_fitness[:retain_length]]
    return selected_population

def crossover(
    all_panels: list[SolarPanel],
    parent1: list[list[SolarPanel]], 
    parent2: list[list[SolarPanel]],
    L: int, M: int, configurations_per_set: int
) -> list[list[SolarPanel]]:
    """
    Perform crossover between two parent sets to produce a child set.
    Ensures no duplicate panels across the child set.
    Handles cases where we run out of panels by discarding incomplete configurations.
    """
    crossover_point = np.random.randint(1, configurations_per_set-1)
    child_set = parent1[:crossover_point] + parent2[crossover_point:]
    child_set_panels = flatten_panels_recursively(child_set)
    used_serial_numbers = {panel.serialnumber for panel in child_set_panels}
    missing_panels = [panel for panel in all_panels if panel.serialnumber not in used_serial_numbers]
    required_panels = L * len(child_set)
    total_panels = len(all_panels)
    if total_panels < required_panels:
        full_configs_possible = total_panels // L
        child_set = child_set[:full_configs_possible]
    
    for panel in missing_panels:
        added = False
        for substring in child_set:
            if len(substring) < L:
                substring.append(panel)
                added = True
                break
            if added:
                break
    child_set_panels = flatten_panels_recursively(child_set)
    used_serial_numbers = {panel.serialnumber for panel in child_set_panels}
    missing_panels = [panel for panel in all_panels if panel.serialnumber not in used_serial_numbers]
    child_set_panels = swap_duplicate(child_set_panels, missing_panels)
    return group_panels(child_set_panels, L)

def mutate(
    configurations: list[list[SolarPanel]], 
    mutation_rate: float, L: int, M: int
) -> list[list[SolarPanel]]:
    """
    Mutate a set of configurations by swapping panels within substrings our within groups.
    Ensures no duplicate panels within the set.
    """
    all_panels = flatten_panels_recursively(configurations)
    if np.random.rand() < mutation_rate:
        i, j = np.random.choice(len(all_panels), 2, replace=False)
        all_panels[i], all_panels[j] = all_panels[j], all_panels[i]
    return group_panels(all_panels, L)

def doAlgorithm(
    solar_panels: list[SolarPanel], 
    sortType: SortType = SortType.SHUFFLE,
    population_size: int = 50, 
    generations: int = 100, 
    mutation_rate: float = 0.05, 
    L: int = 20, 
    M: int = 2
):
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename="./results_longi-test-10000.log", encoding='utf-8', level=logging.DEBUG)
    configurations_per_set = len(solar_panels) // L
    population = initialize_population(solar_panels, L, M, population_size, sortType)
    top_sets = []   
    for generation in range(generations):
        g = f"{datetime.datetime.now()}: Generation {generation + 1}"
        logger.debug(g)
        population = selection(population, L, M)
        offspring = []
        while len(offspring) <= population_size - len(population):
            parent1, parent2 = random.sample(population, 2)
            child = crossover(solar_panels, parent1, parent2, L, M, configurations_per_set)   
            child = mutate(child, mutation_rate, L, M)
            offspring.append(child)
        population.extend(offspring)
        if len(population) > population_size:
            population = population[:population_size]
        top_sets.extend(population)
        top_sets = sorted(population, key=lambda config: fitness(config, L, M), reverse=True)[:10]
        total_loss = 0.0  
        index = 0
        if (generation%10 == 0):
            print(len(flatten_panels_recursively(top_sets[0])))
            while (index+1< len(top_sets[0])):
                g1 = top_sets[0][index]
                g2 = top_sets[0][index+1]
                avg_max_values = average_max_value(g1, g2)
                flattened_group1 = flatten_panels_recursively(g1)
                flattened_group2 = flatten_panels_recursively(g2)
                flattened_group = flattened_group1 + flattened_group2
                #group_loss = calculate_mismatch_loss(flattened_group, L, M)
                group_loss = calculate_mismatch_loss(flattened_group, L, M, avg_max_values)
                total_loss += group_loss
                index += 2
            result = f"{datetime.datetime.now()} Lowest mismatch = {total_loss:.8f}"
            logger.debug(result)
            print(result)
    winner = max(top_sets, key=lambda config: fitness(config, L, M))
    dup = has_duplicate_panels(flatten_panels_recursively(winner))
    print(f"Winner has {dup} duplicates.")
    return population

