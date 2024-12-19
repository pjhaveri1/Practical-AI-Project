import gdown
import os

# Create the data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# URL for the Parquet file on Google Drive
url = "https://drive.google.com/uc?id=1AyHgKVPIKZCEbtFSW6ekvOdR6u0wVpce"  # Replace FILE_ID with the actual file ID from Google Drive
output = "data/recipes.parquet"

# Download the file
print("Downloading recipes.parquet...")
gdown.download(url, output, quiet=False)
print("Download complete!")
