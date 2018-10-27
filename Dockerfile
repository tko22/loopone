FROM python:3.7
COPY . .
RUN pip install -r requirements.txt
RUN pip install .
CMD ["loopone", "paper"]
