try:
    # Python 3.8+
    from importlib import metadata
except ImportError:
    # Python < 3.8
    import importlib_metadata as metadata

from pathlib import Path

try:
    __version__ = metadata.version('payload-api')
except metadata.PackageNotFoundError:
    with open(str(Path(__file__).parent.parent) + '/pyproject.toml') as pyproject_toml:
        __version__ = (
            next(line for line in pyproject_toml if line.startswith("version"))
            .split("=")[1]
            .strip("'\"\n ")
        )

__version__ = tuple(map(int, __version__.split('.')))
