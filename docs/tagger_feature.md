# Tagger Feature Documentation

## Overview

This feature implements a **simple unigram tagger** using the `RegexpTokenizer`. It includes:
- **Unigram trainer** (`simple_unigram_trainer.py`): A trainer for learning a unigram model.
- **Unigram tagger** (`simple_unigram_tagger.py`): The tagger that assigns tags based on the learned model with backoff logic.
- **Tests** (`test_tagger.py`): Unit tests for verifying the functionality of the tagger.

## Trainer: `simple_unigram_trainer.py`

The trainer trains a unigram model from a corpus. It reads a corpus of text and learns the frequency of each word and its corresponding tag.

### Example usage:
```python
from src.tagger.simple_unigram_trainer import UnigramTrainer

trainer = UnigramTrainer(corpus)
trainer.train()

