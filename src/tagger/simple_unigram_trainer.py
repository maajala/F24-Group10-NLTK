class UnigramTrainer:
    def __init__(self, corpus):
        self.corpus = corpus
        self.model = {}

    def train(self):
        for sentence in self.corpus:
            for word, tag in sentence:
                self.model[word] = tag

    def get_model(self):
        return self.model

