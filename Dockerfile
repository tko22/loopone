FROM python:3.7-alpine
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "loopone/collector.py"]
