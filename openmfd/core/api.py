"""Helpers for deriving public module export surfaces."""

from collections.abc import Mapping


def derive_public_exports(
    namespace: Mapping[str, object], package_prefix: str = "openmfd."
) -> list[str]:
    """Derive public API exports from module bindings.

    A binding counts as public if:
    - its name is not private
    - it originates from the OpenMFD package tree
    """

    exports: list[str] = []
    for name, value in namespace.items():
        if name.startswith("_"):
            continue
        module_name = getattr(value, "__module__", "")
        if module_name.startswith(package_prefix):
            exports.append(name)
    return sorted(exports)
