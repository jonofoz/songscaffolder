import sys
from random import randint as r_int

sys.path.append("..")
from common import attributes_map
from scaffolder import SongScaffolder

# These will of course change with user input, but for now...
attributes_to_use = {attr:True for attr in attributes_map.keys()}
directives = {
    "key-signatures": {
        "use_spicy_modes": True,
        "include_generics": False
    }
}

def main():
    with SongScaffolder(attributes_to_use, directives) as scaffolder:
        scaffolder.print_results()

if __name__ == "__main__":
    main()