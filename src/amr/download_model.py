import os
import urllib.request
import tarfile
import shutil

# URL for the "BART Base" model (smaller and faster than Large, but very accurate)
MODEL_URL = "https://github.com/bjascob/amrlib-models/releases/download/parse_xfm_bart_base-v0_1_0/model_parse_xfm_bart_base-v0_1_0.tar.gz"
TAR_FILE = "model_parse_xfm_bart_base-v0_1_0.tar.gz"
EXTRACT_DIR = "amr_model"


def download_and_setup():
    # 1. Check if already exists
    if os.path.exists(EXTRACT_DIR):
        print(f"✅ Model directory '{EXTRACT_DIR}' already exists. Skipping download.")
        return

    # 2. Download
    print(f"⬇️  Downloading AMR model (approx 500MB)... please wait.")
    try:
        urllib.request.urlretrieve(MODEL_URL, TAR_FILE)
        print("✅ Download complete.")
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return

    # 3. Extract
    print("📦 Extracting files...")
    with tarfile.open(TAR_FILE, "r:gz") as tar:
        tar.extractall()

        # Rename the extracted folder to a simple name 'amr_model'
        # The tar usually extracts to a folder with the same name as the file (minus .tar.gz)
        extracted_name = TAR_FILE.replace(".tar.gz", "")
        if os.path.exists(extracted_name):
            os.rename(extracted_name, EXTRACT_DIR)
            print(f"✅ Extracted to '{EXTRACT_DIR}'")

    # 4. Cleanup
    if os.path.exists(TAR_FILE):
        os.remove(TAR_FILE)
    print("🎉 Setup done! You can now run the generation script.")


if __name__ == "__main__":
    download_and_setup()
