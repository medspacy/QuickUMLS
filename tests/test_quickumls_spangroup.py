import unittest

import spacy
import warnings
from sys import platform
import pytest

from quickumls import spacy_component
from quickumls.constants import MEDSPACY_DEFAULT_SPAN_GROUP_NAME

class TestQuickUMLSSpangroup(unittest.TestCase):







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
                                                   "span_group_name": custom_span_group_name})

        text = "Decreased dipalmitoyllecithin also branching glycosyltransferase and dipalmitoyl phosphatidylcholine"

        doc = nlp(text)

        assert len(doc.ents) == 0

        assert MEDSPACY_DEFAULT_SPAN_GROUP_NAME not in doc.spans or len(doc.spans[MEDSPACY_DEFAULT_SPAN_GROUP_NAME]) == 0

        assert len(doc.spans[custom_span_group_name]) >= 1
