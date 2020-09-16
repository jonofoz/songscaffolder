import sys
import os
import json
import unittest
sys.path.append(os.path.join("..", ".."))

from common       import attributes_map
from common.utils import get_file_dir
from backend.scaffolder import SongScaffolder

class TestScaffolderClass(unittest.TestCase):
    def setUp(self):
        self.attributes_to_use = {attr:True for attr in attributes_map.keys()}
        self.directives = {
            "key-signatures": {
                "use_spicy_modes": True,
                "include_generics": False
            }
        }
        self.metadata = {}

    def test_all_keys(self):
        with SongScaffolder(self.attributes_to_use, self.directives) as scaffolder:
            for k in attributes_map.keys():
                self.assertTrue(k in scaffolder.song_data)

if __name__ == "__main__":
    unittest.main()