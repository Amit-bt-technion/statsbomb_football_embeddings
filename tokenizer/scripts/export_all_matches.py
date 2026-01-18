import os
from pathlib import Path
from tqdm import tqdm
from tokenizer.tokenizer import Tokenizer


def main():
    """Entry point for the tokenizer-export CLI command."""
    # Define the root directory containing match files
    # Assumes the open-data repo is cloned to a sibling directory to the project root
    matches_root_dir = Path('../../../open-data/data/events')
    output_dir = Path('../../events_csv')
    os.makedirs(output_dir, exist_ok=True)

    # Collect all JSON file paths
    json_paths = []
    for root, _, files in os.walk(matches_root_dir):
        for file in files:
            if file.endswith('.json'):
                json_paths.append(os.path.join(root, file))

    # Process all match files using the Tokenizer
    for json_path in tqdm(json_paths, desc='Processing match files'):
        try:
            # Initialize and process the match file using the Tokenizer
            tokenizer = Tokenizer(path=json_path)
            tokenizer.get_tokenized_match_events()

            # Export the tokenized data to CSV, keeping the original filename
            filename = Path(json_path).stem + '.csv'
            output_path = output_dir / filename
            tokenizer.export_to_csv(path=str(output_path.parent))

        except Exception as e:
            print(f'Error processing {json_path}: {e}')

    print('All match files processed successfully!')


if __name__ == "__main__":
    main()

