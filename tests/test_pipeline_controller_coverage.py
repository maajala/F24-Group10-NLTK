import unittest
from unittest.mock import MagicMock
from src.pipeline.pipeline import Pipeline, PipelineController
from src.pipeline.steps import PipelineStep, TokenizerStep, TaggerStep, ParserStep
from src.pipeline.document import TextDocument
from src.pipeline.errors import InvalidPipelineError

class TestPipelineControllerCoverage(unittest.TestCase):
    """
    Advanced White Box Testing for PipelineController.
    Goal: Achieve 100% Branch Coverage by exercising all validation logic and error handling.
    """

    def setUp(self):
        self.doc = TextDocument("Test text")
        # Create mocks for steps
        self.mock_tokenizer = MagicMock(spec=TokenizerStep)
        self.mock_tagger = MagicMock(spec=TaggerStep)
        self.mock_parser = MagicMock(spec=ParserStep)
        # Ensure isinstance checks work by mocking the class logic if necessary, 
        # or simply using the real classes with mocked methods if specs fail.
        # For this test, using instances of the real classes is safer for isinstance checks.
        self.real_tokenizer = TokenizerStep(MagicMock())
        self.real_tagger = TaggerStep(MagicMock())
        self.real_parser = ParserStep(MagicMock())

    def test_validate_empty_pipeline(self):
        """Test validation fails when pipeline has no steps."""
        pipeline = Pipeline([])
        controller = PipelineController(pipeline)
        with self.assertRaisesRegex(InvalidPipelineError, "Pipeline is empty"):
            controller.run(self.doc)

    def test_validate_multiple_tokenizers(self):
        """Test validation fails with multiple TokenizerSteps."""
        pipeline = Pipeline([self.real_tokenizer, self.real_tokenizer])
        controller = PipelineController(pipeline)
        with self.assertRaisesRegex(InvalidPipelineError, "multiple TokenizerStep"):
            controller.run(self.doc)

    def test_validate_multiple_taggers(self):
        """Test validation fails with multiple TaggerSteps."""
        pipeline = Pipeline([self.real_tagger, self.real_tagger])
        controller = PipelineController(pipeline)
        with self.assertRaisesRegex(InvalidPipelineError, "multiple TaggerStep"):
            controller.run(self.doc)

    def test_validate_multiple_parsers(self):
        """Test validation fails with multiple ParserSteps."""
        pipeline = Pipeline([self.real_parser, self.real_parser])
        controller = PipelineController(pipeline)
        with self.assertRaisesRegex(InvalidPipelineError, "multiple ParserStep"):
            controller.run(self.doc)

    def test_validate_order_tokenizer_after_tagger(self):
        """Test validation fails if Tokenizer comes after Tagger."""
        pipeline = Pipeline([self.real_tagger, self.real_tokenizer])
        controller = PipelineController(pipeline)
        # Note: We must ensure doc has tokens so it doesn't fail the 'first step' check
        self.doc.tokens = ["some", "tokens"] 
        with self.assertRaisesRegex(InvalidPipelineError, "TokenizerStep must come before TaggerStep"):
            controller.run(self.doc)

    def test_validate_order_tokenizer_after_parser(self):
        """Test validation fails if Tokenizer comes after Parser."""
        pipeline = Pipeline([self.real_parser, self.real_tokenizer])
        controller = PipelineController(pipeline)
        self.doc.tokens = ["tokens"]
        self.doc.tags = [("token", "tag")]
        with self.assertRaisesRegex(InvalidPipelineError, "TokenizerStep must come before ParserStep"):
            controller.run(self.doc)

    def test_validate_order_tagger_after_parser(self):
        """Test validation fails if Tagger comes after Parser."""
        pipeline = Pipeline([self.real_parser, self.real_tagger])
        controller = PipelineController(pipeline)
        self.doc.tokens = ["tokens"]
        self.doc.tags = [("token", "tag")]
        with self.assertRaisesRegex(InvalidPipelineError, "TaggerStep must come before ParserStep"):
            controller.run(self.doc)

    def test_validate_first_step_tagger_no_tokens(self):
        """Test validation fails if first step is Tagger but doc has no tokens."""
        pipeline = Pipeline([self.real_tagger])
        controller = PipelineController(pipeline)
        self.doc.tokens = [] # Empty tokens
        with self.assertRaisesRegex(InvalidPipelineError, "Pipeline starts with TaggerStep, but TextDocument.tokens is empty"):
            controller.run(self.doc)

    def test_validate_first_step_parser_no_data(self):
        """Test validation fails if first step is Parser but doc has no tokens/tags."""
        pipeline = Pipeline([self.real_parser])
        controller = PipelineController(pipeline)
        self.doc.tokens = []
        self.doc.tags = []
        with self.assertRaisesRegex(InvalidPipelineError, "Pipeline starts with ParserStep, but TextDocument has no tokens"):
            controller.run(self.doc)

    def test_validate_missing_tokenizer_gap(self):
        """Test validation fails if Tagger is present without a Tokenizer, and doc is empty."""
        # Create a dummy step to be first, so Tagger is second, triggering the 'no tokenizer' check logic
        class DummyStep(PipelineStep):
            def process(self, doc): pass
        
        pipeline = Pipeline([DummyStep(), self.real_tagger])
        controller = PipelineController(pipeline)
        self.doc.tokens = []
        with self.assertRaisesRegex(InvalidPipelineError, "No TokenizerStep in pipeline, but a TaggerStep is present"):
            controller.run(self.doc)

    def test_run_execution_success(self):
        """Test successful execution of all steps."""
        # Mock the process methods to verify they are called
        t_mock = MagicMock(spec=TokenizerStep)
        p_mock = MagicMock(spec=TaggerStep)
        pipeline = Pipeline([t_mock, p_mock])
        controller = PipelineController(pipeline)
        
        controller.run(self.doc)
        t_mock.process.assert_called_once_with(self.doc)
        p_mock.process.assert_called_once_with(self.doc)

    def test_run_propagates_invalid_pipeline_error(self):
        """Test that existing InvalidPipelineErrors are re-raised as-is."""
        step_mock = MagicMock(spec=TokenizerStep)
        step_mock.process.side_effect = InvalidPipelineError("Already descriptive")
        
        pipeline = Pipeline([step_mock])
        controller = PipelineController(pipeline)
        
        with self.assertRaisesRegex(InvalidPipelineError, "Already descriptive"):
            controller.run(self.doc)

    def test_run_wraps_generic_exception(self):
        """Test that generic exceptions are wrapped in InvalidPipelineError."""
        step_mock = MagicMock(spec=TokenizerStep)
        step_mock.process.side_effect = ValueError("Random crash")
        
        pipeline = Pipeline([step_mock])
        controller = PipelineController(pipeline)
        
        with self.assertRaisesRegex(InvalidPipelineError, "Error in MagicMock: Random crash"):
            controller.run(self.doc)

if __name__ == "__main__":
    unittest.main()
