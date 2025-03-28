FROM registry.fedoraproject.org/fedora-minimal:41 AS base

RUN \
    dnf install -y \
        python3-pip && \
        dnf clean all

WORKDIR /usr/app

RUN python3 -m venv venv
RUN venv/bin/pip install -U pip

COPY requirements.txt /usr/app/requirements.txt
RUN venv/bin/pip install -r requirements.txt

# Copy the source code in last to optimise rebuilding the image
COPY src/pinnwand /usr/app/pinnwand

EXPOSE 8000
CMD ["venv/bin/python3", "-m", "pinnwand", "http"]

# =========================================================================

FROM base AS psql
WORKDIR /usr/app
COPY --from=base /usr/app ./
RUN venv/bin/pip install psycopg2-binary

EXPOSE 8000
CMD ["venv/bin/python3", "-m", "pinnwand", "http"]

# =========================================================================

FROM base AS mysql
WORKDIR /usr/app
RUN \
    dnf install -y \
        community-mysql-devel python3-devel gcc && \
    dnf clean all

COPY --from=base /usr/app ./
RUN venv/bin/pip install mysqlclient

EXPOSE 8000
CMD ["venv/bin/python3", "-m", "pinnwand", "http"]
