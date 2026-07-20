"""
config_loader.py
Functions for reading the config/settings.yaml file and converting it into a dictionary,
allowing all modules (chassis, gimbal, vision, logger, and main) to use the same parameter set.
"""

from pathlib import Path
import yaml


def load_config(path="config/settings.yaml") -> dict:
    """
    Read a .yaml file and return its contents as a dictionary.

    Parameters
    ----------
    path : str | Path
        Path to the settings.yaml file (default = config/settings.yaml,
        relative to the working directory where main.py is executed).

    Returns
    -------
    dict
        All configuration values, for example:
        config["movement"]["distance_m"]
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"No config: {path.resolve()}")

    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)