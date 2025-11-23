from typing import List, Tuple, Any

class TextDocument:
    """
    Represents a text document being processed in the pipeline.
    It holds the original text and fields for tokens, tags, and parse tree results.
    """
    def __init__(self, text: str):
        """
        Initialize a TextDocument with raw text.
        The tokens, tags, and parse_tree fields are initialized to empty.
        """
        self.text: str = text
        self.tokens: List[str] = []
        self.tags: List[Tuple[str, str]] = []
        self.parse_tree: Any = None
