import unittest

import spacy
import warnings
from sys import platform
import pytest

from quickumls import spacy_component
from quickumls.constants import MEDSPACY_DEFAULT_SPAN_GROUP_NAME
from pathlib import Path
class TestQuickUMLSSpangroup(unittest.TestCase):


    quickumls_fp=str(Path('output', 'QuickUMLS_SAMPLE_lowercase_UNQLITE'))
    @classmethod
    def setUpClass(cls):
        """Create sample db on the fly, to avoid os dependent path issue.
        """
        from .init_db import init
        quickumls_fp=init(quickumls_fp=cls.quickumls_fp)  



    def test_custom_span_group_name(self):
        """
        Test that extractions can be made for custom span group names
        """

        # let's make sure that this pipe has been initialized
        # At least for MacOS and Linux which are currently supported...


        # allow default QuickUMLS (very small sample data) to be loaded
        nlp = spacy.blank("en")

        custom_span_group_name = "my_own_span_group"

        nlp.add_pipe("medspacy_quickumls", config={"threshold": 0.7,
                                                   "result_type": "group",
                                                   "span_group_name": custom_span_group_name,
                                                   "quickumls_fp":self.quickumls_fp})

        text = "Decreased dipalmitoyllecithin also branching glycosyltransferase and dipalmitoyl phosphatidylcholine"

        doc = nlp(text)

        assert len(doc.ents) == 0

        assert MEDSPACY_DEFAULT_SPAN_GROUP_NAME not in doc.spans or len(doc.spans[MEDSPACY_DEFAULT_SPAN_GROUP_NAME]) == 0

        assert len(doc.spans[custom_span_group_name]) >= 1
