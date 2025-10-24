import argparse
from nltk.tokenize import RegexpTokenizer

def main():
    # Set up argument parsing for CLI
    parser = argparse.ArgumentParser(description="Custom regex tokenizer")
    parser.add_argument('--pattern', type=str, help='Regex pattern for tokenization', default=r'\w+')
    parser.add_argument('--text', type=str, help='Text to tokenize', required=True)

    args = parser.parse_args()

    # Create the tokenizer with the custom pattern
    tokenizer = RegexpTokenizer(args.pattern)
<<<<<<< HEAD
    tokens = tokenizer.tokenize(args.text)  # Tokenize the input text

    # Print the tokens
    print(f"Tokens: {tokens}")

if __name__ == "__main__":
    main()

=======
    print(tokenizer.tokenize(args.text))  # Tokenize the input text

if __name__ == "__main__":
    main()
>>>>>>> 3630eee060db80ff45abcb97639f7e0dfef8b863
