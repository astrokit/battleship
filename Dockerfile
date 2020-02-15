FROM python:3.12-alpine

COPY main.py /main.py
CMD ["python", "/main.py"]
