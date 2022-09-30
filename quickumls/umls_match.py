from typing import Set


class UmlsMatch:

    def __init__(self,
                 cui: str,
                 semtypes: Set[str],
                 similarity: float):
        """Instantiate UmlsMatch object

                    This creates a QuickUMLS spaCy component which can be used in modular pipelines.
                    This module adds entity Spans to the document where the entity label is the UMLS CUI and the Span's "underscore" object is extended to contains "similarity" and "semtypes" for matched concepts.
                    Note that this implementation follows and enforces a known spacy convention that entity Spans cannot overlap on a single token.

                Args:
                    cui: UMLS controlled unique identifier (CUI) value (e.g., "C0243095")
                    semtypes (Set[str]): List of UMLS semantic types as Type Unique Identifier values (TUI)
                            for this matched concept (e.g., "T203")
                    similarity (float): Similarity score between match and UMLS concept
                """
        self.cui = cui
        self.semtypes = semtypes
        self.similarity = similarity
