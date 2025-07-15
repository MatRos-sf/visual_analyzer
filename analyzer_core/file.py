import os
from pathlib import Path
from typing import List, Tuple

PATH = Path(os.getcwd()).parent
FILES_PATH = Path(__file__).parent.parent / "files"
TEMP_DIR_NAME_PATH = Path("_temp")


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


# TODO: deprecated function
def create_temp_files(paths: List[Path], main_path: Path) -> None:
    """
    Create temporary directories inside main_path/TEMP_DIR_NAME_PATH
    matching the structure of given paths.
    """
    import warnings

    warnings.warn(
        "create_temp_files is deprecated and will be removed in a future release.",
        DeprecationWarning,
    )

    temp_file_path = main_path / TEMP_DIR_NAME_PATH
    temp_file_path.mkdir(parents=True, exist_ok=True, mode=0o777)

    original_mask = os.umask(0)
    for path in paths:
        temp_dir = temp_file_path / path
        try:
            temp_dir.mkdir(parents=True, exist_ok=True, mode=0o777)
        except PermissionError:
            print(f"Permission denied {temp_dir}")
        finally:
            os.umask(original_mask)
