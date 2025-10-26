from nltk.tokenize import RegexpTokenizer
from tagger.simple_unigram_tagger import UnigramTagger

def main():
    text = "The quick brown fox jumps over 12 lazy dogs."

    # Step 1: Tokenize
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(text)
    print("Tokens:", tokens)

    # Step 2: Create a dummy model for the tagger
    dummy_model = {
        'The': 'DT',
        'quick': 'JJ',
        'brown': 'JJ',
        'fox': 'NN',
        'jumps': 'VBZ',
        'over': 'IN',
        'lazy': 'JJ',
        'dogs': 'NNS',
        '12': 'CD'
    }

    # Step 3: Initialize tagger with the dummy model
    tagger = UnigramTagger(dummy_model)

    # Step 4: Pass tokens directly (not a string)
    tagged = tagger.tag_text(tokens)
    print("Tagged:", tagged)

if __name__ == "__main__":
    main()

