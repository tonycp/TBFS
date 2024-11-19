from .services import *
from .business_data import *


def get_FileService(db_url) -> FileService:
    return FileService(get_repository(File, db_url))


def get_UserService(db_url) -> UserService:
    return UserService(get_repository(User, db_url))


def get_TagService(db_url) -> TagService:
    return TagService(get_repository(Tag, db_url))


def get_FileSourceService(db_url) -> FileSourceService:
    return FileSourceService(get_repository(FileSource, db_url))
