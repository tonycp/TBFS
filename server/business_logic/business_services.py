import os
from typing import Any, Dict, Optional, Type
from dotenv import load_dotenv
from .services import *
from .business_data import *

__all__ = ["ServerService", "set_config"]

_service_config = {}


class ServerService:
    def __init__(self):
        _check_default(_service_config)
        self.FileService = _instance_service(FileService, File)
        self.UserService = _instance_service(UserService, User)
        self.TagService = _instance_service(TagService, Tag)
        self.FileSourceService = _instance_service(FileSourceService, FileSource)

    def get_FileService(self) -> FileService:
        return self.FileService

    def get_UserService(self) -> UserService:
        return self.UserService

    def get_TagService(self) -> TagService:
        return self.TagService

    def get_FileSourceService(self) -> FileSourceService:
        return self.FileSourceService


def _instance_service(service: Any, model: Type[ModelType]) -> Any:
    return service(get_repository(model, _service_config["database"]))


def _check_default(config: Dict[str, Optional[Any]]):
    """Check and set default values for the configuration."""
    load_dotenv()
    default_config = {
        "database": os.getenv(
            "DATABASE_URL", "postgresql://postgres:ranvedi@localhost/SDDB"
        ),
    }

    for key, value in default_config.items():
        config.setdefault(key, value)
    return config


def set_config(self, config: Dict[str, Optional[Any]]) -> None:
    """Set the configuration for the server."""
    global _service_config
    _service_config.update(config)
