"""Idealised symmetric E–I laminations and concentric rectangular windings, in SI."""

from dataclasses import dataclass
from math import floor, inf, isfinite, nextafter


def require_positive(**values: float) -> None:
    for name, value in values.items():
        if not isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be finite and positive")


def require_nonnegative(**values: float) -> None:
    for name, value in values.items():
        if not isfinite(value) or value < 0:
            raise ValueError(f"{name} must be finite and nonnegative")


def require_turns(turns: int) -> None:
    if type(turns) is not int or turns < 1:
        raise ValueError("Turns must be a positive integer")


@dataclass(frozen=True)
class EICore:
    centre_width_m: float
    stack_depth_m: float
    window_width_m: float
    window_height_m: float
    stacking_factor: float

    def __post_init__(self) -> None:
        require_positive(**vars(self))
        if self.stacking_factor > 1:
            raise ValueError("Stacking factor must be at most one")

    @property
    def effective_area_m2(self) -> float:
        return self.stacking_factor * self.centre_width_m * self.stack_depth_m

    @property
    def magnetic_path_m(self) -> float:
        """Centreline length of one loop through the centre limb and one return."""
        return (
            2 * self.window_height_m
            + 2 * self.window_width_m
            + 2.5 * self.centre_width_m
        )

    @property
    def steel_volume_m3(self) -> float:
        """Lamination footprint times equivalent solid steel stack depth."""
        return 2 * self.effective_area_m2 * (
            self.window_height_m + self.window_width_m + self.centre_width_m
        )

    def steel_mass_kg(self, density_kg_m3: float) -> float:
        require_positive(density_kg_m3=density_kg_m3)
        return self.steel_volume_m3 * density_kg_m3

    def with_effective_area(self, area_m2: float) -> "EICore":
        """Scale all linear dimensions at fixed proportions and stack factor."""
        require_positive(area_m2=area_m2)
        scale = (area_m2 / self.effective_area_m2) ** 0.5
        return EICore(
            self.centre_width_m * scale,
            self.stack_depth_m * scale,
            self.window_width_m * scale,
            self.window_height_m * scale,
            self.stacking_factor,
        )


@dataclass(frozen=True)
class WindowClearances:
    former_wall_m: float
    outer_clearance_m: float
    end_margin_m: float
    winding_barrier_m: float

    def __post_init__(self) -> None:
        require_nonnegative(**vars(self))

    def usable_dimensions(self, core: EICore) -> tuple[float, float]:
        height = core.window_height_m - 2 * self.end_margin_m
        width = core.window_width_m - self.former_wall_m - self.outer_clearance_m
        require_positive(usable_height_m=height, usable_width_m=width)
        return height, width


@dataclass(frozen=True)
class WindingLayout:
    turns_per_layer: int
    layers: int
    mean_turn_length_m: float
    radial_build_m: float


def winding_layout(
    core: EICore,
    turns: int,
    insulated_diameter_m: float,
    usable_height_m: float,
    inner_offset_m: float,
) -> WindingLayout:
    """Pack at wire-diameter pitch and weight the last layer by its actual turns."""
    require_turns(turns)
    require_positive(insulated_diameter_m=insulated_diameter_m, height_m=usable_height_m)
    require_nonnegative(inner_offset_m=inner_offset_m)
    # Recover an exact integer fit rounded one floating-point step below a boundary.
    turns_per_layer = floor(nextafter(usable_height_m / insulated_diameter_m, inf))
    if turns_per_layer < 1:
        raise ValueError("Insulated wire cannot fit in the usable winding height")
    layers = (turns + turns_per_layer - 1) // turns_per_layer
    length = 0.0
    remaining = turns
    for layer in range(layers):
        layer_turns = min(remaining, turns_per_layer)
        offset = inner_offset_m + (layer + 0.5) * insulated_diameter_m
        rectangular_perimeter = 2 * (core.centre_width_m + core.stack_depth_m) + 8 * offset
        length += layer_turns * rectangular_perimeter
        remaining -= layer_turns
    return WindingLayout(turns_per_layer, layers, length / turns, layers * insulated_diameter_m)
