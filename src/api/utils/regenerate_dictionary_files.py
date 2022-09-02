import pandas as pd
import json
import re

from src.api.utils.common import str_clean


def get_threshold(name):
    if re.compile("\d").search(name): # digits
        return 1
    match len(name):
        case (1|2): return 1
        case 3: return 0.97
        case 4: return 0.93
        case _: return 0.85


def generate_name(name, additional_name):
    names_array = [] if pd.isna(additional_name) else additional_name.split(" | ")
    names_array.append(str_clean(name))
    return [{"name": x, "threshold": get_threshold(x)} for x in names_array]

def prepare_dictionary(input_path: str, output_path: str):
    df = pd.read_csv(input_path)
    brands = set(df["brand"])

    for brand in brands:
        df_brand = df[df["brand"] == brand]

        brand_object = {
            "id": brand,
            "names": generate_name(brand, " | ".join(df_brand[pd.notna(df_brand["brand_names"])])),
            "models": {
                row["model"]: {
                    "id": row["model"],
                    "names": generate_name(row["model"], row["model_names"]),
                }
                for index, row in df_brand.iterrows()
            },
        }

        with open(output_path + re.sub(r"/", "", brand) + '.json', 'w') as outfile:
            json.dump(brand_object, outfile, ensure_ascii=False,)

if __name__ == "__main__":
    prepare_dictionary()
