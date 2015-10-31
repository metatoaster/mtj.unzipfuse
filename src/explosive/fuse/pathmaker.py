import re

FLATTEN_CHAR = '_'

__all__ = [
    'default',
    'flatten',
    'junk',
]


def default():
    """
    Present file entries as they were within their respective directory
    structures to the root of its source archive.
    """

    def default(inner_path):
        frags = inner_path.split('/')
        filename = frags.pop()

        return frags, filename

    return default


def flatten(char='_'):
    """
    Flattens the directory structure to the root of the mount point by
    replacing all path separators for each file entries with the `_`
    character by default.
    """

    if char == '/':
        raise ValueError('`char` cannot be `/` path separator.')

    if len(char) != 1:
        raise ValueError('`char` must be a single character.')

    def flatten(inner_path):
        if inner_path.endswith('/'):
            # Directories shouldn't result in a file entry.
            return [], ''

        return [], inner_path.replace('/', char)

    return flatten


def junk(keep='0'):
    """
    Junk paths, keep only directories counting from root up to the level
    specified for a positive keep number, otherwise junking all but the
    absolute number of keep levels previous to the basename of the
    filename for a negative keep number.  Default is to keep no
    directories.  Useful value is ``1`` if it is desirable to keep the
    source archive name as a container directory (i.e. ``-l junk:1``)
    if ``--omit-arcname`` is not used.
    """

    if not re.match(r"^[-+]?\d+$", keep):
        raise ValueError('`keep` must be a number')

    level = int(keep)

    def junk(inner_path):
        # Special case where no path separator.
        if '/' not in inner_path:
            return [], inner_path

        dirname, basename = inner_path.rsplit('/', 1)
        if level >= 0:
            frags = dirname.split('/')[:level]
        else:
            frags = dirname.split('/')[level:]
        return frags, basename

    return junk


# TODO consider keeping the "plugins" within a class either by some
# sort of registration mechanism or other.

def _tokenize_arg(arg):
    # limitations: no empty parameters.
    return [i.replace('\\:', ':')
            for i in re.findall(r'((?:[^:\\]*(?:\\.)?)+)', arg) if i]

def _process_arg(arg):
    """
    Convert the string argument into a pathmaker callable.
    """

    g = globals()
    args = _tokenize_arg(arg)
    if args[0] not in __all__:
        raise ValueError('No such pathmaker')
    pm = g.get(args[0])
    if pm is None:
        raise ValueError('No such pathmaker')

    try:
        return pm(*args[1:])
    except TypeError:
        raise ValueError('Invalid argument')
