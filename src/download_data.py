"""
Step 0: Download the DiverseVul dataset into the data/ folder.

The authors share the dataset on Google Drive (link from
https://github.com/wagner-group/diversevul). We use the `gdown`
library to download from Google Drive.

Run from the project folder:
    python src/download_data.py
"""

import os
import zipfile

import gdown

# Google Drive file id of the DiverseVul dataset (from the authors' GitHub page)
DATASET_ID = "12IWKhmLhq7qn5B_iXgn5YerOQtkH-6RG"

os.makedirs("data", exist_ok=True)

# Download the file. gdown keeps the original file name from Google Drive.
path = gdown.download(id=DATASET_ID, output="data/", quiet=False)
print("Downloaded:", path)

# If the download is a zip file, unzip it into data/
if path.endswith(".zip"):
    with zipfile.ZipFile(path) as z:
        z.extractall("data/")
    print("Unzipped into data/")

print("Files in data/:", os.listdir("data"))
