import pytest
import six
import eggshell
from eggshell.config import Paths

def test_Path():
    """Simply check that all properties return a string."""
    path = Paths(eggshell)

    properties = [p for p in dir(Paths) if isinstance(getattr(Paths,p),property)]
    for prop in properties:
        assert (isinstance(getattr(path, prop), six.string_types))

