import mimetypes
import os
from pathlib import Path
from typing import List, Tuple

PATH = Path(os.getcwd()).parent
FILES_PATH = Path(__file__).parent.parent
TEMP_DIR_NAME_PATH = Path("_temp")


class NotSupported(Exception):
    def __init__(self, message, *args):
        super().__init__(message, *args)


def capture_files_and_directories(
    path: Path | str = FILES_PATH,
) -> Tuple[List[Path], List[Path]]:
    """
    Recursively captures all files and directories from the given path, excluding TEMP_DIR_PATH.

    Args:
        path: Root path to search.

    Returns:
        Tuple[List[Path], List[Path]]: A tuple containing a list of file paths and a list of directory paths.
    """
    path = Path(path)

    collected_files = []
    collected_dirs = []

    for root, dirs, files in os.walk(path):
        # skip temp dir
        if TEMP_DIR_NAME_PATH in Path(root).parents:
            continue

        relative_path = Path(root).relative_to(path)

        for file in files:
            file_path = Path(root) / file
            collected_files.append(file_path)

        # do not include the root directory itself in the list
        if relative_path == Path("."):
            continue

        collected_dirs.append(Path(relative_path))

    return collected_files, collected_dirs


# def create_temp_files(paths: List[Path]) -> None:
#     """
#     Create a temporary directory tree at the given path, mirroring the existing directory structure.
#
#     This function walks through the directory structure at `path` and recreates the same
#     structure inside a "_temp" subdirectory. Useful for preparing isolated environments
#     or backup folder trees.
#     """
#     for path in paths:
#
#     # files = []
#     temp_file_path = path / TEMP_DIR_NAME_PATH
#     temp_file_path.mkdir(parents=True, exist_ok=True, mode=0o777)
#
#     for root, dirs, _ in os.walk(path):
#         if str(TEMP_DIR_NAME_PATH) in str(Path(root)):
#             continue
#         relative_path = Path(root).relative_to(path)
#         if relative_path == Path("."):
#             continue
#
#         new_dir = temp_file_path / relative_path
#         try:
#             original_mask = os.umask(0)
#             new_dir.mkdir(parents=True, exist_ok=True, mode=0o777)
#             files.append(new_dir)
#         except PermissionError:
#             print(f"Permission denied {new_dir}")
#         finally:
#             os.umask(original_mask)
#     return files


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
