from __future__ import annotations

from typing import Dict, Optional, Union
from dotenv import load_dotenv

import os

from data.const import *

__all__ = ["Configurable"]


class Configurable:
    def __init__(self, config: Optional[Dict[str, Optional[Union[str, int]]]] = None):
        self._config = self._check_default(config or {})

    @staticmethod
    def _check_default(
        config: Dict[str, Optional[Union[str, int]]],
    ) -> Dict[str, Optional[Union[str, int]]]:
        """Check and set default values for the configuration."""
        load_dotenv()
        default: Dict[str, Optional[Union[str, int]]] = {
            PROTOCOL_KEY: os.getenv(PROTOCOL_ENV_KEY, DEFAULT_PROTOCOL),
            HOST_KEY: os.getenv(HOST_ENV_KEY, DEFAULT_HOST),
            PORT_KEY: int(os.getenv(PORT_ENV_KEY, DEFAULT_DATA_PORT)),
            NODE_PORT_KEY: int(os.getenv(NODE_PORT_ENV_KEY, DEFAULT_NODE_PORT)),
            MCAST_ADDR_KEY: os.getenv(MCAST_ADDR_ENV_KEY, DEFAULT_MCAST_ADDR),
            DB_BASE_URL_KEY: os.getenv(DB_BASE_URL_ENV_KEY, DEFAULT_DB_BASE_URL),
            DB_NAME_KEY: os.getenv(DB_NAME_ENV_KEY, DEFAULT_DB_NAME),
            CONTENT_PATH_KEY: os.getenv(CONTENT_PATH_ENV_KEY, DEFAULT_CONTENT_PATH),
        }
        default[DB_URL_KEY] = default[DB_BASE_URL_KEY] + default[DB_NAME_KEY]

        for key, value in default.items():
            config.setdefault(key, value)
        return config

    def copy_with_updates(
        self, updates: Dict[str, Optional[Union[str, int]]]
    ) -> Configurable:
        """Return a copy of the current configuration with updates applied."""
        new_config = self._config.copy()
        new_config.update(updates)
        return Configurable(new_config)

    def __getitem__(self, name):
        """Get a value from the configuration."""
        att = self._config.get(name)
        if att:
            return att
        raise KeyError(f"Key {name} not found in configuration")

    def __setitem__(self, name, value):
        """Set a value in the configuration."""
        if name not in self._config:
            raise KeyError(f"Key {name} not found in configuration")
        self._config[name] = value
