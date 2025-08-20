# https://hub.docker.com/_/python
FROM python:3.12.0-alpine3.18

# Optional python modules for additional functionality
# https://urlwatch.readthedocs.io/en/latest/dependencies.html#optional-packages
# Include apprise to enable multi-service notifications
ARG OPT_PYPKGS="beautifulsoup4 jsbeautifier cssbeautifier aioxmpp apprise"

# Optional system packages for filters/reporters that need external tools
# - jq: JSON query filter
# - poppler-utils: provides pdftotext for PDF to text filter
# - tesseract-ocr (+ english data): OCR filter
ARG OPT_APK="jq poppler-utils tesseract-ocr tesseract-ocr-data-eng"
ENV HOME="/home/user"

RUN apk add --no-cache $OPT_APK && adduser -D user
USER user
WORKDIR $HOME

COPY --chown=user . $HOME/urlwatch

RUN pip install \
  --no-cache-dir \
  ./urlwatch \
  $OPT_PYPKGS \
  && rm -rf urlwatch

ENV PATH="$HOME/.local/bin:$PATH"
ENTRYPOINT ["/home/user/.local/bin/urlwatch"]
