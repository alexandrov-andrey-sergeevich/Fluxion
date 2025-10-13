import pytest
from src.fluxion.engine.jet_injector import LiquidJetInjector, GasJetInjector


class TestLiquidJetInjector:
    @pytest.fixture(scope="function")
    def liquid_jet_injector(self):
        liquid_injector = LiquidJetInjector(
            density=800,
            diameter=0.002,
            length=0.003,
            mass_flow_rate=0.05,
            viscosity=0.0015,
            density_comb=1.2,
            sigma_fuel=0.028,
        )
        return liquid_injector

    def test_injector_nozzle_area(self, liquid_jet_injector):
        assert liquid_jet_injector.injector_nozzle_area == pytest.approx(3.1415926535898e-06)

    def test_reynolds_number(self, liquid_jet_injector):
        assert liquid_jet_injector.reynolds_number == pytest.approx(21220.6590789194)

    def test_average_speed(self, liquid_jet_injector):
        assert liquid_jet_injector.average_speed == pytest.approx(1.9894367886487e+01)

    def test_relative_length_injector(self, liquid_jet_injector):
        assert liquid_jet_injector.relative_length_injector == pytest.approx(1.5)

    def test_linear_hydraulic_resistance(self, liquid_jet_injector):
        assert liquid_jet_injector.linear_hydraulic_resistance == pytest.approx(0.031)

    def test_injector_losses_inlet(self, liquid_jet_injector):
        assert liquid_jet_injector.injector_losses_inlet == pytest.approx(1.08215)

    def test_injector_flow_coefficient(self, liquid_jet_injector):
        assert liquid_jet_injector.injector_flow_coefficient == pytest.approx(0.941283307)

    def test_pressure_drop_injector(self, liquid_jet_injector):
        assert liquid_jet_injector.pressure_drop_injector == pytest.approx(1.7868149049676e+05)

    def test_weber_criterion(self, liquid_jet_injector):
        assert liquid_jet_injector.weber_criterion == pytest.approx(3.3924503451676e+01)

    def test_media_diameter_spray_droplets(self, liquid_jet_injector):
        assert liquid_jet_injector.media_diameter_spray_droplets == pytest.approx(1.71005486466707e-03)


class TestGasInjector:
    @pytest.fixture(scope="function")
    def gas_jet_injector(self):
        gas_injector = GasJetInjector(
            density=5.0,
            diameter=0.005,
            length=0.010,
            mass_flow_rate=0.1,
            viscosity=2e-5,
            combustion_pressure=5e6,
            pressure_drop_internal_circuit=0.5e6,
            gas_constant_gen_gas=300,
            temperature_gen_gas=800,
            entropy_expansion_ratio=1.2,
        )
        return gas_injector

    def test_injector_nozzle_area(self, liquid_jet_injector):
        assert liquid_jet_injector.injector_nozzle_area == pytest.approx(0)

    def test_reynolds_number(self, liquid_jet_injector):
        assert liquid_jet_injector.reynolds_number == pytest.approx(0)

    def test_average_speed(self, liquid_jet_injector):
        assert liquid_jet_injector.average_speed == pytest.approx(0)

    def test_relative_length_injector(self, liquid_jet_injector):
        assert liquid_jet_injector.relative_length_injector == pytest.approx(0)

    def test_injector_pressure(self, gas_jet_injector):
        assert gas_jet_injector.injector_pressure == pytest.approx(0)

    def test_density_gen_gas(self, gas_jet_injector):
        assert gas_jet_injector.density_gen_gas == pytest.approx(0)

    def test_injector_flow_coefficient(self, gas_jet_injector):
        assert gas_jet_injector.injector_flow_coefficient == pytest.approx(0)

    def test_injector_nozzle_area_outlet(self, gas_jet_injector):
        assert gas_jet_injector.injector_nozzle_area_outlet == pytest.approx(0)

    def test_diameter_injector(self, gas_jet_injector):
        assert gas_jet_injector.diameter_injector == pytest.approx(0)
