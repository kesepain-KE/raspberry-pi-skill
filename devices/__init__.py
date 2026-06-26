"""Semantic device layer for raspberry-pi-skill."""

from .common import DeviceError, DeviceRegistry, emit_json, fail, load_device_registry

__all__ = [
    "DeviceError",
    "DeviceRegistry",
    "emit_json",
    "fail",
    "load_device_registry",
]
