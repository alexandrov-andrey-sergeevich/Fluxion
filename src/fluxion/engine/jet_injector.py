from abc import ABC
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from math import pi, exp, sqrt


@dataclass(frozen=True)
class Injector(ABC):
    density: float
    diameter: float
    length: float
    mass_flow_rate: float
    viscosity: float

    @cached_property
    def injector_nozzle_area(self) -> float:
        return pi * self.diameter**2 / 4

    @cached_property
    def reynolds_number(self) -> float:
        return 4 * self.mass_flow_rate / (pi * self.diameter * self.viscosity)

    @cached_property
    def average_speed(self) -> float:
        return self.mass_flow_rate / (self.density * self.injector_nozzle_area)

    @cached_property
    def relative_length_injector(self) -> float:
        return self.length / self.diameter


class Reynolds(Enum):
    LAMINAR = 2000
    TURBULENT = 10_000


@dataclass(frozen=True)
class LiquidJetInjector(Injector):
    density_comb: float
    sigma_fuel: float

    @cached_property
    def linear_hydraulic_resistance(self) -> float:
        if self.reynolds_number < Reynolds.LAMINAR.value:
            return 64 / self.reynolds_number
        elif Reynolds.LAMINAR.value <= self.reynolds_number <= Reynolds.TURBULENT.value:
            return 0.3164 * self.reynolds_number**-0.25
        return 0.031

    @cached_property
    def injector_losses_inlet(self) -> float:
        if self.reynolds_number < Reynolds.LAMINAR.value:
            return 2.2 - 0.726 * exp(
                -74.5 * self.viscosity * self.length / self.mass_flow_rate
            )
        return 1 + 2.65 * self.linear_hydraulic_resistance

    @cached_property
    def injector_flow_coefficient(self) -> float:
        return 1 / sqrt(
            self.injector_losses_inlet
            + self.linear_hydraulic_resistance * self.length / self.diameter
        )

    @cached_property
    def pressure_drop_injector(self) -> float:
        return self.mass_flow_rate**2 / (
            2
            * self.density
            * self.injector_flow_coefficient**2
            * self.injector_nozzle_area**2
        )

    @cached_property
    def weber_criterion(self) -> float:
        return (
            self.density_comb * self.average_speed**2 * self.diameter / self.sigma_fuel
        )

    @cached_property
    def media_diameter_spray_droplets(self) -> float:
        return self.diameter * (27 * pi / 4) ** (1 / 3) * self.weber_criterion ** (-1 / 3)


@dataclass(frozen=True)
class GasJetInjector(Injector):
    combustion_pressure: float
    pressure_drop_internal_circuit: float
    gas_constant_gen_gas: float
    temperature_gen_gas: float
    entropy_expansion_ratio: float

    @cached_property
    def injector_pressure(self) -> float:
        return self.combustion_pressure + self.pressure_drop_internal_circuit

    @cached_property
    def density_gen_gas(self) -> float:
        return self.injector_pressure / (
            self.gas_constant_gen_gas * self.temperature_gen_gas
        )

    @cached_property
    def injector_flow_coefficient(self) -> float:
        return ((sqrt(1.23 ** 2 + 232 * self.length / (self.reynolds_number * self.diameter)) - 1.23)
                / (116 * self.length / (self.reynolds_number * self.diameter)))

    @cached_property
    def injector_nozzle_area_outlet(self) -> float:
        return self.mass_flow_rate / (self.injector_flow_coefficient * self.density_gen_gas * (self.pressure_drop_internal_circuit / self.injector_pressure) ** (1 / self.entropy_expansion_ratio) * sqrt(2 * self.entropy_expansion_ratio / (self.entropy_expansion_ratio - 1) * self.gas_constant_gen_gas * self.temperature_gen_gas * (1 - (self.pressure_drop_internal_circuit / self.injector_pressure) ** ((self.entropy_expansion_ratio - 1) / self.entropy_expansion_ratio))))

    @cached_property
    def diameter_injector(self) -> float:
        return sqrt(4 * self.injector_nozzle_area_outlet / pi)

    @cached_property
    def discrepancy(self) -> float:
        return (self.diameter_injector - self.diameter) / self.diameter_injector
