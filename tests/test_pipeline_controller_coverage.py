import unittest
from unittest.mock import MagicMock
from pipeline.pipeline import Pipeline, PipelineController
from pipeline.steps import PipelineStep, TokenizerStep, TaggerStep, ParserStep
from pipeline.document import TextDocument
from pipeline.errors import InvalidPipelineError


class TestPipelineControllerCoverage(unittest.TestCase):
    """
    Comprehensive white-box testing for PipelineController to achieve full
    branch and line coverage of pipeline validation and execution logic.
    """

    def setUp(self):
        self.doc = TextDocument("Test text")

        # Real step instances (for correct isinstance behavior)
        self.real_tokenizer = TokenizerStep(MagicMock())
        self.real_tagger = TaggerStep(MagicMock())
        self.real_parser = ParserStep(MagicMock())

    # ----------------------------------------------------------------------
    # VALIDATION TESTS
    # ----------------------------------------------------------------------

    def test_validate_empty_pipeline(self):
        """Pipeline must not accept empty step lists."""
        pipeline = Pipeline([])
        controller = PipelineController(pipeline)
        with self.assertRaisesRegex(InvalidPipelineError, "Pipeline is empty"):
            controller.run(self.doc)

    def test_validate_multiple_tokenizers(self):
        """Only one TokenizerStep allowed."""
        pipeline = Pipeline([self.real_tokenizer, self.real_tokenizer])
        controller = PipelineController(pipeline)
        with self.assertRaisesRegex(InvalidPipelineError, "multiple TokenizerStep"):
            controller.run(self.doc)

    def test_validate_multiple_taggers(self):
        """Only one TaggerStep allowed."""
        pipeline = Pipeline([self.real_tagger, self.real_tagger])
        controller = PipelineController(pipeline)
        with self.assertRaisesRegex(InvalidPipelineError, "multiple TaggerStep"):
            controller.run(self.doc)

    def test_validate_multiple_parsers(self):
        """Only one ParserStep allowed."""
        pipeline = Pipeline([self.real_parser, self.real_parser])
        controller = PipelineController(pipeline)
        with self.assertRaisesRegex(InvalidPipelineError, "multiple ParserStep"):
            controller.run(self.doc)

    def test_validate_order_tokenizer_after_tagger(self):
        """Tokenizer must come before Tagger."""
        self.doc.tokens = ["tokens"]  # prevent first-step failure
        pipeline = Pipeline([self.real_tagger, self.real_tokenizer])
        controller = PipelineController(pipeline)
        with self.assertRaisesRegex(InvalidPipelineError, "TokenizerStep must come before TaggerStep"):
            controller.run(self.doc)

    def test_validate_order_tokenizer_after_parser(self):
        """Tokenizer must come before Parser."""
        self.doc.tokens = ["tokens"]
        self.doc.tags = [("t", "TAG")]
        pipeline = Pipeline([self.real_parser, self.real_tokenizer])
        controller = PipelineController(pipeline)
        with self.assertRaisesRegex(InvalidPipelineError, "TokenizerStep must come before ParserStep"):
            controller.run(self.doc)

    def test_validate_order_tagger_after_parser(self):
        """Tagger must come before Parser."""
        self.doc.tokens = ["tokens"]
        self.doc.tags = [("t", "TAG")]
        pipeline = Pipeline([self.real_parser, self.real_tagger])
        controller = PipelineController(pipeline)
        with self.assertRaisesRegex(InvalidPipelineError, "TaggerStep must come before ParserStep"):
            controller.run(self.doc)

    def test_validate_first_step_tagger_no_tokens(self):
        """Cannot start with Tagger if document has no tokens."""
        self.doc.tokens = []
        pipeline = Pipeline([self.real_tagger])
        controller = PipelineController(pipeline)
        with self.assertRaisesRegex(InvalidPipelineError, "Pipeline starts with TaggerStep"):
            controller.run(self.doc)

    def test_validate_first_step_parser_no_data(self):
        """Cannot start with Parser if document has no tokens or tags."""
        self.doc.tokens = []
        self.doc.tags = []
        pipeline = Pipeline([self.real_parser])
        controller = PipelineController(pipeline)
        with self.assertRaisesRegex(InvalidPipelineError, "Pipeline starts with ParserStep"):
            controller.run(self.doc)

    def test_validate_missing_tokenizer_gap(self):
        """
        If a Tagger appears in the pipeline without a Tokenizer before it,
        the pipeline must reject the configuration.
        """
        class DummyStep(PipelineStep):
            def process(self, doc): pass

        self.doc.tokens = []  # ensure missing-tokenization failure
        pipeline = Pipeline([DummyStep(), self.real_tagger])
        controller = PipelineController(pipeline)
        with self.assertRaisesRegex(InvalidPipelineError, "No TokenizerStep in pipeline"):
            controller.run(self.doc)

    # ----------------------------------------------------------------------
    # EXECUTION TESTS
    # ----------------------------------------------------------------------

    def test_run_execution_success(self):
        """Successful pipelines should call each step exactly once."""
        t_mock = MagicMock(spec=TokenizerStep)
        g_mock = MagicMock(spec=TaggerStep)

        pipeline = Pipeline([t_mock, g_mock])
        controller = PipelineController(pipeline)

        controller.run(self.doc)

        t_mock.process.assert_called_once_with(self.doc)
        g_mock.process.assert_called_once_with(self.doc)

    def test_run_propagates_invalid_pipeline_error(self):
        """Existing InvalidPipelineErrors must not be rewrapped."""
        step_mock = MagicMock(spec=TokenizerStep)
        step_mock.process.side_effect = InvalidPipelineError("Already descriptive")

        pipeline = Pipeline([step_mock])
        controller = PipelineController(pipeline)

        with self.assertRaisesRegex(InvalidPipelineError, "Already descriptive"):
            controller.run(self.doc)

    def test_run_wraps_generic_exception(self):
        """
        Any generic exception should be wrapped with step information.
        Ensures full error-handling coverage.
        """
        step_mock = MagicMock(spec=TokenizerStep)
        step_mock.process.side_effect = ValueError("Random crash")

        pipeline = Pipeline([step_mock])
        controller = PipelineController(pipeline)

        with self.assertRaisesRegex(InvalidPipelineError, "Error in TokenizerStep: Random crash"):
            controller.run(self.doc)


if __name__ == "__main__":
    unittest.main()
