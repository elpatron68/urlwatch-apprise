[![Unit Tests](https://github.com/thp/urlwatch/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/thp/urlwatch/actions/workflows/unit-tests.yml)
[![Packaging status](https://repology.org/badge/tiny-repos/urlwatch.svg)](https://repology.org/metapackage/urlwatch/versions)
[![PyPI version](https://badge.fury.io/py/urlwatch.svg)](https://badge.fury.io/py/urlwatch)
[![Documentation](https://readthedocs.org/projects/urlwatch/badge/?version=latest&style=flat)](https://urlwatch.readthedocs.io/en/latest/)


```
                         _               _       _       ____
              _   _ _ __| |_      ____ _| |_ ___| |__   |___ \
             | | | | '__| \ \ /\ / / _` | __/ __| '_ \    __) |
             | |_| | |  | |\ V  V / (_| | || (__| | | |  / __/
              \__,_|_|  |_| \_/\_/ \__,_|\__\___|_| |_| |_____|

                                  ... monitors webpages for you
```

urlwatch is intended to help you watch changes in webpages and get notified
(via e-mail, in your terminal or through various third party services) of any
changes. The change notification will include the URL that has changed and
a unified diff of what has changed.

* Documentation: https://urlwatch.readthedocs.io/
* Website: https://thp.io/2008/urlwatch/
* E-Mail: m@thp.io

## Apprise notifications

urlwatch now supports sending notifications via Apprise, allowing you to fan out messages to many services
(Discord, Telegram, Slack, Matrix, email gateways, and more) using one unified configuration.

- Install Apprise (optional dependency):

  ```bash
  pip install apprise
  ```

- Enable the reporter in your config (run `urlwatch --edit-config`):

  ```yaml
  report:
    apprise:
      enabled: true
      urls:
        - "discord://WEBHOOK_ID/WEBHOOK_TOKEN"
        - "tgram://BOT_TOKEN/CHAT_ID"
      # Or load targets from Apprise config sources (file/http):
      # config_urls:
      #   - "file:///path/to/apprise.yml"
      format: markdown   # 'text' | 'markdown' | 'html'
      subject: "{count} changes: {jobs}"
  ```

- Test your setup:

  ```bash
  urlwatch --test-reporter apprise
  ```

The Apprise reporter respects your text/markdown/html formatters and the common `separate` option from the
reporter hierarchy.

## Optional dependencies

Some reporters and filters require extra Python packages or system tools. Common extras include:

- apprise: `pip install apprise` (Apprise notifications)
- jq: `pip install jq` (JSON query filter; requires the jq Python package, not the system binary)
- pytesseract + tesseract: `pip install pytesseract pillow` and install the Tesseract binary
- pdftotext (Poppler): `pip install pdftotext` and install Poppler (e.g., `apt install poppler-utils`)

See the documentation for a full list and platform-specific installation notes.

## Running tests locally

Create and activate a virtual environment, install dependencies, then run the test suite:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt pytest pycodestyle

# Optional (to cover filters/reporters that need extras)
pip install apprise jq pytesseract pillow pdftotext

pytest -q
```

Note: some tests exercise filters that depend on system tools/libraries (e.g., `grep`/`awk` for `shellpipe`,
Poppler/pdftotext, Tesseract, jq). On Windows, these tools are easier to satisfy in WSL. On Linux:

```bash
sudo apt update && sudo apt install -y jq poppler-utils tesseract-ocr
```

Then install the matching Python packages in your virtual environment as shown above.
