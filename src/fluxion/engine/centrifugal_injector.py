from math import pi, sqrt, log, atan, cos, sin
from enum import Enum
from dataclasses import dataclass
from functools import cached_property
from abc import ABC, abstractmethod


class AngularValues(Enum):
    """Константа прямого угла"""
    RIGHT_ANGLE = 90


@dataclass(frozen=True)
class Injector(ABC):
    """Основной класс содержащий обязательные функции для расчета"""
    outer_diameter_injector: float
    side_wall_thickness_injector: float
    number_input_tangential_holes: float
    diameter_input_tangential_holes: float
    length_input_tangential_holes: float
    relative_length_twisting_chamber: float
    diameter_injector_nozzle: float
    relative_length_injector_nozzle: float
    angle_nozzle_axis: float
    mass_flow_rate: float
    viscosity: float
    cross_sectional_area_one_passage_channel: float
    density_fuel_component_front_injector: float
    density_combustion_products: float
    surface_tension_coefficient: float

    @cached_property
    def diameter_twisting_chamber_injector(self) -> float:
        """Диаметр камеры закручивания центробежной форсунки"""
        return self.outer_diameter_injector - 2 * self.side_wall_thickness_injector

    @cached_property
    def relative_length_tangential_hole(self) -> float:
        """Отношение длины входного тангенциального к его диаметру"""
        return self.length_input_tangential_holes / self.diameter_input_tangential_holes

    @cached_property
    def length_twisting_chamber(self) -> float:
        """Длину камеры закручивания центробежной форсунки"""
        return self.relative_length_twisting_chamber * self.diameter_twisting_chamber_injector

    @cached_property
    def radius_twisting_chamber_injector(self) -> float:
        """Радиус камеры закручивания центробежной форсунки"""
        return self.diameter_twisting_chamber_injector / 2

    @cached_property
    def radius_input_tangential_holes(self) -> float:
        """Радиус входных тангенциальных отверстий"""
        return self.diameter_input_tangential_holes / 2

    @cached_property
    def radius_tangential_inlet(self) -> float:
        """Величину радиуса, на котором расположена ось входного тангенциального отверстия от оси форсунки"""
        return self.radius_twisting_chamber_injector - self.radius_input_tangential_holes

    @cached_property
    def length_injector_nozzle(self) -> float:
        """Длину сопла форсунки"""
        return self.relative_length_injector_nozzle * self.diameter_injector_nozzle

    @cached_property
    def radius_injector_nozzle(self) -> float:
        """Радиус сопла форсунки"""
        return self.diameter_injector_nozzle / 2

    @cached_property
    def reynolds_number(self) -> float:
        """Число Рейнольдса"""
        return (4 * self.mass_flow_rate) / (pi * self.viscosity * self.diameter_input_tangential_holes
                                            * sqrt(self.number_input_tangential_holes))

    @cached_property
    def coefficient_friction(self) -> float:
        """Коэффициент трения"""
        return 10 ** ((25.8 / (log(self.reynolds_number)) ** 2.58) - 2)

    @abstractmethod
    def geometric_characteristics_injector(self) -> float:
        """Геометрическую характеристику форсунки"""
        raise NotImplementedError('Не выбран тип форсунки для расчета')

    @cached_property
    def equivalent_geometric_characteristic_injector(self) -> float:
        """Эквивалентную геометрическую характеристику"""
        return self.geometric_characteristics_injector() / (1 + self.coefficient_friction /
                                                            2 * self.radius_tangential_inlet *
                                                            (self.radius_tangential_inlet +
                                                             self.diameter_input_tangential_holes -
                                                             self.radius_injector_nozzle))

    @cached_property
    def ratio_live_section_injector_nozzle(self) -> float:
        """Коэффициент живого сечения сопла форсунки"""
        linear_fraction_geometric_characteristic = self.equivalent_geometric_characteristic_injector / (2 * sqrt(2))
        quadratic_fraction_geometric_characteristic = sqrt(self.equivalent_geometric_characteristic_injector ** 2 / 8 -
                                                           1 / 27)

        return 1 / ((linear_fraction_geometric_characteristic + quadratic_fraction_geometric_characteristic) ** (1 / 3)
                    + (linear_fraction_geometric_characteristic - quadratic_fraction_geometric_characteristic) **
                    (1 / 3)) ** 2

    @cached_property
    def flow_rate_centrifugal_injector(self) -> float:
        """Коэффициент расхода центробежной форсунки"""
        return self.ratio_live_section_injector_nozzle * sqrt(self.ratio_live_section_injector_nozzle /
                                                              (2 - self.ratio_live_section_injector_nozzle))

    @cached_property
    def average_angle_spray_torch(self) -> float:
        """Средний угол факела распыла"""
        return atan(2 * self.flow_rate_centrifugal_injector * self.equivalent_geometric_characteristic_injector /
                    sqrt((1 + sqrt(1 - self.ratio_live_section_injector_nozzle)) ** 2 - 4 *
                         self.flow_rate_centrifugal_injector ** 2 *
                         self.equivalent_geometric_characteristic_injector ** 2))

    @cached_property
    def injector_nozzle_area(self) -> float:
        """Площадь сопла форсунки"""
        return pi * self.diameter_injector_nozzle ** 2 / 4

    @cached_property
    def pressure_drop_front_injector(self) -> float:
        """Перепад давления на форсунке, для обеспечения необходимого расхода компонента через форсунку"""
        return self.mass_flow_rate ** 2 / (2 * self.density_fuel_component_front_injector *
                                           self.flow_rate_centrifugal_injector ** 2 * self.injector_nozzle_area ** 2)

    @cached_property
    def radius_vortex_outlet_section_injector(self) -> float:
        """Радиус вихря жидкости или воздушного вихря в выходном сечении форсунки"""
        return self.radius_injector_nozzle * sqrt(1 - self.ratio_live_section_injector_nozzle)

    @cached_property
    def area_live_section_injector_nozzle(self) -> float:
        """Площадь живого сечения сопла форсунки"""
        return self.ratio_live_section_injector_nozzle * self.injector_nozzle_area

    @cached_property
    def average_value_axial_velocity_outlet_injector(self) -> float:
        """Среднее значение осевой скорости на выходе из форсунки"""
        return self.mass_flow_rate / (self.density_fuel_component_front_injector *
                                      self.area_live_section_injector_nozzle)

    @cached_property
    def average_value_absolute_velocity_outlet_injector(self) -> float:
        """Среднее значение абсолютной скорости на выходе из форсунки"""
        return self.average_value_axial_velocity_outlet_injector / cos(self.average_angle_spray_torch)

    @cached_property
    def thickness_veil_outlet_injector(self) -> float:
        """Толщину пелены на выходе из форсунки"""
        return self.radius_injector_nozzle - self.radius_vortex_outlet_section_injector

    @cached_property
    def weber_criterion(self) -> float:
        """Критерий Вебера"""
        return self.density_combustion_products * self.average_value_absolute_velocity_outlet_injector ** 2 * \
            self.diameter_injector_nozzle / self.surface_tension_coefficient

    @cached_property
    def laplace_criterion(self) -> float:
        """Критерий Лапласа"""
        return self.density_fuel_component_front_injector * self.thickness_veil_outlet_injector * \
            self.surface_tension_coefficient / self.viscosity

    @cached_property
    def media_diameter_spray_torch_droplets(self) -> float:
        """Медианный диаметр образовавшихся капель в факеле распыла форсунки"""
        return 269 * self.laplace_criterion ** -0.35 * ((self.weber_criterion * self.density_combustion_products) /
                                                        self.density_fuel_component_front_injector) ** 0.483


@dataclass(frozen=True)
class CentrifugalInjector(Injector):
    """"""
    def geometric_characteristics_injector(self) -> float:
        """Геометрическую характеристику центробежной форсунки"""
        product_radii_entrance_holes = self.radius_tangential_inlet * self.radius_injector_nozzle
        product_number_holes_radius = self.number_input_tangential_holes * self.radius_input_tangential_holes ** 2

        if self.angle_nozzle_axis == AngularValues.RIGHT_ANGLE.value:
            return product_radii_entrance_holes / product_number_holes_radius
        else:
            return product_radii_entrance_holes / product_number_holes_radius * sin(self.angle_nozzle_axis)


@dataclass(frozen=True)
class ScrewInjector(Injector):
    """"""
    def geometric_characteristics_injector(self) -> float:
        """Геометрическую характеристику шнековой форсунки"""
        return (pi * self.radius_tangential_inlet * self.radius_injector_nozzle) / \
               (self.number_input_tangential_holes * self.cross_sectional_area_one_passage_channel) * \
            sin(self.angle_nozzle_axis)
