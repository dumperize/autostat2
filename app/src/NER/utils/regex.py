import re


def match_sequence(pattern,text,pos=0):
  regex = re.compile(pattern)
  match = regex.search(text)
  while match:
    yield match
    if match.end() == pos:
      break # infinite loop otherwise
    pos = match.start() + 1
    match = regex.search(text,pos)