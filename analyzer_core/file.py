import mimetypes
import os
from pathlib import Path
from typing import List

PATH = Path(os.getcwd()).parent
FILES_PATH = Path(__file__).parent.parent
TEMP_DIR_PATH = Path("_temp")


class NotSupported(Exception):
    def __init__(self, message, *args):
        super().__init__(message, *args)


def create_temp_files(path: Path | str = FILES_PATH) -> List[Path]:
    """
    Create a temporary directory tree at the given path, mirroring the existing directory structure.

    This function walks through the directory structure at `path` and recreates the same
    structure inside a "_temp" subdirectory. Useful for preparing isolated environments
    or backup folder trees.
    """
    path = Path(path)
    if path.is_file():
        # TODO: implement behavior when is only files with
        raise NotImplementedError

    files = []
    temp_file_path = path / TEMP_DIR_PATH
    temp_file_path.mkdir(parents=True, exist_ok=True, mode=0o777)

    for root, dirs, _ in os.walk(path):
        if str(TEMP_DIR_PATH) in str(Path(root)):
            continue
        relative_path = Path(root).relative_to(path)
        if relative_path == Path("."):
            continue

        new_dir = temp_file_path / relative_path
        try:
            original_mask = os.umask(0)
            new_dir.mkdir(parents=True, exist_ok=True, mode=0o777)
            files.append(new_dir)
        except PermissionError:
            print(f"Permission denied {new_dir}")
        finally:
            os.umask(original_mask)
    return files


def check_type(path: str | Path) -> str:
    """
    Return the high-level MIME type of the given file path.

    :raise:
        NotSupported:   If the MINE type cannot be determined

    :return: Top level MINE type (e.g. 'image', 'video' ...)
    """
    path = Path(path)
    mine_type, _ = mimetypes.guess_type(path)
    if mine_type is None:
        raise NotSupported(f"File {path} is not supported (unknow MIME type).")
    return mine_type.split("/")[0]
