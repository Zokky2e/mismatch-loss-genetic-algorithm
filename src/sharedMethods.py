from enum import Enum
from SolarPanel import SolarPanel

#Types of sort in genetic algorthim
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
        if isinstance(item, list):
            flat_list.extend(flatten_panels_recursively(item))
        elif isinstance(item, SolarPanel):
            flat_list.append(item)
        else:
            print(f"Error: Found a non-SolarPanel object: {type(item)}")
    return flat_list

def reconstruct_configuration(flattened_list: list[SolarPanel], L: int, M: int, N: int) -> list[list[list[SolarPanel]]]:
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

