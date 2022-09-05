FROM python:3.10

WORKDIR /code


RUN pip3 install --upgrade pip

COPY ./app /code
# COPY ./Docker/fast_api/requirements.txt /code/
RUN pip3 install -r requirements.txt

CMD ["uvicorn", "src.api.inference:app", "--host", "0.0.0.0", "--port", "8003"]