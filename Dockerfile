FROM python:3-slim AS builder

RUN pip install pipenv

WORKDIR /deps
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv requirements >requirements.txt

COPY main.py /app
COPY gh.py /app
WORKDIR /app

RUN p

# We are installing a dependency here directly into our app source dir
RUN pip install --target=/app -r /deps/requirements.txt

# A distroless container image with Python and some basics like SSL certificates
# https://github.com/GoogleContainerTools/distroless
FROM gcr.io/distroless/python3-debian10
COPY --from=builder /app /app
WORKDIR /app
ENV PYTHONPATH /app
CMD ["/app/main.py"]
