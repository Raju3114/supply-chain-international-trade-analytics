import os
import hashlib
import requests

FILES_TO_DOWNLOAD = [
    {
        "filename": "DataCoSupplyChainDataset.csv",
        "url": "https://data.mendeley.com/public-files/datasets/8gx2fvg2k6/files/72784be5-36d3-44fe-b75d-0edbf1999f65/file_downloaded",
        "expected_sha256": "fa6d022ed437155e1a2f0378710602848703c8a7f203f7ff5d77805bf8480aa6",
        "expected_size": 95910149,
    },
    {
        "filename": "DescriptionDataCoSupplyChain.csv",
        "url": "https://data.mendeley.com/public-files/datasets/8gx2fvg2k6/files/29dc7b05-dda6-4834-8354-5b5cc44430df/file_downloaded",
        "expected_sha256": "9828e34669bd6d77e3b4463364cc44a5d52446b5e246fc258758cfe592566c4b",
        "expected_size": 3444,
    },
]

def download_and_verify(dest_dir: str = os.path.join("data", "raw")):
    os.makedirs(dest_dir, exist_ok=True)
    for item in FILES_TO_DOWNLOAD:
        dest_path = os.path.join(dest_dir, item["filename"])
        if os.path.exists(dest_path):
            with open(dest_path, "rb") as f:
                existing_sha = hashlib.sha256(f.read()).hexdigest()
            if existing_sha == item["expected_sha256"]:
                print(f"[OK] {item['filename']} already downloaded and verified.")
                continue

        print(f"Downloading {item['filename']} ({item['expected_size'] / (1024*1024):.2f} MB)...")
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        with requests.get(item["url"], stream=True, headers=headers, timeout=60) as response:
            response.raise_for_status()
            hasher = hashlib.sha256()
            downloaded_bytes = 0
            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
                        hasher.update(chunk)
                        downloaded_bytes += len(chunk)

        calculated_sha = hasher.hexdigest()
        print(f"Downloaded {downloaded_bytes} bytes. SHA256: {calculated_sha}")
        if calculated_sha != item["expected_sha256"]:
            raise ValueError(f"Checksum mismatch for {item['filename']}: expected {item['expected_sha256']}, got {calculated_sha}")
        print(f"[VERIFIED] {item['filename']} verified successfully against Mendeley cryptographic hash.")

if __name__ == "__main__":
    download_and_verify()
