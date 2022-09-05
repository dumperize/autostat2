from spacy.tokens import Span

from src.api.data_loader.DataLoader import data_loader
from src.NER.utils.add_del_span import add_span_in_doc
from src.NER.utils.jaro import get_most_likely_word
from src.NER.utils.operation import filter_ent, find_start_string
from src.NER.utils.retokenizer import split_token_by_n


def set_similar_brand(doc):
    max_rate = 0.0
    most_likely_brand = ''
    best_index_token = 0
    dictionary = data_loader.dictionary
    for index, token in enumerate(doc):
            if len(token) > 2:
                rate, word = get_most_likely_word(str(token), dictionary)
                if max_rate < rate:
                    max_rate = rate
                    most_likely_brand = word
                    best_index_token = index
    if max_rate > 0.0:
            span = Span(doc, best_index_token, best_index_token + 1, label="BRAND", kb_id=most_likely_brand)
            add_span_in_doc(doc,span)


def set_in_next_token(ent, doc):
    brand = ent.kb_id_ or ent.ent_id_
    dictionary_brand = data_loader.dictionary[brand]['models']

    dictionary_models = {}
    for key in dictionary_brand.keys():
        dictionary_models[key.lower()] = key
        for x in dictionary_brand[key]['names']: 
            dictionary_models[x['name'].lower()] = key


    if ent:
        start = ent.end
        end = start + 3 if start + 3 < len(doc) else len(doc)

        pred_model = "".join([doc[x].text for x in range(start, end)]).replace(' ', '')
        model = find_start_string(pred_model, dictionary_models.keys())

        if model: 
            span_name = f'{brand.upper()}_{dictionary_models[model].upper()}'
    
            if len(model) < len(doc[start].text):
                split_token_by_n(doc, start, len(model))

                span_model = doc[start:end].char_span(0, len(doc[start].text), label="MODEL", kb_id=span_name)
                add_span_in_doc(doc, span_model)
                exist_ent =doc[start].ent_type_
                if exist_ent =='YEAR':
                    span_year = doc[start:end].char_span(len(doc[start].text), len(doc[start].text) + len(doc[start + 1].text), label="YEAR")
                    add_span_in_doc(doc, span_year)
            else:
                span = Span(doc, start, start + 1, label="MODEL", kb_id=span_name)
                add_span_in_doc(doc, span)
            return True
    return False


def set_most_likely_model(ent, doc):
    max_rate = 0.0
    most_likely_brand = ''
    best_index_token = 0

    brand = ent.kb_id_ or ent.ent_id_
    dictionary = data_loader.dictionary
    dictionary_brand = dictionary[brand]['models']

    for index, token in enumerate(doc):
        if len(token) > 2 and token.ent_type_ == '':
            rate, word = get_most_likely_word(str(token), dictionary_brand)
            if max_rate < rate:
                max_rate = rate
                most_likely_brand = word
                best_index_token = index
    if max_rate > 0.0:
        new_ent = Span(doc, best_index_token, best_index_token + 1, label="MODEL", kb_id=most_likely_brand)
        doc.set_ents(list(doc.ents) + [new_ent])



def loop_by_brand(doc, fn):
    brands_ents = filter_ent(doc, 'BRAND')

    for iter in range(len(brands_ents)):
        ents = filter_ent(doc, 'BRAND') # кишки меняются поэтому вот так
        ent = ents[iter] if len(ents) > iter else None

        if ent: fn(ent, doc)

def set_similar_model(doc):
    loop_by_brand(doc, set_in_next_token)

    if len(filter_ent(doc, 'MODEL')):
        return

    loop_by_brand(doc, set_most_likely_model)
