import argparse
import os
import sys
sys.path.append(os.getcwd())
from modules.loader import load_corpus_to_dataframe
from modules.utils import save_data


def main():
    parser = argparse.ArgumentParser(description="Unified Argument Extraction")
    parser.add_argument("--input", default="arg-microtexts/corpus/en", help="Input folder")
    parser.add_argument("--output", required=True, help="Output file (.csv or .xml)")
    parser.add_argument("--filter_type", nargs='+', choices=['claim', 'premise', 'objection'],
                        help="Optional: Filter by argument type")

    args = parser.parse_args()

    # 1. Load
    df = load_corpus_to_dataframe(args.input)
    if df.empty:
        print("No data extracted.")
        return

    # 2. Filter (Optional)
    if args.filter_type:
        print(f"Filtering for types: {args.filter_type}")
        df = df[df['type'].isin(args.filter_type)]

    # 3. Save
    save_data(df, args.output)


if __name__ == "__main__":
    main()
