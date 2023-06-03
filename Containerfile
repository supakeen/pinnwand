FROM registry.fedoraproject.org/fedora-minimal:36

RUN \
    microdnf install -y \
        python3-pip && \
        microdnf clean all

WORKDIR /usr/app

RUN python3 -m venv venv
RUN venv/bin/pip install -U pip

COPY requirements.txt /usr/app/requirements.txt
RUN venv/bin/pip install -r requirements.txt

# Copy the source code in last to optimise rebuilding the image
COPY src/pinnwand /usr/app/pinnwand

EXPOSE 8000

CMD ["venv/bin/python3", "-m", "pinnwand", "http"]
