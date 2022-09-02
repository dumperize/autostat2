from http.client import HTTPException
import os
import pandas as pd
import mlflow
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from os.path import dirname, abspath
from src.models.NER.model import create_ner_model
from src.config import DICTIONARY_FILE_PATH
from src.api.data_loader.DataLoader import DataLoader

from src.api.utils.regenerate_dictionary_files import prepare_dictionary
# from src.models.NER.model import create_ner_model


dirname = dirname(dirname(abspath(__file__)))
load_dotenv()


app = FastAPI()

# os.environ['MLFLOW_S3_ENDPOINT_URL'] = os.getenv('MLFLOW_S3_ENDPOINT_URL')


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


def flatten(xss):
    return [x for xs in xss for x in xs]


class Model:
    def __init__(self) -> None:
        # client = mlflow.tracking.MlflowClient()
        # models = client.get_registered_model(model_name)
        # model = next(x for x in models.latest_versions if x.current_stage == 'Staging')
        # run_id=model.run_id

        # local_dir = os.path.abspath(os.getcwd()) + "/tmp/artifact_downloads"
        # if not os.path.exists(local_dir): os.makedirs(local_dir)

        # important_names_file = client.download_artifacts(run_id, "important_names.jsonl", local_dir)
        # rules_file = client.download_artifacts(run_id, "rules.jsonl", local_dir)
        self.model = create_ner_model()

    def predict(self, data):
        result = []
        for index, row in data.iterrows():
            doc = self.model(str(row['text']))
            result = result + simplify_multiple([{
                "id": index,
                "brand": None if pd.isna(doc.user_data['brands']) else doc.user_data['brands'],
                "model": None if pd.isna(doc.user_data['models']) else doc.user_data['models'],
                "year": None if pd.isna(doc.user_data['years']) else doc.user_data['years'],
            }])
        return  result





@app.post("/invacation")
async def create_upload_file(file: UploadFile):
    if file.filename.endswith(".csv"):
        with open(file.filename, "wb") as f:
            f.write(file.file.read())
        data = pd.read_csv(file.filename, index_col='id')
        os.remove(file.filename)

        model = Model()
        json_compatible_item_data = jsonable_encoder(model.predict(data))
        return JSONResponse(content=json_compatible_item_data)
    else:
        raise HTTPException(status_code=400, detail="invalid file format")


@app.get("/generate_dictionary")
async def generate_dictionary():
    # try:
    data_loader = DataLoader()
    data_loader.needUpdate = True

    # print(data_loader.dictionary)

    return JSONResponse(content={"succes": True})


# except:
#     raise HTTPException(status_code=400, detail="Error")

# if os.getenv('AWS_ACCESS_KEY_ID') is None or os.getenv('AWS_SECRET_ACCESS_KEY') is None:
#     exit(1)
