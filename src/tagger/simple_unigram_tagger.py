class UnigramTagger:
    def __init__(self, model):
        self.model = model

    def tag_text(self, text):
        # Assuming the model is a dictionary-like object
        return [(word, self.model.get(word, 'NN')) for word in text]

