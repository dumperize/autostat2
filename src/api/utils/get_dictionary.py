import os
import json
import re
import pandas as pd
from src.api.utils.common import str_clean

from src.config import DICTIONARY_PATH


class Data(object):
    def __new__(self):
        if not hasattr(self, "instance"):
            self.instance = super(Data, self).__new__(self)
        return self.instance

    def __init__(self, path_to_file):
        self.path_to_file = path_to_file

        self._dictionary = None
        self._needUpdate = True

    @property
    def dictionary(self):
        if self.needUpdate:
            print('hey')
            self.update_dictionary()
            self.needUpdate = False
        return self._dictionary

    def set_need_update(self):
        self._needUpdate = True


    def update_dictionary(self):
        def get_threshold(name):
            if re.compile("\d").search(name):  # digits
                return 1
            match len(name):
                case (1 | 2): return 1
                case 3: return 0.97
                case 4: return 0.93
                case _: return 0.85

        def generate_name(name, additional_name):
            names_array = ([] if pd.isna(additional_name) else additional_name.split(" | "))
            names_array.append(str_clean(name))
            return [{"name": x, "threshold": get_threshold(x)} for x in names_array]

        df = pd.read_csv(self.path_to_file)
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
            self._dictionary[brand] = brand_object
