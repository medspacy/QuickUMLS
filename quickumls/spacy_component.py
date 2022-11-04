from sys import platform
from os import path
from pathlib import Path
from typing import Literal

import spacy
from spacy.tokens import Span
from spacy.strings import StringStore
from spacy.language import Language

from .core import QuickUMLS
from . import constants
from .umls_match import UmlsMatch
from .constants import MEDSPACY_DEFAULT_SPAN_GROUP_NAME

@Language.factory("medspacy_quickumls")
class SpacyQuickUMLS(object):

    def __init__(self, nlp, name = "medspacy_quickumls", quickumls_fp=None,
                 overlapping_criteria='score',
                 threshold=0.7,
                 window=5,
                 similarity_name='jaccard',
                 min_match_length=3,
                 accepted_semtypes=constants.ACCEPTED_SEMTYPES,
                 verbose=False,
                 keep_uppercase=False,
                 best_match=True,
                 ignore_syntax=False,
                 result_type: Literal["ents", "group"] = "ents",
                 span_group_name: str = MEDSPACY_DEFAULT_SPAN_GROUP_NAME,
                 ):
        """Instantiate SpacyQuickUMLS object

            This creates a QuickUMLS spaCy component which can be used in modular pipelines.  
            This module adds either entity Spans (default) or Span Groups to the document where the  label is the UMLS CUI and the Span's
                "underscore" object is extended to contain additional information about matched concepts.
            Note that this implementation follows and enforces a known spacy convention on entities
                that entity Spans cannot overlap on a single token.  If SpanGroups are selected instead, they may overlap

        Args:
            nlp: Existing spaCy pipeline.  This is needed to update the vocabulary with UMLS CUI values
            quickumls_fp (str): Path to QuickUMLS data
            overlapping_criteria (str, optional):
                    One of "score" or "length". Choose how results are ranked.
                    Choose "score" for best matching score first or "length" for longest match first.. Defaults to 'score'.
            threshold (float, optional): Minimum similarity between strings. Defaults to 0.7.
            window (int, optional): Maximum amount of tokens to consider for matching. Defaults to 5.
            similarity_name (str, optional): One of "dice", "jaccard", "cosine", or "overlap".
                    Similarity measure to be used. Defaults to 'jaccard'.
            min_match_length (int, optional): TODO: ??. Defaults to 3.
            accepted_semtypes (List[str], optional): Set of UMLS semantic types concepts should belong to.
                Semantic types are identified by the letter "T" followed by three numbers
                (e.g., "T131", which identifies the type "Hazardous or Poisonous Substance").
                Defaults to constants.ACCEPTED_SEMTYPES.
            verbose (bool, optional): TODO:??. Defaults to False.
            keep_uppercase (bool, optional): By default QuickUMLS converts all
                    uppercase strings to lowercase. This option disables that
                    functionality, which makes QuickUMLS useful for
                    distinguishing acronyms from normal words. For this the
                    database should be installed without the -L option.
                    Defaults to False.
            best_match (bool, optional): Whether to return only the top match or all overlapping candidates. Defaults to True.
            ignore_syntax (bool, optional): Whether to use the heuristcs introduced in the paper (Soldaini and Goharian, 2016). TODO: clarify,. Defaults to False
            result_type: "ents" (default), or "group". Determines where component will put the matched spans.
                "ents" will add spans to doc.ents and add to any existing entities, but does not allow overlapping.
                "group" will add spans to doc.spans under the specified group name.
            span_group_name: The name of the span group used to store results when result_type is "group". Default is
                "medspacy_spans".
        """

        if quickumls_fp is None:
            # let's use a default sample that we provide in medspacy
            # NOTE: Currently QuickUMLS uses an older fork of simstring where databases
            # cannot be shared between Windows and POSIX systems so we distribute the sample for both:

            quickumls_platform_dir = "QuickUMLS_SAMPLE_lowercase_POSIX_unqlite"
            if platform.startswith("win"):
                quickumls_platform_dir = "QuickUMLS_SAMPLE_lowercase_Windows_unqlite"

            quickumls_fp = path.join(
                Path(__file__).resolve().parents[1], "resources", "quickumls/{0}".format(quickumls_platform_dir)
            )
            print("Loading QuickUMLS resources from a default SAMPLE of UMLS data from here: {}".format(quickumls_fp))
        
        self.quickumls = QuickUMLS(quickumls_fp, 
            # By default, the QuickUMLS objects creates its own internal spacy pipeline but this is not needed
            # when we're using it as a component in a pipeline
            spacy_component = True,
            overlapping_criteria=overlapping_criteria,
            threshold=threshold,
            window=window,
            similarity_name=similarity_name,
            min_match_length=min_match_length,
            accepted_semtypes=accepted_semtypes,
            verbose=verbose,
            keep_uppercase=keep_uppercase
            )
        
        # save this off so that we can get vocab values of labels later
        self.nlp = nlp
        self.name = name
        
        # keep these for matching
        self.best_match = best_match
        self.ignore_syntax = ignore_syntax
        self.verbose = verbose

        self._result_type = result_type
        self._span_group_name = span_group_name

        # let's extend this with some proprties that we want
        # NOTE: These two might be deprecated at some point since we now have
        # umls_matches below which contains more information and enables overlapping
        if not Span.has_extension("similarity"):
            Span.set_extension('similarity', default = -1.0)
        if not Span.has_extension("semtypes"): 
            Span.set_extension('semtypes', default = -1.0)

        # match objects are a set, since span objects with the same start/end keys
        # would have the same values for custom attributes in spacy
        if not Span.has_extension("umls_matches"):
            Span.set_extension('umls_matches', default=set())

    @property
    def result_type(self) -> str:
        """
        The result type of the component. "ents" indicates that calling TargetMatcher will store the results in
        doc.ents, "group" indicates that the results will be stored in the span group indicated by `span_group_name`,

        Returns:
            The result type string.
        """
        return self._result_type

    @result_type.setter
    def result_type(self, result_type: Literal["ents", "group"]):
        if not (result_type == "group" or result_type == "ents"):
            raise ValueError('result_type must be "ents", or "group".')
        self._result_type = result_type

    @property
    def span_group_name(self) -> str:
        """
        The name of the span group used by this component. If `result_type` is "group", calling this component will
        place results in the span group with this name.

        Returns:
            The span group name.
        """
        return self._span_group_name

    @span_group_name.setter
    def span_group_name(self, name: str):
        if not name or not isinstance(name, str):
            raise ValueError("Span group name must be a string.")
        self._span_group_name = name
        
    def __call__(self, doc):
        # pass in the document which has been parsed to this point in the pipeline for ngrams and matches
        matches = self.quickumls._match(doc, best_match=self.best_match, ignore_syntax=self.ignore_syntax)
        
        # NOTE: Spacy spans do not allow overlapping tokens, so we prevent the overlap here
        # For more information, see: https://github.com/explosion/spaCy/issues/3608
        tokens_in_ents_set = set()

        if self.result_type.lower() == "group":
            # set up an empty list if there are no spans yet
            doc.spans.setdefault(self.span_group_name, [])
        
        # let's track any other entities which may have been attached via upstream components
        for ent in doc.ents:
            for token_index in range(ent.start, ent.end):
                tokens_in_ents_set.add(token_index)
        
        # Convert QuickUMLS match objects into Spans
        for match in matches:
            # each match may match multiple ngrams
            for ngram_match_dict in match:
                start_char_idx = int(ngram_match_dict['start'])
                end_char_idx = int(ngram_match_dict['end'])
                
                cui = ngram_match_dict['cui']
                # add the string to the spacy vocab
                self.nlp.vocab.strings.add(cui)
                # pull out the value
                cui_label_value = self.nlp.vocab.strings[cui]
                
                # char_span() creates a Span from these character indices
                # UMLS CUI should work well as the label here
                span = doc.char_span(start_char_idx, end_char_idx, label = cui_label_value)
                
                # before we add this, let's make sure that this entity does not overlap any tokens added thus far
                candidate_token_indexes = set(range(span.start, span.end))
                
                # check the intersection and skip this if there is any overlap
                if self.result_type.lower() == "ents" and len(tokens_in_ents_set.intersection(candidate_token_indexes)) > 0:
                    continue
                    
                # track this to make sure we do not introduce overlap later
                tokens_in_ents_set.update(candidate_token_indexes)
                
                # add some custom metadata to the spans
                span._.similarity = ngram_match_dict['similarity']
                span._.semtypes = ngram_match_dict['semtypes']

                # let's create this more fully featured match object
                umls_match = UmlsMatch(cui,
                                       ngram_match_dict['semtypes'],
                                       ngram_match_dict['similarity'])

                span._.umls_matches.add(umls_match)

                if self.result_type.lower() == "ents":
                    doc.ents = list(doc.ents) + [span]
                elif self.result_type.lower() == "group":
                    doc.spans[self.span_group_name].append(span)
                
        return doc
