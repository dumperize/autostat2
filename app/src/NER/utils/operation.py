def filter_ent(doc, label): 
    return list(filter(lambda ent: ent.label_ == label, doc.ents))


def replace_rus_to_eng_char(sample_string):
    sample_string = sample_string.upper()
    char_to_replace = {'А': 'A',
                       'В': 'B',
                       'С': 'C',
                       'Е': 'E',
                       'Н': 'H',
                       'К': 'K',
                       'О': 'O',
                       'Р': 'P',
                       'Т': 'T',
                       'Х': 'X',
                       }
    return sample_string.translate(str.maketrans(char_to_replace))


def find_start_string(word, strings): 
    strings = sorted(set(strings),  key=len, reverse=True)
    def compare(w, s): 
        w_r = replace_rus_to_eng_char(w)
        s_r = replace_rus_to_eng_char(s)

        return w_r.startswith(s_r)
    return next(filter(lambda string: compare(word, string), strings), None)