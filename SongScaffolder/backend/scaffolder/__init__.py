import sys
import os
import json
from random import randint as r_int

sys.path.append(os.path.join("..", ".."))
from common import attributes_map

def _get_subset(data):
    return [k for k,v in data.items() if v >= r_int(1,5)]

def _pick_random(data):
    return data[r_int(0, len(data) - 1)]

def _count_keys_in_dict(data):
    total_keys = 0
    for k, v in data.items():
        if isinstance(v, dict):
            total_keys += _count_keys_in_dict(v)
        else:
            total_keys += 1
    return total_keys

class SongScaffolder(object):
    def __init__(self, attributes={}, directives={}):
        self.attributes = attributes
        self.directives = directives

    def __enter__(self):
        self.generate()
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __getitem__(self, attr):
        return self.song_data[attr]

    def generate(self):
        self.song_data      = {}
        self.printable_data = []
        for attr, full_title in attributes_map.items():
            if attr in self.attributes:
                directives_to_use = self.directives[full_title] if full_title in self.directives else{}
                self.song_data[attr] = self._generate(attr, r_int(1,5), directives=directives_to_use)
                self.printable_data.append("{:16} {}".format(full_title.upper().replace("_", " "), self.song_data[attr]))

    def print_results(self):
        print("\n------------ NEW SCAFFOLD ------------\n")
        for line in self.printable_data:
            print(line + "\n")
        print("--------------------------------------\n")

    def _generate(self, attr, results_left=1, **directives):

        def _try_append_result(result, results, results_left):
            if result not in results:
                results.append(result)
                results_left -= 1
            return results_left

        def _get_input(filename):
            return os.path.join("inputs", filename + ".json")

        def _more_results_than_data(data, results_wanted):
            return True if results_wanted > _count_keys_in_dict(data) else False

        full_title = attributes_map[attr]
        with open(os.path.join(os.path.dirname(__file__), "inputs", "{}.json".format(full_title))) as f:
            source_data = json.load(f)[full_title]
        results = []

        # For now, this only works on single-level JSON documents.
        if _more_results_than_data(source_data, results_left):
            print("\nWARNING: The number of requested results ({}) for '{}' was greater than the" \
                  "unique results available from the data. Returning all results.\n".format(results_left, full_title))
            return [k for k in source_data.keys()]

        if attr in ["CHORD", "FEELS", "GENRE", "INFLC", "INSTR", "MOODS", "THEME"]:
            while results_left > 0:
                result = _pick_random(_get_subset(source_data))
                results_left = _try_append_result(result, results, results_left)
        else:
            if attr == "TMSIG":
                while results_left > 0:
                    num_subset = _get_subset(source_data["numerator"])
                    den_subset = _get_subset(source_data["denominator"])
                    result = "{}/{}".format(_pick_random(num_subset), _pick_random(den_subset))
                    results_left = _try_append_result(result, results, results_left)

            if attr == "KYSIG":
                while results_left > 0:
                    # Use generic
                    if full_title in directives \
                    and "include_generics" in directives[full_title] \
                    and r_int(1, 5) > 3:
                        result = _pick_random(_get_subset(source_data["generic"]))
                        results_left = _try_append_result(result, results, results_left)
                    # Use root + mode
                    else:
                        heat_index = "spicy" \
                            if full_title in directives \
                            and "use_spicy_modes" in directives[full_title] \
                            and r_int(1, 5) > 3 \
                            else "mild"
                        result = "{} {}".format( \
                                _pick_random(_get_subset(source_data["roots"])),
                                _pick_random(_get_subset(source_data["modes"][heat_index]))
                        )
                        results_left = _try_append_result(result, results, results_left)
        return results