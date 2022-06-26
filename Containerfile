FROM registry.fedoraproject.org/fedora-minimal:36

RUN \
    microdnf install -y \
        python3-pip && \
        microdnf clean all

COPY pinnwand /usr/app/pinnwand
COPY requirements.txt /usr/app/requirements.txt

WORKDIR /usr/app

RUN python3 -m venv venv

RUN venv/bin/pip install -U pip
RUN venv/bin/pip install -r requirements.txt

EXPOSE 8000

CMD ["venv/bin/python3", "-m", "pinnwand", "http"]
