from tokenizer.tokenizer import Tokenizer

if __name__ == "__main__":
    tokenizer = Tokenizer(
        "https://raw.githubusercontent.com/statsbomb/open-data/refs/heads/master/data/events/15956.json", True)
    tokenizer.get_tokenized_match_events()

