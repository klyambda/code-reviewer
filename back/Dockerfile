FROM python:3.11.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY requirements.txt /app
RUN python3 -m pip install -r requirements.txt

RUN apt update
RUN apt install -y libpango-1.0-0 libpangoft2-1.0-0 libcairo2 libcairo2-dev

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY . /app

CMD python3 app.py