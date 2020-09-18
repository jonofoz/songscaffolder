import sys
import os
# import json
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
    def __init__(self, data={}, quantities={}, attributes={}, directives={}):
        self.data = data
        self.attributes = attributes
        self.quantities = quantities
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
        for full_title, truth_value in self.attributes.items():
            if truth_value == True:
                # directives_to_use = self.directives[full_title] if full_title in self.directives else {}
                directives_to_use = {}
                # TODO: Replace r_int with value specified by user.
                # TODO: Remove directives to generalize data format.
                self.song_data[full_title] = self._generate(full_title, int(self.quantities[full_title]), directives=directives_to_use)
                # TODO: Remove printable_data.
                # self.printable_data.append("{:16} {}".format(full_title.upper().replace("_", " "), self.song_data[attr]))

    # TODO: Remove print_results.
    def print_results(self):
        print("\n------------ NEW SCAFFOLD ------------\n")
        for line in self.printable_data:
            print(line + "\n")
        print("--------------------------------------\n")

    def get_json_results(self):
        return self.song_data

    def _generate(self, full_title, results_left=1, **directives):

        def _try_append_result(result, results, results_left):
            if result not in results:
                results.append(result)
                results_left -= 1
            return results_left

        def _get_input(filename):
            return os.path.join("inputs", filename + ".json")

        def _more_results_than_data(data, results_wanted):
            return True if results_wanted > _count_keys_in_dict(data) else False

        # with open(os.path.join(os.path.dirname(__file__), "inputs", "{}.json".format(full_title))) as f:
        source_data = self.data[full_title]
        results = []

        # For now, this only works on single-level JSON documents.
        if _more_results_than_data(source_data, results_left):
            # TODO: Return as warning to user.
            print("\nWARNING: The number of requested results ({}) for '{}' was greater than the" \
                  "unique results available from the data. Returning all results.\n".format(results_left, full_title))
            return [k for k in source_data.keys()]

        # TODO: Remove this check once data format is standardized.
        while results_left > 0:
            result = _pick_random(_get_subset(source_data))
            results_left = _try_append_result(result, results, results_left)

        return results