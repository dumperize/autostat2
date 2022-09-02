from spacy.language import Language
import re
import numpy as np
from src.models.NER.ent_year import set_ent_year, currentYearReg
from src.models.NER.ent_brand_leven import set_similar_model, set_similar_brand
from src.models.NER.utils.add_del_span import del_span_in_doc
from src.models.NER.utils.operation import filter_ent



def get_ents_id(ents): return map(lambda ent: ent.kb_id_ or ent.ent_id_, ents)


def del_not_fit_model_for_brand(doc):
    ent_brands = filter_ent(doc, 'BRAND')
    ent_models = filter_ent(doc, 'MODEL')
    brands = set(get_ents_id(ent_brands))

    if len(brands) == 1 and len(ent_models) > 0:        # есть 1 бренд и модели
        brand = list(ent_brands)[0]
        brand_name = brand.text.lower() + '_'
        not_fit_ent_model = set(filter(
                lambda x: not (x.kb_id_.lower().startswith(brand_name) or x.ent_id_.lower().startswith(brand_name)), 
                ent_models
            ))
        
        for x in not_fit_ent_model:
            del_span_in_doc(doc, x)


@Language.component("expand_model")
def expand_model(doc):
        for ent in doc.ents:
            if ent.label_ == 'YEAR': set_ent_year(doc, ent)

        if len(filter_ent(doc, 'BRAND')) == 0: 
            set_similar_brand(doc)
        

        del_not_fit_model_for_brand(doc)
        
        if len(filter_ent(doc, 'BRAND')) > 0 and len(filter_ent(doc, 'MODEL')) == 0:
            set_similar_model(doc)


        ent_brands = filter_ent(doc, 'BRAND')
        ent_models = filter_ent(doc, 'MODEL')
        ent_years = filter_ent(doc, 'YEAR')

        name_years_set = list(set([re.search(r'{}'.format(currentYearReg), x.text).group() for x in ent_years]))

        doc.user_data['brands'] = ', '.join(set(get_ents_id(ent_brands))) if len(ent_brands) else np.nan
        doc.user_data['models'] = ', '.join(set(get_ents_id(ent_models))) if len(ent_models) else np.nan
        doc.user_data['years'] = ', '.join(name_years_set) if len(name_years_set) else np.nan
        
        return doc