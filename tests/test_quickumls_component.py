import unittest

import spacy
import warnings
from sys import platform
import pytest

from quickumls import spacy_component

class TestQuickUMLSSpangroup(unittest.TestCase):

    def test_simple_pipeline(self):
        # let's make sure that this pipe has been initialized
        # At least for MacOS and Linux which are currently supported...

        # allow default QuickUMLS (very small sample data) to be loaded
        nlp = spacy.blank("en")

        nlp.add_pipe("medspacy_quickumls")

        assert nlp

        quickumls = nlp.get_pipe("medspacy_quickumls")

        assert quickumls
        # this is a member of the QuickUMLS algorithm inside the component
        assert quickumls.quickumls
        # Check that the simstring database exists
        assert quickumls.quickumls.ss_db



    def test_min_similarity_threshold(self):
        """
        Test that an extraction is NOT made if we set our matching to be perfect matching (100% similarity)
        and we have a typo
        """

        # let's make sure that this pipe has been initialized
        # At least for MacOS and Linux which are currently supported...

        # allow default QuickUMLS (very small sample data) to be loaded
        nlp = spacy.blank("en")

        nlp.add_pipe("medspacy_quickumls", config={"threshold": 1.0})

        concept_term = "dipalmitoyllecithin"
        # Let's turn this into a typo which will no longer match...
        concept_term += 'n'

        text = "Decreased {} content found in lung specimens".format(concept_term)

        doc = nlp(text)
        comp = nlp.get_pipe('medspacy_quickumls')
        print(comp.result_type)

        assert len(doc.ents) == 0


        nlp = spacy.blank("en")

        nlp.add_pipe("medspacy_quickumls", config={"threshold": .9})

        doc = nlp(text)


        assert len(doc.ents) == 1

    def test_ensure_match_objects(self):
        """
        Test that an extraction has UmlsMatch objects for it
        """

        # let's make sure that this pipe has been initialized
        # At least for MacOS and Linux which are currently supported...


        # allow default QuickUMLS (very small sample data) to be loaded
        nlp = spacy.blank("en")

        nlp.add_pipe("medspacy_quickumls", config={"threshold": 1.0})

        concept_term = "dipalmitoyllecithin"

        text = "Decreased {} content found in lung specimens".format(concept_term)

        doc = nlp(text)
        assert len(doc.ents) == 1

        ent = doc.ents[0]

        assert len(ent._.umls_matches) > 0

        # make sure that we have a reasonable looking CUI
        match_object = list(ent._.umls_matches)[0]

        assert match_object.cui.startswith("C")


