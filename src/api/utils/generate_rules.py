import json
import re
import jsonlines


def in_rules(name):
    digit_re = re.compile('\d')
    return digit_re.search(name) or len(name) < 3

def generate_rule(label, name, id):
    rules = [] 
    if in_rules(name): return rules
    
    rules.append({"label": label, "pattern": [{"LOWER": name.lower()}], "id": id})
    if len(name.split(' ')) > 1:
        rules.append({"label": label, "pattern": [{"LOWER": w.lower()} for w in name.split(' ')], "id": id })
    
    return rules

def prepare_rules(input_path: str, output_file: str): 
    with open(input_path) as json_file:
        dictionary = json.load(json_file)
        rules = []

        for id in dictionary.keys():
            brand = dictionary[id]
            for i in brand['names']:
                name = i['name']
                rules.extend(generate_rule("BRAND", name, id))
                    
                    
            for id_model in brand['models'].keys():
                model = brand['models'][id_model]
                for i in model['names']:
                    name = i['name']
                    rules.extend(generate_rule("MODEL", name, f"{id}_{id_model}"))

        with jsonlines.open(output_file, 'w') as writer:
            writer.write_all(rules)


if __name__ == "__main__":
    prepare_rules()