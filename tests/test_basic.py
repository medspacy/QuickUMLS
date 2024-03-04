#!/usr/bin/env python
import unittest

import pysimstring.simstring as simstring


class TestBasics(unittest.TestCase):
    @classmethod
    def tearDown(cls) -> None:
        from pathlib import Path
        print('Clean up....')
        for tmp_file in Path('./').glob('*.*db'):
            print('remove', tmp_file)
            tmp_file.unlink()


    def test_simstring(self):
        # Create a SimString database with two person names.
        db = simstring.writer('sample.db')
        db.insert('Barack Hussein Obama II')
        db.insert('James Gordon Brown')
        db.close()

        # Open the database for reading.
        db = simstring.reader('sample.db')

        # Use cosine similarity and threshold 0.6.
        db.measure = simstring.cosine
        db.threshold = 0.6
        print(db.retrieve('Barack Obama'))  # OK.
        print(db.retrieve('Gordon Brown'))  # OK.
        print(db.retrieve('Obama'))  # Too dissimilar!

        # Use overlap coefficient and threshold 1.0.
        db.measure = simstring.overlap
        db.threshold = 1.
        print(db.retrieve('Obama'))  # OK.


