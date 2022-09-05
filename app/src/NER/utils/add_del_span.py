def del_span_in_doc(doc, span):
    ents = [x for x in doc.ents if x != span]
    doc.set_ents(ents)

def add_span_in_doc(doc, span):
    find_ents = [x for x in doc.ents if span.start == x.start]

    for find_ent in find_ents:
        del_span_in_doc(doc, find_ent)

    ents = list(doc.ents)
    ents.append(span)
    doc.set_ents(ents)
