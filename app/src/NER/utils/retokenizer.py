def split_token_by_n(doc, num_token, *pos_str):
    pos_str_with_border = sorted(list(set([0] + list(pos_str) + [len(doc[num_token].text)])))
    pair = pos_str_with_border[:-1], pos_str_with_border[1:]
    words = [doc[num_token].text[prev:curr]  for prev, curr in list(zip(*pair))]
    heads = [(doc[num_token], 1) for _ in range(len(pos_str_with_border) - 1)]

    with doc.retokenize() as retokenizer:
        retokenizer.split(
            doc[num_token], 
            words, 
            heads=heads, 
            attrs={}
        )