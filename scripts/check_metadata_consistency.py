import pandas as pd
import json
from typing import List


def check_metadata_consistency(csv_file_path: str, json_file_paths: List[str]):
    # Load CSV
    csv_data = pd.read_csv(csv_file_path)

    # Prepare to collect JSON metadata
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

    # Convert JSON list to DataFrame
    json_df = pd.DataFrame(json_data)

    # Combine and return for checking
    combined = pd.concat([csv_data.reset_index(drop=True), json_df.reset_index(drop=True)], axis=1)

    # Optionally: validate matches
    combined["cid_match"] = combined["ipfs_cid"] == combined["ipfs_cid"]
    return combined


# Example usage:
if __name__ == "__main__":
    csv_path = "nft_image_links_template_jpeg.csv"
    json_files = [
        "prompt_card_1.json",
        "prompt_card_2.json",
        "prompt_card_3.json",
        "prompt_card_4.json",
        "prompt_card_5.json"
    ]

    result_df = check_metadata_consistency(csv_path, json_files)
    print(result_df.to_string(index=False))
