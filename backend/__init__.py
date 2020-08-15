import sys
from random import randint as r_int

sys.path.append("..")
from common import attributes
from scaffolder import SongScaffolder

init_data = {attr:True for attr in attributes.keys()}
directives = {
    "key_signatures": {
        "use_spicy_modes": True,
        "include_generics": False
    }
}

with SongScaffolder() as scaffolder:
    scaffolder.generate()
    scaffolder.print()
