from spacy.tokenizer import Tokenizer
import re


class CustomTokenizer(Tokenizer):
    def __init__(self, vocab, important_names):
        Tokenizer.__init__(self, vocab)
        self.important_names = important_names
    
    def add_spaces(self, string):
        reg = '('+'|'.join(self.important_names)+')'
  
        # TODO в конфиг и через артифакты
        big_words = r'машин[ыаеу]|автомобиль|передвижной|цвет|рама|двигател[ья]|шасси|модель|наименование|марк[аи]|белый|выпуска|адрес|коробка|бензиновый|дизельный|кузов|легковой|черный'
        small_words = r'год|гос|легк|г.в|г.'


        string = string.lower()
        string = ' '.join(re.split(reg, string, flags=re.IGNORECASE))
        string = re.sub(r'({})'.format(big_words), r' \1 ', string, flags=re.IGNORECASE)
        string = re.sub(r'([0-9A-Z])({}|{})'.format(small_words, big_words), r'\1 \2', string, flags=re.IGNORECASE)
        string = re.sub(r'({}|{})([0-9A-Z])'.format(small_words, big_words), r'\1 \2', string, flags=re.IGNORECASE)
        string = re.sub(r'([А-я])(г.в|{})'.format(big_words), r'\1 \2', string, flags=re.IGNORECASE)
        string = re.sub(r'({})([А-я])'.format(big_words), r'\1 \2', string, flags=re.IGNORECASE)
        string = re.sub(r'([0-9])(VIN)', r'\1 \2', string, flags=re.IGNORECASE)
        string = re.sub(r'(№)', r' \1 ', string, flags=re.IGNORECASE)
        string = re.sub(r'(\))([\s\w\d]*)(\))', r'\1 \2', string)
        string = re.sub(r'(\()([\d\s\w]*)(\))', r' \1\2\3 ', string)
        string = re.sub(r'-'," ", string)
        string = re.sub(r'\?'," ", string)
        string = re.sub(r'\!'," ", string)
        string = re.sub(r'\)'," ", string)
        string = re.sub(r'\('," ", string)
        string = re.sub(r'([ ]+)|([ ]){2,}'," ", string)
        string = re.sub(r'([mм][eе]r[scс][eе]d[eе]s) (b[eе]n[zsc])', r'\1\2', string, flags=re.IGNORECASE)
        string = re.sub(r'([mм][eе]р[cс][eе]д[eе][зс]) (б[eе]н[зс])', r'\1\2', string, flags=re.IGNORECASE)
        string = re.sub(r'(максима) (льная)', r'\1\2', string, flags=re.IGNORECASE)
        string = re.sub(r'(дизель) (ный)', r'\1\2', string, flags=re.IGNORECASE)
        string = re.sub(r'(эл) (лада)', r'\1\2', string, flags=re.IGNORECASE)
        string = re.sub(r'(марк) (а)', r'\1\2', string, flags=re.IGNORECASE)
        string = re.sub(r'(okt) (avia)', r'\1\2', string, flags=re.IGNORECASE)
        string = re.sub(r'(автос) (амосвал)', r'\1\2', string, flags=re.IGNORECASE)
        string = re.sub(r'(са) (марс) (к)', r'\1\2\3', string, flags=re.IGNORECASE)
        string = re.sub(r'(наиме) (нова) (ние)', r'\1\2\3', string, flags=re.IGNORECASE)
        string = re.sub(r'(к) (атего) (рия)', r'\1\2\3', string, flags=re.IGNORECASE)

        return string

    def __call__(self, string):
        string = self.add_spaces(string)
        return Tokenizer.__call__(self, string)
    
