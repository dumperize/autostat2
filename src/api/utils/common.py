import re


def flatten(l):
    return [item for sublist in l for item in sublist]


def str_clean(s):
    s = re.sub(r"-", " ", s)
    s = re.sub(r" ", "", s)
    return s