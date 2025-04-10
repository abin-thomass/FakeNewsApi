FROM python:3.9

WORKDIR /code

COPY ./req.txt /code/req.txt

RUN pip install --no-cache-dir --upgrade -r /code/req.txt


COPY ./api.py /code/


CMD ["uvicorn","api:app","--host","0.0.0.0","--port","8000"]