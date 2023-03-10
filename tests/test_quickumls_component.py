import spacy
import warnings
from sys import platform
import pytest

from quickumls import spacy_component
from quickumls.constants import MEDSPACY_DEFAULT_SPAN_GROUP_NAME

class TestQuickUMLSSpangroup:
    @staticmethod
    def can_test_quickumls():
        if platform.startswith("win"):
            try:
                import quickumls_simstring
            except:
                # we're done here for now...
                return False

        return True

    def test_simple_pipeline(self):
        # let's make sure that this pipe has been initialized
        # At least for MacOS and Linux which are currently supported...

        if not TestQuickUMLSSpangroup.can_test_quickumls():
            return

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

    def test_quickumls_extractions(self):
        """
        Test that extractions can be performed using the very small (<100 concept) UMLS sample resources
        """

        # let's make sure that this pipe has been initialized
        # At least for MacOS and Linux which are currently supported...
        if not TestQuickUMLSSpangroup.can_test_quickumls():
            return

        # allow default QuickUMLS (very small sample data) to be loaded
        nlp = spacy.blank("en")

        nlp.add_pipe("medspacy_quickumls")

        doc = nlp("Decreased dipalmitoyllecithin content found in lung specimens")

        assert len(doc.ents) == 1

        entity_spans = [ent.text for ent in doc.ents]

        assert "dipalmitoyllecithin" in entity_spans

    def test_min_similarity_threshold(self):
        """
        Test that an extraction is NOT made if we set our matching to be perfect matching (100% similarity)
        and we have a typo
        """

        # let's make sure that this pipe has been initialized
        # At least for MacOS and Linux which are currently supported...
        if not TestQuickUMLSSpangroup.can_test_quickumls():
            return

        # allow default QuickUMLS (very small sample data) to be loaded
        nlp = spacy.blank("en")

        nlp.add_pipe("medspacy_quickumls", config={"threshold": 1.0})

        concept_term = "dipalmitoyllecithin"
        # Let's turn this into a typo which will no longer match...
        concept_term += 'n'

        text = "Decreased {} content found in lung specimens".format(concept_term)

        doc = nlp(text)

        assert len(doc.ents) == 0

    def test_ensure_match_objects(self):
        """
        Test that an extraction has UmlsMatch objects for it
        """

        # let's make sure that this pipe has been initialized
        # At least for MacOS and Linux which are currently supported...
        if not TestQuickUMLSSpangroup.can_test_quickumls():
            return

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

    def test_overlapping_spans(self):
        """
            Test that overlapping terms can be extracted
        """

        # let's make sure that this pipe has been initialized
        # At least for MacOS and Linux which are currently supported...
        if not TestQuickUMLSSpangroup.can_test_quickumls():
            return

        # allow default QuickUMLS (very small sample data) to be loaded
        nlp = spacy.blank("en")

        nlp.add_pipe("medspacy_quickumls", config={"threshold": 0.7,
                                                   "result_type": "group",
                                                   # do not constrain to the best match for overlapping
                                                   "best_match": False})

        # the demo data contains both of these concepts, so let's put them together
        # and allow overlap on one of the tokens
        # dipalmitoyl phosphatidylcholine
        # phosphatidylcholine, dipalmitoyl
        text = """dipalmitoyl phosphatidylcholine dipalmitoyl"""

        doc = nlp(text)

        assert len(doc.spans[MEDSPACY_DEFAULT_SPAN_GROUP_NAME]) >= 2


    @pytest.mark.skip(reason="TODO: This test succeeds if other tests do not run, but fails when they do")
    def test_custom_span_group_name(self):
        """
        Test that extractions can be made for custom span group names
        """

        # let's make sure that this pipe has been initialized
        # At least for MacOS and Linux which are currently supported...
        if not TestQuickUMLSSpangroup.can_test_quickumls():
            return

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
