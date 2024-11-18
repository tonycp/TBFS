from .dtos import FileInputDto, TagInputDto, UserInputDto
from .business_data import FileInputTypes
from .handlers import *


@Create(FileInputTypes)
def create_file(data: FileInputDto):
    pass


@Update(FileInputTypes)
def update_file(data: FileInputDto):
    pass


@Delete({"file_id": int})
def delete_file(file_id):
    pass


@Get({"file_id": int})
def get_file(file_id):
    pass


@Get(FileInputTypes)
def get_file_by_input(data: FileInputDto):
    pass


@GetAll(FileInputTypes)
def get_all_files(data: FileInputDto):
    pass
