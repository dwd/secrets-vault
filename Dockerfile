FROM debian:12-slim as builder
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes python3-pip python3-venv
RUN python3 -m venv /deps
RUN /deps/bin/python3 -m pip install pipenv
WORKDIR /deps
COPY Pipfile .
COPY Pipfile.lock .
RUN /deps/bin/python3 -m pipenv requirements >requirements.txt
RUN python3 -m venv /venv
WORKDIR /venv
RUN /venv/bin/pip install -r /deps/requirements.txt
FROM gcr.io/distroless/python3-debian12
WORKDIR /app
COPY --from=builder /venv /venv
COPY secrets /venv/secrets/
COPY main.py /venv/
COPY gh /venv/gh/
ENTRYPOINT ["/venv/bin/python3"]
CMD ["/venv/main.py"]
