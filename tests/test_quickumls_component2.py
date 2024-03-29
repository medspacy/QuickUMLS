import unittest
from quickumls import spacy_component
import spacy
from quickumls.constants import MEDSPACY_DEFAULT_SPAN_GROUP_NAME
from pathlib import Path
"""
This test won't pass when tested with others in pytest tests. Skip it for now.
"""
class TestSpanGoup2(unittest.TestCase):

    quickumls_fp=str(Path('output', 'QuickUMLS_SAMPLE_lowercase_UNQLITE'))
    @classmethod
    def setUpClass(cls):
        """Create sample db on the fly, to avoid os dependent path issue.
        """
        from .init_db import init
        quickumls_fp=init(quickumls_fp=cls.quickumls_fp)      

    def test_multiword_entity(self):
        """
        Test that an extraction can be made on a concept with multiple words
        """

        # let's make sure that this pipe has been initialized
        # At least for MacOS and Linux which are currently supported...
        # allow default QuickUMLS (very small sample data) to be loaded
        nlp = spacy.blank("en")

        nlp.add_pipe("medspacy_quickumls", config={"threshold": 0.7, "result_type": "group","quickumls_fp":self.quickumls_fp})

        # the demo data contains this concept:
        # dipalmitoyl phosphatidylcholine
        text = """dipalmitoyl phosphatidylcholine"""

        doc = nlp(text)

        assert len(doc.spans[MEDSPACY_DEFAULT_SPAN_GROUP_NAME]) == 1