"""Explicit screening limits. Passing these checks establishes model feasibility only."""

from dataclasses import dataclass

from .core_geometry import require_nonnegative, require_positive
from .transformer_model import DesignResult, peak_flux_density


@dataclass(frozen=True)
class DesignLimits:
    peak_flux_density_t: float
    maximum_supply_rms_v: float
    minimum_frequency_hz: float
    maximum_fill_fraction: float
    ideal_voltage_tolerance_fraction: float
    loaded_voltage_tolerance_fraction: float
    maximum_current_density_a_m2: float

    def __post_init__(self) -> None:
        require_positive(
            peak_flux_density_t=self.peak_flux_density_t,
            maximum_supply_rms_v=self.maximum_supply_rms_v,
            minimum_frequency_hz=self.minimum_frequency_hz,
            maximum_fill_fraction=self.maximum_fill_fraction,
            maximum_current_density_a_m2=self.maximum_current_density_a_m2,
        )
        require_nonnegative(
            ideal_voltage_tolerance_fraction=self.ideal_voltage_tolerance_fraction,
            loaded_voltage_tolerance_fraction=self.loaded_voltage_tolerance_fraction,
        )
        if self.maximum_fill_fraction > 1 or max(
            self.ideal_voltage_tolerance_fraction, self.loaded_voltage_tolerance_fraction
        ) >= 1:
            raise ValueError("Check fill and voltage tolerance fractions")


@dataclass(frozen=True)
class ConstraintCheck:
    name: str
    value: float
    limit: float
    unit: str

    @property
    def passed(self) -> bool:
        return self.value <= self.limit


def check_design(result: DesignResult, limits: DesignLimits) -> tuple[ConstraintCheck, ...]:
    """Check an evaluated point without changing its currents, ratio or losses."""
    spec = result.spec
    if limits.maximum_supply_rms_v < spec.primary_rms_v or limits.minimum_frequency_hz > spec.frequency_hz:
        raise ValueError("The flux screening envelope must include the nominal supply and frequency")
    worst_flux = peak_flux_density(limits.maximum_supply_rms_v, limits.minimum_frequency_hz,
                                   result.primary.turns, result.core.effective_area_m2)
    ideal_error = abs(result.ideal_secondary_rms_v / spec.secondary_target_rms_v - 1)
    loaded_error = abs(result.load.secondary_terminal_rms_v / spec.secondary_target_rms_v - 1)
    return (
        ConstraintCheck("Peak flux at screening envelope", worst_flux, limits.peak_flux_density_t, "T"),
        ConstraintCheck("Bare-copper window fill", result.bare_copper_fill, limits.maximum_fill_fraction, "fraction"),
        ConstraintCheck("Insulated radial build", result.required_radial_build_m, result.usable_width_m, "m"),
        ConstraintCheck("Ideal secondary voltage error", ideal_error, limits.ideal_voltage_tolerance_fraction, "fraction"),
        ConstraintCheck("Loaded secondary voltage error", loaded_error, limits.loaded_voltage_tolerance_fraction, "fraction"),
        ConstraintCheck("Primary current density", result.load.primary_rms_a / result.primary.conductor_area_m2,
                        limits.maximum_current_density_a_m2, "A/m²"),
        ConstraintCheck("Secondary current density", result.load.secondary_rms_a / result.secondary.conductor_area_m2,
                        limits.maximum_current_density_a_m2, "A/m²"),
    )
