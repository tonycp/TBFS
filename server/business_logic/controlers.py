from .dtos import FileDto
from .business_services import ServerService
from .handlers import *

_server_service = ServerService()


@GetAll({"tag_query": list[str]})
def list(tag_query: list[str]) -> list[FileDto]:
    file_service = _server_service.get_FileService()
    tag_service = _server_service.get_TagService()
    tags = [ tag.id for tag in tag_service.get_tags_by_names(tag_query)]
    return file_service.get_files_by_tags(tags)
