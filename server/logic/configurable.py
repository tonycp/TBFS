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
        config: Dict[str, Optional[Union[str, int]]]
    ) -> Dict[str, Optional[Union[str, int]]]:
        """Check and set default values for the configuration."""
        load_dotenv()
        default_config: Dict[str, Optional[Union[str, int]]] = {
            PROTOCOL_KEY: os.getenv(PROTOCOL_ENV_KEY, DEFAULT_PROTOCOL),
            HOST_KEY: os.getenv(HOST_ENV_KEY, DEFAULT_HOST),
            PORT_KEY: int(os.getenv(PORT_ENV_KEY, DEFAULT_DATA_PORT)),
            NODE_PORT_KEY: int(os.getenv(NODE_PORT_ENV_KEY, DEFAULT_NODE_PORT)),
            MCAST_ADDR_KEY: os.getenv(MCAST_ADDR_ENV_KEY, DEFAULT_MCAST_ADDR),
        }

        for key, value in default_config.items():
            config.setdefault(key, value)
        return config

    def copy_with_updates(
        self, updates: Dict[str, Optional[Union[str, int]]]
    ) -> Configurable:
        """Return a copy of the current configuration with updates applied."""
        new_config = self._config.copy()
        new_config.update(updates)
        return Configurable(new_config)
