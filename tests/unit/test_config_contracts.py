from dataclasses import dataclass, field
import importlib.util
from pathlib import Path
import sys

import pytest

from openmfd.core import ConfigurationContract
from openmfd.core.api import derive_public_exports


def load_module(module_name: str, relative_path: str):
    root = Path(__file__).resolve().parents[2]
    path = root / relative_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


devices_config = load_module("test_devices_config", "openmfd/devices/config.py")
export_config = load_module("test_export_config", "openmfd/export/config.py")
inserts_config = load_module("test_inserts_config", "openmfd/inserts/config.py")

CasingConfiguration = devices_config.CasingConfiguration
PDMSConfiguration = devices_config.PDMSConfiguration
ExportConfiguration = export_config.ExportConfiguration
OpenSCADConfig = export_config.OpenSCADConfig
TaperConfiguration = inserts_config.TaperConfiguration


@dataclass
class ExampleConfiguration(ConfigurationContract):
    value: int
    events: list[str] = field(default_factory=list)

    def _normalize(self) -> None:
        self.events.append("normalize")
        self.value = abs(self.value)

    def _validate(self) -> None:
        self.events.append("validate")
        if self.value == 0:
            raise ValueError("value must be non-zero")

    def _derive(self) -> None:
        self.events.append("derive")


@pytest.mark.unit
def test_configuration_contract_runs_template_method_lifecycle() -> None:
    config = ExampleConfiguration(-3)

    assert config.value == 3
    assert config.events == ["normalize", "validate", "derive"]


@pytest.mark.unit
def test_configuration_contract_stops_before_derive_on_validation_error() -> None:
    with pytest.raises(ValueError, match="value must be non-zero"):
        ExampleConfiguration(0)


@pytest.mark.unit
def test_export_configuration_normalizes_then_derives_output_directory(tmp_path: Path) -> None:
    output_directory = str(tmp_path / "exports")

    config = ExportConfiguration(output_directory=output_directory, formats=["scad", "dxf"])  # type: ignore[arg-type]

    assert isinstance(config.output_directory, Path)
    assert config.output_directory == Path(output_directory)
    assert config.output_directory.exists()


@pytest.mark.unit
def test_openscad_config_normalizes_extra_args_to_empty_list() -> None:
    config = OpenSCADConfig()

    assert config.extra_args == []


@pytest.mark.unit
def test_existing_device_config_validation_still_runs_through_contract() -> None:
    with pytest.raises(ValueError, match="x must be positive"):
        CasingConfiguration(x=0, y=5)


@pytest.mark.unit
def test_pdms_scale_factor_matches_legacy_heat_shrinkage_fit() -> None:
    assert PDMSConfiguration(cure_temp=100).scale_factor() == pytest.approx(1.0226)


@pytest.mark.unit
def test_insert_configuration_types_also_use_nominal_contract_validation() -> None:
    with pytest.raises(ValueError, match="height must be positive"):
        TaperConfiguration(height=0, degrees=16)


@pytest.mark.unit
def test_public_export_derivation_prefers_openmfd_bindings() -> None:
    namespace = {
        "_private": object(),
        "ConfigurationContract": ConfigurationContract,
        "pytest": pytest,
    }

    assert derive_public_exports(namespace) == ["ConfigurationContract"]
