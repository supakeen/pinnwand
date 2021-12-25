FROM python

COPY pinnwand /usr/app/pinnwand
COPY requirements.txt /usr/app/requirements.txt

WORKDIR /usr/app

RUN python3 -m venv venv

RUN venv/bin/pip install -U pip
RUN venv/bin/pip install -r requirements.txt

CMD ["venv/bin/python3", "-m", "pinnwand", "http"]
