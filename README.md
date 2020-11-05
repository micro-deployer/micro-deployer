# micro-deployer
A deployment tool for microcontrollers



# development

`
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
`

For updating requirements please use pip-tools:

`
pip install pip-tools
pip-compile requirements.in
`

Running tests:

`python -m pytest`

