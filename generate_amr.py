import pandas as pd
import amrlib
import os


def main():
    # 1. Load the Data
    input_file = "microtext_claims.csv"
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} total ADUs.")

    # 2. Filter Data
    # Keep only Major Claims (the main conclusions)
    # AND remove rows where the topic is missing (the 'd' teaching examples)
    df_filtered = df[
        (df['is_major_claim'] == False) &
        (df['topic_id'] != 'MISSING_TOPIC')
        ].copy()

    print(f"Filtered down to {len(df_filtered)} Major Claims across {df_filtered['topic_id'].nunique()} topics.")

    # 3. Load AMR Parser (Concept Alignment)
    # This downloads a pre-trained model if not present.
    # Note: The first run will take time to download the model (~1GB).
    print("Loading AMR model (this may take a moment)...")

    # We use 'r' before the string to handle the backslashes correctly
    stog = amrlib.load_stog_model(model_dir=r"E:\UNI\Semester 5\PM - Stede\PM_ARGMIN_26\amr_model")

    # 4. Generate Graphs
    print("Parsing sentences into AMR graphs...")
    # stog.parse_sents takes a list of strings and returns a list of PENMAN graphs
    df_filtered['amr_penman'] = stog.parse_sents(df_filtered['text'].tolist())

    # 5. Save Results
    output_file = "microtext_major_claims_amr_is_major_claim_False.csv"
    df_filtered.to_csv(output_file, index=False)

    print("------------------------------------------------")
    print(f"Success! Saved parsed graphs to '{output_file}'.")
    print("Here is a preview of the first graph:")
    print(f"Text: {df_filtered.iloc[0]['text']}")
    print(f"AMR:  {df_filtered.iloc[0]['amr_penman']}")
    print("------------------------------------------------")


if __name__ == "__main__":
    main()