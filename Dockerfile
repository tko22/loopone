FROM python:3.7
COPY . /loopone
WORKDIR /loopone
RUN pip install -r requirements.txt
RUN pip install .
CMD ["loopone", "paper"]
