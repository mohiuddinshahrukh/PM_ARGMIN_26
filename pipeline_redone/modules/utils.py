import os
import pandas as pd
from pathlib import Path


def ensure_dir(file_path):
    """Creates directory if it doesn't exist."""
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)


def load_data(input_path):
    """Universal loader for CSV or XML."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    ext = input_path.lower().split('.')[-1]
    if ext == 'csv':
        return pd.read_csv(input_path)
    elif ext == 'xml':
        return pd.read_xml(input_path)
    else:
        raise ValueError(f"Unsupported input format: {ext}")


def save_data(df, output_path, root_name='data', row_name='item'):
    """Universal saver for CSV or XML."""
    ensure_dir(output_path)
    ext = output_path.lower().split('.')[-1]

    try:
        if ext == 'csv':
            df.to_csv(output_path, index=False, encoding='utf-8')
        elif ext == 'xml':
            df.to_xml(output_path, index=False, root_name=root_name, row_name=row_name, encoding='utf-8')
        else:
            raise ValueError("Output must be .csv or .xml")
        print(f"Success! Saved {len(df)} items to: {output_path}")
    except Exception as e:
        print(f"Error saving data: {e}")
