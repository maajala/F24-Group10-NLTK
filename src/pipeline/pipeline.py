from .steps import PipelineStep, TokenizerStep, TaggerStep, ParserStep
from .document import TextDocument
from .errors import InvalidPipelineError

class Pipeline:
    """
    Represents an ordered collection of PipelineStep objects (e.g., tokenizer, tagger, parser).
    Provides methods to manage these steps.
    """
    def __init__(self, steps=None):
        """
        Initialize a Pipeline with an optional list of PipelineStep instances.
        """
        self.steps = list(steps) if steps is not None else []

    def add_step(self, step: PipelineStep) -> None:
        """
        Add a PipelineStep to the end of the pipeline.
        """
        self.steps.append(step)

    def remove_step(self, step: PipelineStep) -> None:
        """
        Remove the given PipelineStep from the pipeline.
        Raises ValueError if the step is not found in the pipeline.
        """
        self.steps.remove(step)

    def __iter__(self):
        """Enable iteration over the pipeline steps in order."""
        return iter(self.steps)

    def __len__(self):
        """Return the number of steps in the pipeline."""
        return len(self.steps)

    def __getitem__(self, index):
        """Allow indexing to get a specific PipelineStep."""
        return self.steps[index]

class PipelineController:
    """
    Controller class that manages execution of a Pipeline on a TextDocument.
    It validates the pipeline configuration, executes each step in order, and handles errors.
    """
    def __init__(self, pipeline: Pipeline):
        """
        Initialize the controller with a Pipeline to execute.
        """
        self.pipeline = pipeline

    def run(self, doc: TextDocument) -> TextDocument:
        """
        Execute the pipeline on the given TextDocument.
        Performs validation before execution, then sequentially applies each PipelineStep to the document.
        If any step fails or the configuration is invalid, an InvalidPipelineError is raised.
        Returns the TextDocument after all processing steps have been applied.
        """
        # Validate pipeline configuration and data dependencies before execution
        self._validate_pipeline(doc)

        # Sequentially apply each step to the document
        for step in self.pipeline:
            try:
                step.process(doc)
            except Exception as e:
                # Wrap or propagate exceptions as InvalidPipelineError for clear diagnostics
                if isinstance(e, InvalidPipelineError):
                    # Pipeline-specific error (already descriptive), propagate it
                    raise e
                else:
                    # Wrap other exceptions with context about which step failed
                    raise InvalidPipelineError(f"Error in {step.__class__.__name__}: {e}")
        # Return the document with all processing results populated
        return doc

    def _validate_pipeline(self, doc: TextDocument) -> None:
        """
        Internal helper to validate that the pipeline steps are in a logical order and compatible with the TextDocument.
        Checks ordering (Tokenizer before Tagger, Tagger before Parser) and initial document state for first step.
        Raises InvalidPipelineError if the pipeline configuration is invalid for the given document.
        """
        steps = self.pipeline.steps
        if not steps:
            raise InvalidPipelineError("Pipeline is empty and has no steps to execute.")

        # Track the first occurrence of each step type
        idx_tokenizer = idx_tagger = idx_parser = None
        for i, step in enumerate(steps):
            if isinstance(step, TokenizerStep):
                if idx_tokenizer is None:
                    idx_tokenizer = i
                else:
                    raise InvalidPipelineError("Pipeline contains multiple TokenizerStep instances, which is not supported.")
            elif isinstance(step, TaggerStep):
                if idx_tagger is None:
                    idx_tagger = i
                else:
                    raise InvalidPipelineError("Pipeline contains multiple TaggerStep instances, which is not supported.")
            elif isinstance(step, ParserStep):
                if idx_parser is None:
                    idx_parser = i
                else:
                    raise InvalidPipelineError("Pipeline contains multiple ParserStep instances, which is not supported.")

        # Enforce logical ordering: Tokenizer -> Tagger -> Parser
        if idx_tokenizer is not None and idx_tagger is not None and idx_tokenizer > idx_tagger:
            raise InvalidPipelineError("TokenizerStep must come before TaggerStep in the pipeline.")
        if idx_tokenizer is not None and idx_parser is not None and idx_tokenizer > idx_parser:
            raise InvalidPipelineError("TokenizerStep must come before ParserStep in the pipeline.")
        if idx_tagger is not None and idx_parser is not None and idx_tagger > idx_parser:
            raise InvalidPipelineError("TaggerStep must come before ParserStep in the pipeline.")

        # Check initial document state for the first step in the pipeline
        first_step = steps[0]
        if isinstance(first_step, TaggerStep):
            # If the pipeline starts with a Tagger, ensure the document already has tokens
            if not doc.tokens:
                raise InvalidPipelineError("Pipeline starts with TaggerStep, but TextDocument.tokens is empty (no tokens to tag).")
        elif isinstance(first_step, ParserStep):
            # If the pipeline starts with a Parser, ensure the document has tokens or tags to parse
            if not doc.tokens and not doc.tags:
                raise InvalidPipelineError("Pipeline starts with ParserStep, but TextDocument has no tokens or tags to parse.")

        # If there is no TokenizerStep at all, ensure the document provides tokens for Tagger or Parser steps
        if idx_tokenizer is None:
            if idx_tagger is not None and not doc.tokens:
                raise InvalidPipelineError("No TokenizerStep in pipeline, but a TaggerStep is present and TextDocument.tokens is empty.")
            if idx_parser is not None and not doc.tokens and not doc.tags:
                raise InvalidPipelineError("No TokenizerStep in pipeline, but a ParserStep is present and TextDocument has no tokens or tags.")
