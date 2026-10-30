FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
COPY app.py index.html ./
EXPOSE 8000
CMD ["python", "app.py"]