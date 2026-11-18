"""Copper and separated electrical-steel material equations, in SI."""

from dataclasses import dataclass
from math import isfinite, pi

from .core_geometry import require_nonnegative, require_positive


@dataclass(frozen=True)
class Copper:
    resistivity_20_ohm_m: float
    resistance_coefficient_per_k: float

    def __post_init__(self) -> None:
        require_positive(**vars(self))

    def resistivity_ohm_m(self, temperature_c: float) -> float:
        if not isfinite(temperature_c) or temperature_c <= -273.15:
            raise ValueError("Temperature must be finite and above absolute zero")
        factor = 1 + self.resistance_coefficient_per_k * (temperature_c - 20)
        require_positive(resistance_temperature_factor=factor)
        return self.resistivity_20_ohm_m * factor


@dataclass(frozen=True)
class LaminatedSteel:
    sheet_thickness_m: float
    electrical_resistivity_ohm_m: float
    density_kg_m3: float

    def __post_init__(self) -> None:
        require_positive(**vars(self))

    def classical_loss_w_m3(self, frequency_hz: float, peak_flux_density_t: float) -> float:
        require_positive(frequency_hz=frequency_hz)
        require_nonnegative(peak_flux_density_t=peak_flux_density_t)
        numerator = pi**2 * (self.sheet_thickness_m * frequency_hz * peak_flux_density_t)**2
        return numerator / (6 * self.electrical_resistivity_ohm_m)

    def classical_loss_w_kg(self, frequency_hz: float, peak_flux_density_t: float) -> float:
        return self.classical_loss_w_m3(frequency_hz, peak_flux_density_t) / self.density_kg_m3
