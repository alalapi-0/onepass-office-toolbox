"""File system related tools for OnePass Office Toolbox.

This package hosts utilities for batch operations such as renaming files or
reorganizing folder contents. Each module is designed to be callable from the
package CLI for quick experiments and automation scripts.
"""

from .rename_files_basic import main as rename_files_basic_main  # noqa: F401
from .organize_by_extension import main as organize_by_extension_main  # noqa: F401
