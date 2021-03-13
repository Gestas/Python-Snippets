import os
from pathlib import Path


class PathDetails:
    """One PathThingy to rule them all. Or: A single place to get lots of details about a path."""

    def __init__(self, path: [Path, str]):
        self.path = Path(path)

        self.file_name = None
        self.file_size = None
        self.path_type = None
        self.original_path = None
        self.file_extension = None
        self.full_path_to_directory = None
        self.file_name_without_extension = None
        self.full_path_to_parent_directory = None
        self.full_path_without_file_extension = None

        self.user_expanded_path = Path(self.path.expanduser())
        self.fully_expanded_path = Path(os.path.expandvars(self.user_expanded_path))
        self.all_path_parts = Path(self.fully_expanded_path).parts

        if self.fully_expanded_path.suffixes:
            self.file_name = self.fully_expanded_path.name
            self.file_extension = self.fully_expanded_path.suffix
            self.file_name_without_extension = Path(self.file_name).stem
            self.full_path_to_directory = Path(self.fully_expanded_path.parents[0])
            self.full_path_without_file_extension = (
                self.full_path_to_directory.joinpath(self.file_name_without_extension)
            )
        else:
            self.full_path_to_directory = self.fully_expanded_path
            self.file_extensions = None

        self.path_exists = self.fully_expanded_path.exists()
        if self.path_exists:
            if self.fully_expanded_path.is_dir():
                self.path_type = "dir"
            if self.fully_expanded_path.is_file():
                self.path_type = "file"
        self.file_size = self.fully_expanded_path.stat().st_size
