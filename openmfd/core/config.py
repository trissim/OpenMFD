"""Nominal configuration contracts shared across OpenMFD subsystems."""

from abc import ABC, abstractmethod


class ConfigurationContract(ABC):
    """Template-method base for configuration records.

    Configuration objects in OpenMFD follow a shared lifecycle:

    1. normalize user input into canonical field values
    2. validate the resulting configuration
    3. derive any secondary state or side effects

    Subclasses implement the pieces they need, but the lifecycle itself is a
    single nominal contract rather than ad hoc ``__post_init__`` logic in each
    dataclass.
    """

    def __post_init__(self) -> None:
        self._normalize()
        self._validate()
        self._derive()

    def _normalize(self) -> None:
        """Canonicalize field values before validation."""

    @abstractmethod
    def _validate(self) -> None:
        """Fail loudly if the configuration is invalid."""

    def _derive(self) -> None:
        """Apply derived state or side effects after validation."""


class PositiveFieldsConfiguration(ConfigurationContract):
    """Configuration contract for records defined by positive numeric fields."""

    @abstractmethod
    def _positive_fields(self) -> dict[str, float | None]:
        """Return the positive-valued field family owned by this config."""

    def _validate(self) -> None:
        for name, value in self._positive_fields().items():
            if value is None:
                continue
            if value <= 0:
                raise ValueError(f"{name} must be positive, got {value}")
        self._validate_after_positive_fields()

    def _validate_after_positive_fields(self) -> None:
        """Allow subclasses to validate additional non-positive-field rules."""
