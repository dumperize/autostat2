import Levenshtein

from src.models.NER.utils.operation import replace_rus_to_eng_char



def get_jaro(word, similar_word): 
    word = replace_rus_to_eng_char(word).replace(' ', '')
    similar_word = replace_rus_to_eng_char(similar_word).replace(' ', '')
    return Levenshtein.jaro_winkler(word, similar_word)

def get_jaro_with_threshold(word, similar_word, threshold):
    jaro = get_jaro(word, similar_word)
    return -1.0 if jaro < threshold else jaro


def get_most_likely_word(word, dictionary): 
    if len(word) < 3: return None

    rate = 0.0
    most_likely_word = ''
    for key in dictionary.keys():
        item = dictionary[key]
        jaro = max(get_jaro_with_threshold(word, x['name'], x['threshold']) for x in item['names'])

        if jaro > rate:
            rate = jaro
            most_likely_word = item['id']
    return (rate, most_likely_word)