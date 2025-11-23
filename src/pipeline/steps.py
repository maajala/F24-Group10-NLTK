from abc import ABC, abstractmethod
from typing import List, Tuple, Any
from .document import TextDocument
from .errors import InvalidPipelineError

# Import NLTK interfaces for type hinting (TokenizerI, TaggerI, ParserI)
from nltk.tokenize.api import TokenizerI
from nltk.tag.api import TaggerI
from nltk.parse.api import ParserI

class PipelineStep(ABC):
    """
    Abstract base class for a processing step in the pipeline.
    Subclasses implement specific NLP processing (tokenization, tagging, parsing) 
    and modify the TextDocument accordingly.
    """
    @abstractmethod
    def process(self, doc: TextDocument) -> None:
        """
        Process the given TextDocument in-place.
        Each PipelineStep reads from and/or writes to specific fields of the TextDocument.
        This method should be implemented by concrete subclasses.
        """
        pass

class TokenizerStep(PipelineStep):
    """
    A PipelineStep that wraps an NLTK tokenizer (TokenizerI).
    It tokenizes the document's text and stores the tokens in TextDocument.tokens.
    """
    def __init__(self, tokenizer: TokenizerI):
        """
        Initialize with a tokenizer that implements nltk.tokenize.TokenizerI.
        """
        self.tokenizer = tokenizer

    def process(self, doc: TextDocument) -> None:
        """
        Tokenize doc.text and store the list of tokens in doc.tokens.
        Clears any existing tags or parse tree since they become outdated after tokenization.
        """
        # Tokenize the raw text
        doc.tokens = self.tokenizer.tokenize(doc.text)
        # Reset downstream data after tokenization (tags and parse tree are no longer valid)
        doc.tags = []
        doc.parse_tree = None

class TaggerStep(PipelineStep):
    """
    A PipelineStep that wraps an NLTK tagger (TaggerI).
    It tags the document's tokens with part-of-speech tags and stores the result in TextDocument.tags.
    """
    def __init__(self, tagger: TaggerI):
        """
        Initialize with a tagger that implements nltk.tag.TaggerI.
        """
        self.tagger = tagger

    def process(self, doc: TextDocument) -> None:
        """
        Tag doc.tokens with part-of-speech tags and store the (token, tag) pairs in doc.tags.
        Requires that doc.tokens is already populated (e.g., via a TokenizerStep).
        """
        # Ensure that there are tokens to tag
        if not doc.tokens:
            raise InvalidPipelineError("TaggerStep cannot run because TextDocument.tokens is empty.")
        # Tag the tokens using the provided tagger
        doc.tags = self.tagger.tag(doc.tokens)
        # Reset parse tree because it depends on the new tags
        doc.parse_tree = None

class ParserStep(PipelineStep):
    """
    A PipelineStep that wraps an NLTK parser (ParserI).
    It parses the document's tokens (or tagged tokens) and stores the resulting parse tree(s) in TextDocument.parse_tree.
    """
    def __init__(self, parser: ParserI):
        """
        Initialize with a parser that implements nltk.parse.ParserI.
        """
        self.parser = parser

    def process(self, doc: TextDocument) -> None:
        """
        Parse the document's content using the parser and store the result in doc.parse_tree.
        If doc.tags is non-empty, the parser will use the tagged tokens; otherwise it will use the raw tokens.
        Raises InvalidPipelineError if neither tokens nor tags are available, or if parsing fails.
        Note: If the parser produces multiple parses (ambiguity), all parse trees are stored as a list 
        in doc.parse_tree. If only one parse tree is produced, it is stored directly as an NLTK Tree.
        """
        # Ensure there are tokens or tagged tokens to parse
        if not doc.tokens and not doc.tags:
            raise InvalidPipelineError("ParserStep cannot run because there are no tokens or tags in TextDocument.")
        try:
            # Determine input for parser: use tagged tokens if available, else use tokens
            input_data = doc.tags if doc.tags else doc.tokens
            parse_result = self.parser.parse(input_data)
        except Exception as e:
            # Catch any parser exceptions and wrap in a pipeline error
            raise InvalidPipelineError(f"ParserStep failed to parse input: {e}")

        # Determine whether parser returned an iterable or a single parse tree
        from nltk.tree import Tree
        if parse_result is None:
            parse_trees = []
        elif isinstance(parse_result, Tree):
            parse_trees = [parse_result]
        else:
            parse_trees = list(parse_result) if parse_result is not None else []

        # Check if any parse trees were produced
        if len(parse_trees) == 0:
            # No parse tree was produced by the parser
            raise InvalidPipelineError("ParserStep did not produce any parse tree for the given input.")
        elif len(parse_trees) == 1:
            # Exactly one parse tree produced
            doc.parse_tree = parse_trees[0]
        else:
            # Multiple parse trees produced (ambiguous parse)
            doc.parse_tree = parse_trees
