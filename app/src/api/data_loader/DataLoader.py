import re
import jsonlines
import pandas as pd

from src.config import DICTIONARY_FILE_PATH, IMPORTANT_ADD_NAME_FILE_PATH, IMPORTANT_REMOVE_NAME_FILE_PATH, YEAR_REGULAR_FILE_PATH


def str_clean(s):
    s = re.sub(r"-", " ", s)
    s = re.sub(r" ", "", s)
    return s
    
class DataLoader(object):
    def __init__(self):
        self.needUpdate = True
        self.path_to_file = DICTIONARY_FILE_PATH

        self._dictionary = {}
        self._year_regular = self.get_year_regular()

    @property
    def dictionary(self):
        if self.needUpdate:
            self.update_dictionary()
            self.needUpdate = False
        return self._dictionary
    

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

            brand_names = set(df_brand[pd.notna(df_brand["brand_names"])]["brand_names"])
   
            brand_object = {
                "id": brand,
                "names": generate_name(brand, " | ".join(brand_names)),
                "models": {
                    row["model"]: {
                        "id": row["model"],
                        "names": generate_name(row["model"], row["model_names"]),
                        "sql_id": row["id"]
                    }
                    for index, row in df_brand.iterrows()
                },
            }
            self._dictionary[brand] = brand_object

    def get_year_regular(self):
        if self.needUpdate:
            with open(YEAR_REGULAR_FILE_PATH) as f:
                self._year_regular = f.readline()
                f.close()
        return self._year_regular

    def get_rules(self): 
        def generate_rule(label, name, id):
            r = [] 
            if re.compile('\d').search(name) or len(name) < 3: return r
                
            r.extend([{"label": label, "pattern": [{"LOWER": name.lower()}], "id": id}])
            if len(name.split(' ')) > 1:
                    r.extend([{"label": label, "pattern": [{"LOWER": w.lower()} for w in name.split(' ')], "id": id }])
            return r

        rules = []
        
        for id in self.dictionary.keys():
            brand = self.dictionary[id]
      
            for i in brand['names']:
                name = i['name']
                rules.extend(generate_rule("BRAND", name, id))
                            
            for id_model in brand['models'].keys():
                model = brand['models'][id_model]
                for i in model['names']:
                    name = i['name']
                    rules.extend(generate_rule("MODEL", name, f"{id}_{id_model}"))

        # год
        rules.extend([{"label": "YEAR", "pattern": [{"TEXT": {"REGEX": self.get_year_regular()}}]}])
        return rules

    def get_important_names(self): 
        def condition(name):
            return not re.compile('\d').search(name) and len(name) > 3 and not re.compile('[\(\)]').search(name)

        important_names = list(jsonlines.open(IMPORTANT_ADD_NAME_FILE_PATH))
        important_names_remove = list(jsonlines.open(IMPORTANT_REMOVE_NAME_FILE_PATH))

        for brand in self.dictionary.values():
            names = [item['name'] for item in brand['names'] if condition(item['name'])]
            important_names.extend(names)

            for model in brand['models'].values():
                names = [item['name'] for item in model['names'] if condition(item['name'])]
                important_names.extend(names)

        important_names = sorted(list(set(important_names)), key=len, reverse=True)
        important_names = list(map(lambda x: x.lower(), important_names))   
        important_names = list(filter(lambda x: x not in important_names_remove, important_names))

        return important_names



data_loader = DataLoader() 
