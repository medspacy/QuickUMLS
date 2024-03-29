import unittest

import spacy
import warnings
from sys import platform
import pytest
from pathlib import Path
from quickumls import spacy_component

class TestQuickUMLSSpangroup(unittest.TestCase):

    quickumls_fp=str(Path('output', 'QuickUMLS_SAMPLE_lowercase_UNQLITE'))
    @classmethod
    def setUpClass(cls):
        """Create sample db on the fly, to avoid os dependent path issue.
        """
        from .init_db import init
        quickumls_fp=init(quickumls_fp=cls.quickumls_fp)  

    def test_simple_pipeline(self):
        # let's make sure that this pipe has been initialized
        # At least for MacOS and Linux which are currently supported...

        # allow default QuickUMLS (very small sample data) to be loaded
        nlp = spacy.blank("en")

        nlp.add_pipe("medspacy_quickumls",config={"quickumls_fp":self.quickumls_fp})

        assert nlp

        quickumls = nlp.get_pipe("medspacy_quickumls")

        print(quickumls.quickumls.info)

        assert quickumls
        # this is a member of the QuickUMLS algorithm inside the component
        assert quickumls.quickumls
        # Check that the simstring database exists
        assert quickumls.quickumls.ss_db





    def test_ensure_match_objects(self):
        """
        Test that an extraction has UmlsMatch objects for it
        """

        # let's make sure that this pipe has been initialized
        # At least for MacOS and Linux which are currently supported...


        # allow default QuickUMLS (very small sample data) to be loaded
        nlp = spacy.blank("en")

        nlp.add_pipe("medspacy_quickumls", config={"threshold": 1.0, "quickumls_fp":self.quickumls_fp})

        pathexist=Path(self.quickumls_fp).exists()
        print(self.quickumls_fp, pathexist)

        concept_term = "dipalmitoyllecithin"

        text = "Decreased {} content found in lung specimens".format(concept_term)

        doc = nlp(text)
        assert len(doc.ents) == 1

        ent = doc.ents[0]

        assert len(ent._.umls_matches) > 0

        # make sure that we have a reasonable looking CUI
        match_object = list(ent._.umls_matches)[0]

        assert match_object.cui.startswith("C")


