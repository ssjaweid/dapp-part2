# how to access using CID
# https://ipfs.io/ipfs/⟨YOUR_CID_HERE⟩

import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define headers
PINATA_API_KEY = os.getenv("PINATA_API_KEY")
PINATA_SECRET_API_KEY = os.getenv("PINATA_SECRET_API_KEY")

JSON_HEADERS = {
    "Content-Type": "application/json",
    "pinata_api_key": PINATA_API_KEY,
    "pinata_secret_api_key": PINATA_SECRET_API_KEY,
}

FILE_HEADERS = {
    "pinata_api_key": PINATA_API_KEY,
    "pinata_secret_api_key": PINATA_SECRET_API_KEY,
}

# Convert content to Pinata compatible JSON format
def convert_data_to_json(content):
    return json.dumps({
        "pinataOptions": {"cidVersion": 1},
        "pinataContent": content
    })

# Pin file to IPFS through Pinata
def pin_file_to_ipfs(data):
    response = requests.post(
        "https://api.pinata.cloud/pinning/pinFileToIPFS",
        files={'file': data},
        headers=FILE_HEADERS
    )

    if response.status_code == 200:
        return response.json().get("IpfsHash")
    else:
        print("Error pinning file to IPFS:", response.json())
        return None

# Pin JSON data to IPFS through Pinata
def pin_json_to_ipfs(json_data):
    response = requests.post(
        "https://api.pinata.cloud/pinning/pinJSONToIPFS",
        data=json_data,
        headers=JSON_HEADERS
    )

    if response.status_code == 200:
        return response.json().get("IpfsHash")
    else:
        print("Error pinning JSON to IPFS:", response.json())
        return None
