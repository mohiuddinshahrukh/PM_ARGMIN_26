import pandas as pd
from smatch import get_amr_match


def main():
    input_file = "microtext_major_claims_amr.csv"

    print(f"--- INSPECTING {input_file} ---")
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"CRITICAL: Could not read CSV. {e}")
        return

    # Check if column exists
    if 'amr_penman' not in df.columns:
        print("CRITICAL: Column 'amr_penman' missing!")
        print("Columns found:", df.columns)
        return

    # Get first row
    first_row = df.iloc[0]
    amr_text = first_row['amr_penman']

    print("\n[1] Checking First Entry Data Type:")
    print(f"Type: {type(amr_text)}")
    print(f"Length: {len(str(amr_text))}")

    print("\n[2] Raw Content (repr):")
    print(repr(amr_text))

    print("\n[3] Printed Content:")
    print(amr_text)

    print("\n[4] Attempting Smatch on this single entry against itself (Should be 1.0):")
    try:
        # We test comparing the graph to itself.
        p, r, f = get_amr_match(amr_text, amr_text)
        print(f"✅ SUCCESS! Self-Smatch Score: {f}")
    except Exception as e:
        print(f"❌ FAILURE: Smatch crashed.")
        print(f"Error details: {e}")


if __name__ == "__main__":
    main()
