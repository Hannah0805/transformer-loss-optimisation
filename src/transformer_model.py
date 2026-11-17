"""Steady-state sinusoidal transformer model with DC winding resistance."""

from dataclasses import dataclass
from math import floor, pi, sqrt

from .core_geometry import (
    EICore, WindowClearances, WindingLayout, require_nonnegative, require_positive,
    require_turns, winding_layout,
)
from .material_models import Copper, HysteresisScenario, LaminatedSteel


def ideal_secondary_voltage(primary_rms_v: float, primary_turns: int, secondary_turns: int) -> float:
    require_positive(primary_rms_v=primary_rms_v)
    require_turns(primary_turns)
    require_turns(secondary_turns)
    return primary_rms_v * secondary_turns / primary_turns


def nearest_secondary_turns(primary_rms_v: float, target_rms_v: float, primary_turns: int) -> int:
    require_positive(primary_rms_v=primary_rms_v, target_rms_v=target_rms_v)
    require_turns(primary_turns)
    return max(1, floor(primary_turns * target_rms_v / primary_rms_v + 0.5))


def peak_flux_density(induced_rms_v: float, frequency_hz: float, turns: int, area_m2: float) -> float:
    require_nonnegative(induced_rms_v=induced_rms_v)
    require_positive(frequency_hz=frequency_hz, area_m2=area_m2)
    require_turns(turns)
    return induced_rms_v / (sqrt(2) * pi * frequency_hz * turns * area_m2)


@dataclass(frozen=True)
class ElectricalSpec:
    primary_rms_v: float
    secondary_target_rms_v: float
    frequency_hz: float
    rated_va: float

    def __post_init__(self) -> None:
        require_positive(**vars(self))

    @property
    def primary_reference_a(self) -> float:
        return self.rated_va / self.primary_rms_v

    @property
    def secondary_reference_a(self) -> float:
        return self.rated_va / self.secondary_target_rms_v


@dataclass(frozen=True)
class Winding:
    turns: int
    bare_diameter_m: float
    insulated_diameter_m: float
    lead_length_m: float
    temperature_c: float

    def __post_init__(self) -> None:
        require_turns(self.turns)
        require_positive(bare_diameter_m=self.bare_diameter_m)
        require_nonnegative(lead_length_m=self.lead_length_m)
        if self.insulated_diameter_m < self.bare_diameter_m:
            raise ValueError("Insulated diameter must be at least the bare diameter")
        require_positive(insulated_diameter_m=self.insulated_diameter_m)

    @property
    def conductor_area_m2(self) -> float:
        return pi * self.bare_diameter_m**2 / 4

    def resistance_ohm(self, copper: Copper, mean_turn_length_m: float) -> float:
        require_positive(mean_turn_length_m=mean_turn_length_m)
        length = self.turns * mean_turn_length_m + self.lead_length_m
        return copper.resistivity_ohm_m(self.temperature_c) * length / self.conductor_area_m2


@dataclass(frozen=True)
class LoadPoint:
    primary_rms_a: float
    secondary_rms_a: float
    primary_induced_rms_v: float
    secondary_terminal_rms_v: float
    delivered_va: float


def resistive_load_point(
    spec: ElectricalSpec,
    turns_ratio: float,
    primary_ohm: float,
    secondary_ohm: float,
    *,
    fixed_va: bool = False,
) -> LoadPoint:
    """Predict a unity-PF operating point, omitting excitation and leakage."""
    require_positive(turns_ratio=turns_ratio)
    require_nonnegative(primary_ohm=primary_ohm, secondary_ohm=secondary_ohm)
    no_load_v = spec.primary_rms_v * turns_ratio
    equivalent_ohm = secondary_ohm + turns_ratio**2 * primary_ohm
    if fixed_va:
        discriminant = no_load_v**2 - 4 * equivalent_ohm * spec.rated_va
        if discriminant < 0:
            raise ValueError("No real resistive operating point at the requested apparent power")
        high_voltage_v = (no_load_v + sqrt(discriminant)) / 2
        secondary_a = spec.rated_va / high_voltage_v
    else:
        secondary_a = spec.secondary_reference_a
    secondary_v = no_load_v - secondary_a * equivalent_ohm
    if secondary_v <= 0:
        raise ValueError("Requested current has no positive terminal voltage")
    primary_a = secondary_a * turns_ratio
    primary_induced_v = spec.primary_rms_v - primary_a * primary_ohm
    return LoadPoint(primary_a, secondary_a, primary_induced_v, secondary_v, secondary_v * secondary_a)


@dataclass(frozen=True)
class DesignResult:
    spec: ElectricalSpec
    core: EICore
    primary: Winding
    secondary: Winding
    primary_layout: WindingLayout
    secondary_layout: WindingLayout
    primary_ohm: float
    secondary_ohm: float
    usable_window_m2: float
    usable_width_m: float
    required_radial_build_m: float
    ideal_secondary_rms_v: float
    no_drop_peak_t: float
    loaded_peak_t: float
    load: LoadPoint
    core_mass_kg: float
    primary_copper_w: float
    secondary_copper_w: float
    classical_w: float
    hysteresis: HysteresisScenario | None
    hysteresis_w: float | None

    @property
    def copper_w(self) -> float:
        return self.primary_copper_w + self.secondary_copper_w

    @property
    def separated_total_w(self) -> float | None:
        if self.hysteresis_w is None:
            return None
        return self.copper_w + self.classical_w + self.hysteresis_w

    @property
    def bare_copper_fill(self) -> float:
        occupied = (
            self.primary.turns * self.primary.conductor_area_m2
            + self.secondary.turns * self.secondary.conductor_area_m2
        )
        return occupied / self.usable_window_m2


def evaluate_design(
    spec: ElectricalSpec,
    core: EICore,
    clearances: WindowClearances,
    primary: Winding,
    secondary: Winding,
    copper: Copper,
    steel: LaminatedSteel,
    hysteresis: HysteresisScenario | None = None,
    *,
    fixed_va: bool = False,
) -> DesignResult:
    """Evaluate a specified winding pair under the requested electrical convention."""
    height, width = clearances.usable_dimensions(core)
    p_layout = winding_layout(core, primary.turns, primary.insulated_diameter_m,
                              height, clearances.former_wall_m)
    s_offset = clearances.former_wall_m + p_layout.radial_build_m + clearances.winding_barrier_m
    s_layout = winding_layout(core, secondary.turns, secondary.insulated_diameter_m, height, s_offset)
    primary_ohm = primary.resistance_ohm(copper, p_layout.mean_turn_length_m)
    secondary_ohm = secondary.resistance_ohm(copper, s_layout.mean_turn_length_m)
    load = resistive_load_point(spec, secondary.turns / primary.turns,
                                primary_ohm, secondary_ohm, fixed_va=fixed_va)
    no_drop_peak = peak_flux_density(spec.primary_rms_v, spec.frequency_hz,
                                    primary.turns, core.effective_area_m2)
    loaded_peak = peak_flux_density(load.primary_induced_rms_v, spec.frequency_hz,
                                   primary.turns, core.effective_area_m2)
    mass = core.steel_mass_kg(steel.density_kg_m3)
    hysteresis_w = None
    if hysteresis is not None and hysteresis.contains(loaded_peak):
        hysteresis_w = mass * hysteresis.specific_loss_w_kg(spec.frequency_hz, loaded_peak)
    return DesignResult(
        spec=spec, core=core, primary=primary, secondary=secondary,
        primary_layout=p_layout, secondary_layout=s_layout,
        primary_ohm=primary_ohm, secondary_ohm=secondary_ohm,
        usable_window_m2=height * width, usable_width_m=width,
        required_radial_build_m=(p_layout.radial_build_m + clearances.winding_barrier_m
                                 + s_layout.radial_build_m),
        ideal_secondary_rms_v=ideal_secondary_voltage(spec.primary_rms_v, primary.turns, secondary.turns),
        no_drop_peak_t=no_drop_peak, loaded_peak_t=loaded_peak, load=load, core_mass_kg=mass,
        primary_copper_w=load.primary_rms_a**2 * primary_ohm,
        secondary_copper_w=load.secondary_rms_a**2 * secondary_ohm,
        classical_w=mass * steel.classical_loss_w_kg(spec.frequency_hz, loaded_peak),
        hysteresis=hysteresis, hysteresis_w=hysteresis_w,
    )
