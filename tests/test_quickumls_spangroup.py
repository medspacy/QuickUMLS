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


    def test_span_groups(self):
        """
        Test that span groups can bs used as a result type (as opposed to entities)
        """

        # let's make sure that this pipe has been initialized
        # At least for MacOS and Linux which are currently supported...
        if not TestQuickUMLSSpangroup.can_test_quickumls():
            return

        # allow default QuickUMLS (very small sample data) to be loaded
        nlp = spacy.blank("en")

        nlp.add_pipe("medspacy_quickumls", config={"threshold": 1.0, "result_type": "group"})

        concept_term = "dipalmitoyllecithin"

        text = "Decreased {} content found in lung specimens".format(concept_term)

        doc = nlp(text)

        assert len(doc.ents) == 0

        assert len(doc.spans[MEDSPACY_DEFAULT_SPAN_GROUP_NAME]) == 1

        span = doc.spans[MEDSPACY_DEFAULT_SPAN_GROUP_NAME][0]

        assert len(span._.umls_matches) > 0

    def test_multiword_entity(self):
        """
        Test that an extraction can be made on a concept with multiple words
        """

        # let's make sure that this pipe has been initialized
        # At least for MacOS and Linux which are currently supported...
        if not TestQuickUMLSSpangroup.can_test_quickumls():
            return

        # allow default QuickUMLS (very small sample data) to be loaded
        nlp = spacy.blank("en")

        nlp.add_pipe("medspacy_quickumls", config={"threshold": 0.7, "result_type": "group"})

        # the demo data contains this concept:
        # dipalmitoyl phosphatidylcholine
        text = """dipalmitoyl phosphatidylcholine"""

        doc = nlp(text)

        assert len(doc.spans[MEDSPACY_DEFAULT_SPAN_GROUP_NAME]) == 1


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
