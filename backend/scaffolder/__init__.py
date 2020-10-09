import os
from random import randint

def _get_subset(data):
    chance = randint(1,5)
    return [k for k,v in data.items() if v >= chance]

def _pick_random(data):
    if len(data) > 0:
        return data[randint(0, len(data) - 1)]
    return data

def _count_keys_in_dict(data):
    total_keys = 0
    for k, v in data.items():
        if isinstance(v, dict):
            total_keys += _count_keys_in_dict(v)
        else:
            total_keys += 1
    return total_keys

class SongScaffolder(object):
    def __init__(self, metadata={}, quantities={}, attributes={}):
        self.metadata = metadata
        self.attributes = attributes
        self.quantities = quantities

    def __enter__(self):
        self.generate()
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __getitem__(self, attr):
        return self.song_data[attr]

    def generate(self):
        self.song_data = {}
        for attr_title, should_include in self.attributes.items():
            if should_include == True:
                self.song_data[attr_title] = self._generate_attr_results(attr_title, int(self.quantities[attr_title]))

    def get_json_results(self):
        return self.song_data

    def _generate_attr_results(self, attr_title, results_left=1):

        def _try_append_result(result, results, results_left):
            if result not in results:
                results.append(result)
                results_left -= 1
            return results_left

        def _get_input(filename):
            return os.path.join("inputs", filename + ".json")

        def _more_results_than_data(data, results_wanted):
            return True if results_wanted > _count_keys_in_dict(data) else False

        if attr_title not in self.metadata:
            return ["UNDEFINED: you have no data for this!"]
        else:
            final_results = []
            source_metadata = {attr:freq for attr, freq in self.metadata[attr_title].items() if freq != 0}

            if _more_results_than_data(source_metadata, results_left):
                all_results = [res for res in source_metadata.keys()]
                # TODO: Return as warning to user.
                print(f"\nWARNING: The number of requested results ({results_left}) for '{attr_title}' was greater than the " \
                    f"number of unique results ({len(all_results)}) available from the data. Returning all results.\n")
                return all_results

            while results_left > 0:
                result = _pick_random(_get_subset(source_metadata))
                if result != []:
                    results_left = _try_append_result(result, final_results, results_left)
            return final_results