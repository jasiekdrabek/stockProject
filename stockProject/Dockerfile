FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "stockProject.wsgi:application"]
