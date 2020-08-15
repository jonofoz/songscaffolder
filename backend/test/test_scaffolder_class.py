import sys
sys.path.append("../..")

import os
import json
import unittest

from common       import attributes
from common.utils import get_file_dir

import pdb;pdb.set_trace()

class TestScaffolderClass(unittest.TestCase):

    @classmethod
    def setUpClass(TestScaffolderClass):
        local_dir = get_file_dir(__file__)
        with open(os.path.join(local_dir, "test_inputs", "test_data.json")) as f:
            data = json.load(f)
            for attr_name in [
                "chords",
                "feels",
                "genres",
                "influences"
                "instruments",
                "key_signatures",
                "moods",
                "themes",
                "time_signatures",
            ]:
            setattr(TestScaffolderClass, attr_name, data[attr_name])

    def setUp(self):
        self.metadata = {
            "include": "all",
            "data": {

            }
        }

    def test_random_all(self):

        with Scaffolder(metadata) as scaffolder:

            for item in ["instruments", "time_signatures", "feels", "moods", "genres", "themes", "time_signatures"]:
                self.assertTrue(item in scaffolder.keys())
