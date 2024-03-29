import unittest
from quickumls import spacy_component
import spacy
from quickumls.constants import MEDSPACY_DEFAULT_SPAN_GROUP_NAME
from pathlib import Path
"""
This test won't pass when tested with others in pytest tests. Skip it for now.
"""
class TestSpanGoup1(unittest.TestCase):
    
    quickumls_fp=str(Path('output', 'QuickUMLS_SAMPLE_lowercase_UNQLITE'))
    @classmethod
    def setUpClass(cls):
        """Create sample db on the fly, to avoid os dependent path issue.
        """
        from .init_db import init
        quickumls_fp=init(quickumls_fp=cls.quickumls_fp)        


    def test_span_groups(self):
        """
        Test that span groups can bs used as a result type (as opposed to entities)
        """

        # let's make sure that this pipe has been initialized
        # At least for MacOS and Linux which are currently supported...

        # allow default QuickUMLS (very small sample data) to be loaded
        nlp = spacy.blank("en")

        nlp.add_pipe("medspacy_quickumls", config={"threshold": 1.0, "result_type": "group","quickumls_fp":self.quickumls_fp})

        concept_term = "dipalmitoyllecithin"

        text = "Decreased {} content found in lung specimens".format(concept_term)

        doc = nlp(text)

        assert len(doc.ents) == 0

        assert len(doc.spans[MEDSPACY_DEFAULT_SPAN_GROUP_NAME]) == 1

        span = doc.spans[MEDSPACY_DEFAULT_SPAN_GROUP_NAME][0]

        assert len(span._.umls_matches) > 0