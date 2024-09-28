import numpy as np
from SolarPanel import SolarPanel  # Import the SolarPanel class

def calculate_mismatch_loss(
    flattened_panels: list[SolarPanel], 
    C: float, L: int, M: int, N: int = 1
) -> float:
    """
    Calculate the mismatch loss for a single series block of solar panels.
    """
    T = L * M * N
    sigma_eta_squared_total = np.var([panel.ipv for panel in flattened_panels])
    sigma_xi_squared_total = np.var([panel.umpp for panel in flattened_panels])
    fractional_loss = (C + 2) / 2 * (
            sigma_eta_squared_total * (1 - 1 / L) 
            - (sigma_eta_squared_total - sigma_xi_squared_total)
            * ( N / T ) * (M - 1)
        )
    mismatch_loss_percentage = fractional_loss * 100
    return float(mismatch_loss_percentage)

def calculate_fill_factor(panel: SolarPanel) -> float:
    return panel.pmpp / (panel.uoc * panel.isc)

