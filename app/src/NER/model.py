import spacy
from src.api.data_loader.DataLoader import data_loader

from src.NER.expand_model import expand_model
from src.NER.add_space import CustomTokenizer


def create_ner_model():
    rules = data_loader.get_rules()
    important_names = data_loader.get_important_names()
    nlp = spacy.blank("ru")

    nlp.tokenizer = CustomTokenizer(nlp.vocab, important_names)
    ruler = nlp.add_pipe("entity_ruler", config={"overwrite_ents": True})

    ruler.add_patterns(rules)
    nlp.add_pipe("expand_model")
    return nlp
