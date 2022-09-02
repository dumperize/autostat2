from os.path import dirname, abspath, join

dirname = dirname(dirname(abspath(__file__)))

DICTIONARY_PATH = join(dirname, "src/data/dict/")
DICTIONARY_FILE_PATH = join(dirname, "data/brand_model_dict.csv")

IMPORTANT_ADD_NAME_FILE_PATH = join(dirname, "data/important_add_name.jsonl")
IMPORTANT_REMOVE_NAME_FILE_PATH = join(dirname, "data/important_remove_name.jsonl")
YEAR_REGULAR_FILE_PATH = join(dirname, "data/year_regular.txt")