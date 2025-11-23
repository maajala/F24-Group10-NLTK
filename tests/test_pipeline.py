from pipeline.pipeline import Pipeline, PipelineController
from pipeline.steps import TokenizerStep, TaggerStep
from pipeline.document import TextDocument
from pipeline.errors import InvalidPipelineError
from nltk.tokenize import TreebankWordTokenizer

class DummyTagger:
    def tag(self, tokens):
        return [(token, "DUMMY") for token in tokens]

def test_pipeline_runs_successfully():
    doc = TextDocument("Testing the NLP pipeline.")
    pipeline = Pipeline()
    pipeline.add_step(TokenizerStep(TreebankWordTokenizer()))
    pipeline.add_step(TaggerStep(DummyTagger()))

    controller = PipelineController(pipeline)
    result = controller.run(doc)

    assert result.tokens == ['Testing', 'the', 'NLP', 'pipeline', '.']
    assert all(tag == "DUMMY" for _, tag in result.tags)

def test_missing_tokenizer_raises_error():
    doc = TextDocument("Missing tokenizer should fail.")
    pipeline = Pipeline()
    pipeline.add_step(TaggerStep(DummyTagger()))
    controller = PipelineController(pipeline)

    try:
        controller.run(doc)
        assert False, "Expected InvalidPipelineError"
    except InvalidPipelineError as e:
        assert "TaggerStep cannot run" in str(e)
