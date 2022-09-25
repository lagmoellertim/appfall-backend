FROM python:3.8

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY preloaded_cache /root/.cache
COPY main.py /app
COPY view_models.py /app
COPY service /app/service

CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]