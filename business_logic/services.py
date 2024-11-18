from .services import *
from .business_data import *


def get_FileService(db_url) -> FileService:
    return FileService(Repository[File](db_url))


def get_UserService(db_url) -> UserService:
    return UserService(Repository[User](db_url))


def get_TagService(db_url) -> TagService:
    return TagService(Repository[Tag](db_url))
