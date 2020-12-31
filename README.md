# micro-deployer
A deployment tool for microcontrollers



# development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

For updating requirements please use pip-tools:

```bash
pip install pip-tools
pip-compile requirements.in
```

Running tests:

```bash
python -m pytest
```

