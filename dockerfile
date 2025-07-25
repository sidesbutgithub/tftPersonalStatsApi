FROM python:3.13.5
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY .env /app/.env
COPY . /app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]