import sys
from random import randint as r_int

sys.path.append("..")
from common import attributes_map
from scaffolder import SongScaffolder

# These will of course change with user input, but for now...
attributes_to_use = {attr:True for attr in attributes_map.keys()}
directives = {
    "key_signatures": {
        "use_spicy_modes": True,
        "include_generics": False
    }
}

with SongScaffolder(attributes_to_use, directives) as scaffolder:
    scaffolder.generate()
    scaffolder.print_results()
