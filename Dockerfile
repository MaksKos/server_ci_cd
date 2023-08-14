FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install requests

WORKDIR /app

COPY  ./server.py /app

CMD [ "python3", "server.py", "-w 2", "-k 5" ]



