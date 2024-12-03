import os


def get_files(dir: str, files: list[str] | str) -> list[str] | str:
    if type(files) == str:
        return os.path.join(dir, files)
    return [os.path.join(dir, fn) for fn in files]


def contains_subdir(dir_: str | os.PathLike) -> bool:
    for item in os.listdir(dir_):
        item_path = os.path.join(dir_, item)
        if os.path.isdir(item_path):
            return True
    return False


def get_subdirs(dir_: str | os.PathLike) -> list[str]:
    return [os.path.join(dir_, subdir) for subdir in os.listdir(dir_)]
