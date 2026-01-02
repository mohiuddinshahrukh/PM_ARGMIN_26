import pandas as pd
import amrlib
import argparse
import os
import sys
from tqdm import tqdm
import warnings

# Suppress minor warnings from libraries
warnings.filterwarnings("ignore")


def load_data(file_path):
    """Loads CSV or XML into a pandas DataFrame."""
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None

    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == '.csv':
            return pd.read_csv(file_path)
        elif ext == '.xml':
            return pd.read_xml(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


def save_data(df, file_path):
    """Saves DataFrame to CSV or XML based on extension."""
    ext = os.path.splitext(file_path)[1].lower()
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

        if ext == '.csv':
            df.to_csv(file_path, index=False)
        elif ext == '.xml':
            df.to_xml(file_path, index=False, root_name='arguments', row_name='argument')
        print(f"Success! Saved AMR parsed results to: {file_path}")
    except Exception as e:
        print(f"Error saving file: {e}")


def main():
    parser = argparse.ArgumentParser(description="Optimize and Run AMR Parsing on Extracted Claims")

    # Input/Output arguments
    parser.add_argument("--input", required=True, help="Path to the extracted claims file (CSV or XML)")
    parser.add_argument("--output", required=True, help="Path to save the final AMR parsed file")

    # Model configuration
    # Note: Use raw string or forward slashes for Windows paths in default if needed
    parser.add_argument("--model", default="amr_model", help="Path to local AMR model (optional)")

    args = parser.parse_args()

    # 1. Load the Extracted Data
    print(f"Loading data from {args.input}...")
    df = load_data(args.input)
    if df is None: return

    # Validate Columns
    if 'full_sentence' not in df.columns:
        print("Error: Input file missing 'full_sentence' column.")
        print("Please run your '5_microtext_claims_extraction.py' script first.")
        return

    # 2. Optimization: Identify Unique Sentences
    # Many arguments share the same sentence. We only want to parse each sentence ONCE.
    unique_sentences = df['full_sentence'].dropna().unique().tolist()

    print(f"Optimization Stats:")
    print(f" - Total Arguments: {len(df)}")
    print(f" - Unique Sentences: {len(unique_sentences)}")
    print(f" - Redundancy Savings: {len(df) - len(unique_sentences)} parses skipped!")

    # 3. Load AMR Model
    print("\nLoading AMR Model...")
    try:
        if os.path.exists(args.model):
            print(f" - Loading local model from: {args.model}")
            stog = amrlib.load_stog_model(model_dir=args.model)
        else:
            print(f" - Local model not found at '{args.model}'.")
            print(" - Downloading/Loading default model (gsii-v3)...")
            stog = amrlib.load_stog_model()
    except Exception as e:
        print(f"Critical Error loading AMR model: {e}")
        return

    # 4. Parsing Loop
    print("\nParsing sentences...")
    batch_size = 16
    parsed_graphs = []

    # Run parsing with progress bar
    for i in tqdm(range(0, len(unique_sentences), batch_size)):
        batch = unique_sentences[i:i + batch_size]
        graphs = stog.parse_sents(batch)
        parsed_graphs.extend(graphs)

    # 5. Re-Map Results to Original Data
    # We create a lookup dictionary: { "Sentence Text" -> "AMR Graph" }
    sent_to_graph = dict(zip(unique_sentences, parsed_graphs))

    # Map the graphs back to the original DataFrame
    # This automatically fills in the graph for every row, even the duplicates
    df['amr_penman'] = df['full_sentence'].map(sent_to_graph)

    # 6. Save Final Result
    save_data(df, args.output)


if __name__ == "__main__":
    main()
