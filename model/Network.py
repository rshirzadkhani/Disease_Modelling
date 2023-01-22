from enum import Enum, auto


class Data(Enum):
    WIFI = auto()
    COPENHAGEN = auto()
    SAFEGRAPH = auto()
    WORKPLACE = auto()
    LYONSCHOOL = auto()
    HIGHSCHOOL = auto()
    CONFERENCE = auto()

class Network(Enum):
    ER = auto()
    BA = auto()
    TEMPORAL = auto()
    STATIC = auto()
    EdgeMST = auto()
    DegMST = auto()