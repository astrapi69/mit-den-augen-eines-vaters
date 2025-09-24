import unittest
import pandas as pd
import json
import os
from typing import List

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
NFT_DIR = os.path.join(PROJECT_ROOT, 'nft')
CSV_FILE = os.path.join(NFT_DIR, 'nft_image_links_template_jpeg.csv')
JSON_FILES = [
    os.path.join(NFT_DIR, f'prompt_card_{i}.json') for i in range(1, 6)
]


def load_json_metadata(json_file_paths: List[str]) -> pd.DataFrame:
    json_data = []
    for json_path in json_file_paths:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            image_cid = data.get("image", "").replace("ipfs://", "")
            json_data.append({
                "name": data.get("name"),
                "description": data.get("description"),
                "ipfs_cid": image_cid,
                "category": next((attr["value"] for attr in data["attributes"] if attr["trait_type"] == "Category"),
                                 None),
                "level": next((attr["value"] for attr in data["attributes"] if attr["trait_type"] == "Level"), None)
            })
    return pd.DataFrame(json_data)


class TestMetadataConsistency(unittest.TestCase):

    def test_csv_and_json_consistency(self):
        # Load data
        csv_data = pd.read_csv(CSV_FILE).reset_index(drop=True)
        json_data = load_json_metadata(JSON_FILES).reset_index(drop=True)

        # Sanity check: count
        self.assertEqual(len(csv_data), len(json_data), "Row counts do not match")

        # Compare field by field
        for idx, (csv_row, json_row) in enumerate(zip(csv_data.iterrows(), json_data.iterrows())):
            csv_values = csv_row[1]
            json_values = json_row[1]
            with self.subTest(card_number=csv_values["card_number"]):
                self.assertEqual(csv_values["ipfs_cid"], json_values["ipfs_cid"],
                                 f"CID mismatch at card #{csv_values['card_number']}")
                self.assertTrue(json_values["name"].startswith(f"Prompt Card #{csv_values['card_number']}"),
                                f"Name mismatch for card #{csv_values['card_number']}")
                # Optional: add more field checks here


if __name__ == "__main__":
    unittest.main()
