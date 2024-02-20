from typing import Any, Dict, List
import srsly


class UmlsMatch:

    def __init__(self,
                 cui: str,
                 semtypes: List[str],
                 similarity: float):
        """Instantiate UmlsMatch object

                    This creates a QuickUMLS spaCy component which can be used in modular pipelines.
                    This module adds entity Spans to the document where the entity label is the UMLS CUI and the Span's "underscore" object is extended to contains "similarity" and "semtypes" for matched concepts.
                    Note that this implementation follows and enforces a known spacy convention that entity Spans cannot overlap on a single token.

                Args:
                    cui: UMLS controlled unique identifier (CUI) value (e.g., "C0243095")
                    semtypes (List[str]): List of UMLS semantic types as Type Unique Identifier values (TUI)
                            for this matched concept (e.g., "T203")
                    similarity (float): Similarity score between match and UMLS concept
                """
        self.cui = cui
        self.semtypes = semtypes
        self.similarity = similarity

    def __repr__(self):
        return f"UmlsMatch({str(self.cui), str(self.semtypes), str(self.similarity)})"

    def serialized_representation(self) -> Dict[str, Any]:
        """
        Returns the serialized representation of the UmlsMatch
        """
        return self.__dict__

    @classmethod
    def from_serialized_representation(cls, serialized_representation):
        """
        Creates the UmlsMatch from the serialized representation
        """
        return UmlsMatch(**serialized_representation)

@srsly.msgpack_encoders("umls_match")
def serialize_context_graph(obj, chain=None):
    if isinstance(obj, UmlsMatch):
        return {"umls_match": obj.serialized_representation()}
    return obj if chain is None else chain(obj)


@srsly.msgpack_decoders("umls_match")
def deserialize_context_graph(obj, chain=None):
    if "umls_match" in obj:
        return UmlsMatch.from_serialized_representation(obj["umls_match"])
    return obj if chain is None else chain(obj)
