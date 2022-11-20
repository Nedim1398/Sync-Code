""" Used to determine actions/operations passed to the logger. """

from enum import Enum

class Action (Enum):
    """ Class containing actions/operations passed to the logger. """
    COPY = 1
    OVERWRITE = 2
    DELETE = 3
