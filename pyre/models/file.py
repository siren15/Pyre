from pathlib import Path
from typing import Optional, Any, List, Union, BinaryIO
from io import IOBase
from pydantic import Field as field, FilePath, model_validator
from .base import PyreObject


class FileMetadata(PyreObject):
    type: str = None
    width: Optional[int] = None
    height: Optional[int] = None


class File(PyreObject):
    id: str = field(alias='_id', default=None)
    tag: str = None
    filename: str = None
    metadata: FileMetadata = None
    content_type: str = None
    size: int = None
    deleted: Optional[bool] = False
    reported: Optional[bool] = False
    message_id: Optional[str] = None
    user_id: Optional[str] = None
    server_id: Optional[str] = None
    object_id: Optional[str] = None

class UploadableFile(PyreObject):
    file: Union[IOBase, BinaryIO, Path, str]
    file_name: str = None
    content_type: str = None

    @model_validator(mode='after')
    def val_file_name(cls, data):
        m = data
        if m.file_name is None:
            if isinstance(m.file, (IOBase, BinaryIO)):
                m.file_name = 'file'
            else:
                m.file_name = Path(m.file).name
        return m
    
    def open_file(self) -> BinaryIO | IOBase:
        """
        Opens the file.

        Returns:
            A file-like BinaryIO object.

        """
        if isinstance(self.file, (IOBase, BinaryIO, bytes)):
            return self.file
        return open(str(self.file), "rb")

    def __enter__(self) -> "File":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if isinstance(self.file, (IOBase, BinaryIO)):
            self.file.close()

UPLOADABLE_TYPE = Union[UploadableFile, IOBase, BinaryIO, Path, str]

def open_file(file: UPLOADABLE_TYPE) -> BinaryIO | IOBase:
    """
    Opens the file.

    Args:
        file: The target file or path to file.

    Returns:
        A file-like BinaryIO object.

    """
    match file:
        case UploadableFile():
            return file.open_file()
        case IOBase() | BinaryIO():
            return file
        case Path() | str():
            return open(str(file), "rb")
        case _:
            raise ValueError(f"{file} is not a valid file")