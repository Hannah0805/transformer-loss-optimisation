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


@dataclass(frozen=True)
class HysteresisScenario:
    """An explicitly labelled power law for quasi-static energy per unit mass."""

    label: str
    reference_energy_j_kg: float
    reference_flux_density_t: float
    exponent: float
    min_flux_density_t: float
    max_flux_density_t: float

    def __post_init__(self) -> None:
        if not self.label.strip():
            raise ValueError("Provide a provenance label for the hysteresis scenario")
        require_nonnegative(reference_energy_j_kg=self.reference_energy_j_kg,
                            min_flux_density_t=self.min_flux_density_t)
        require_positive(reference_flux_density_t=self.reference_flux_density_t,
                         exponent=self.exponent, max_flux_density_t=self.max_flux_density_t)
        if not self.contains(self.reference_flux_density_t):
            raise ValueError("Reference flux density must lie in the scenario range")

    def contains(self, peak_flux_density_t: float) -> bool:
        return self.min_flux_density_t <= peak_flux_density_t <= self.max_flux_density_t

    def specific_loss_w_kg(self, frequency_hz: float, peak_flux_density_t: float) -> float:
        require_positive(frequency_hz=frequency_hz)
        if not self.contains(peak_flux_density_t):
            raise ValueError("Peak flux density outside the hysteresis scenario range")
        ratio = peak_flux_density_t / self.reference_flux_density_t
        return frequency_hz * self.reference_energy_j_kg * ratio**self.exponent
