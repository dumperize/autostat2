import re
from src.models.NER.utils.add_del_span import add_span_in_doc, del_span_in_doc
from src.models.NER.utils.operation import filter_ent
from src.models.NER.utils.regex import match_sequence

from src.models.NER.utils.retokenizer import split_token_by_n


# TODO 2023 год уже не попадет - надо написать через переменную
currentYearReg = '[1][9][6-9][0-9]|(20)[0-1][0-9]|(20)[2][0-2]'

def get_points(ent, pos_next):
    points_find_iter = [match.start() for match in re.finditer(currentYearReg, ent.text)]
    points_intersect = [match.start() for match in match_sequence(currentYearReg, ent.text)]
    if (len(points_find_iter) < len(points_intersect)) and pos_next:
        return [points_intersect[-1]]
    return points_find_iter

def get_neighbor(doc, ent, next: bool):
            incr = 1 if next else -1
            is_fit_token = True
            while is_fit_token:
                token =  None if ent.start + incr < 0 or ent.start + incr >= len(doc) else doc[ent.start + incr]
                if token is None:
                    is_fit_token = False
                if re.compile("^[-.?!)(,:]$").match(str(token)):
                    incr = incr + 1 if incr > 0 else incr - 1
                else:
                    is_fit_token = False
            return token

def set_ent_year(doc, ent):
                # print(ent)
                prev_token = get_neighbor(doc, ent, False) 
                next_token = get_neighbor(doc, ent, True)

                match_string = r'г\.|года|год|выпуска|изготовления|в\.'
                not_match_string = r'№|куб.см|^см|^с.|^кг\.|^НМ$|^от$|рама|двигатель|двигателя|января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|декабря|номер'

                prev_result = re.match(match_string, str(prev_token)) # есть в пред
                prev_neg_result = re.match(not_match_string, str(prev_token)) # есть плохое в пред
                pos_prev = not prev_neg_result and prev_result

                next_result = re.match(match_string, str(next_token)) # есть в след
                next_neg_result = re.match(not_match_string, str(next_token)) # есть плохое в след
                pos_next = not next_neg_result and next_result

                inner_result = re.match(match_string, str(ent.text)) # есть в внутри
                inner_neg_result = re.match(not_match_string, str(ent.text)) # есть плохое в внутри
                pos_inner = not inner_neg_result and inner_result

                only_digits = re.match(r'^{}$'.format(currentYearReg), str(ent.text)) # состоит только из 4х цифр
                neg_data = re.match(r'\d{2}\.\d{2}\.\d{4}', str(ent.text))  # это не дата

                pos_token = pos_prev or pos_next or pos_inner # в токенах вокруг что-то позитивное
                pos_digits = only_digits and not prev_neg_result and not next_neg_result # это просто 4 цифры и ничего негативного вокруг

                ents = filter_ent(doc, 'YEAR')
                only_one_sim = len(ents) == 1 and not prev_neg_result and not next_neg_result # это единственное что-то похожее на год в строке и ничего негативного вокруг

                # print(neg_data, pos_token, pos_digits)
                if not neg_data and (pos_token or pos_digits or only_one_sim):
                    if len(ent.text) == 4: return True

                    # points_start = [match.start() for match in re.finditer(currentYearReg, ent.text)]
                    points_start = get_points(ent, pos_next)

                    points_end = [x + 4 for x in points_start]
                    points = points_start + points_end
                    split_token_by_n(doc, ent.start, *points)

                    spans = [doc.char_span(ent.start_char + point, ent.start_char + point + 4, label="YEAR") for point in points_start]

                    del_span_in_doc(doc, ent)
                    for span in spans:
                        add_span_in_doc(doc, span)
                else:
                    del_span_in_doc(doc, ent)

