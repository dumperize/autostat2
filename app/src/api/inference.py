from http.client import HTTPException
import os
import pandas as pd
from fastapi import FastAPI, UploadFile, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from os.path import dirname, abspath
from src.NER.model import create_ner_model
from src.api.data_loader.DataLoader import data_loader


dirname = dirname(dirname(abspath(__file__)))

app = FastAPI()

def simplify_multiple(objects):
    for obj in objects:
        if pd.notna(obj["brand"]) and obj["brand"].find(",") > -1:
            arr = [obj | {"brand": x} for x in obj["brand"].split(",")]
            return simplify_multiple(arr)

        if pd.notna(obj["model"]) and obj["model"].find(",") > -1:
            arr = [obj | {"model": x} for x in obj["model"].split(",")]
            return simplify_multiple(arr)

        if pd.notna(obj["year"]) and obj["year"].find(",") > -1:
            arr = [obj | {"year": x} for x in obj["year"].split(",")]
            return simplify_multiple(arr)
    return objects


class Model:
    def __init__(self) -> None:
        self.model = create_ner_model()



    def predict(self, data):
        dictionary = data_loader.dictionary

        def set_sql_id(x):
            try: 
                model_name = x['model'].split('_')[1]
                sql_id = dictionary[ x['brand'] ]['models'][ model_name ]['sql_id']
                x["sql_id"] = sql_id
            except:
                x["sql_id"] = None
            return x

        result = []
        for index, row in data.iterrows():
            doc = self.model(str(row['text']))
            result_row = simplify_multiple([{
                "id": row['id'],
                "brand": None if pd.isna(doc.user_data['brands']) else doc.user_data['brands'],
                "model": None if pd.isna(doc.user_data['models']) else doc.user_data['models'],
                "year": None if pd.isna(doc.user_data['years']) else doc.user_data['years'],
            }])
            result_row = map(set_sql_id, result_row)

            result.extend(result_row)
        return  result

@app.get("/generate_dictionary")
async def generate_dictionary():
    data_loader.needUpdate = True

    return JSONResponse(content={"succes": True})


@app.post("/invacation_file")
async def create_upload_file(file: UploadFile):
    if file.filename.endswith(".csv"):
        with open(file.filename, "wb") as f:
            f.write(file.file.read())
        data = pd.read_csv(file.filename)
        os.remove(file.filename)

        model = Model()
        json_compatible_item_data = jsonable_encoder(model.predict(data))
        return JSONResponse(content=json_compatible_item_data)
    else:
        raise HTTPException(status_code=400, detail="invalid file format")



@app.post("/invacation")
async def update_item(request: Request):
    try: 
        data_json = await request.json()
        model = Model()
        data = pd.json_normalize(data_json)

        json_compatible_item_data = jsonable_encoder(model.predict(data))
        return JSONResponse(content=json_compatible_item_data)
    except:
        raise HTTPException(status_code=400, detail="Error") 

    