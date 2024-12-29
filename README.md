# obsidian-taskwarrior-bridge
A tool to synchronize your TaskWarrior task list into a file in an Obsidian vault.

## Getting started

```
# Assuming you store venvs in a single directory.
venv_storage=~/.local/venvs
venv_name=obsidian-taskwarrior-bridge
venv_location="${venv_storage}/${venv_name}"

test -d "$venv_storage" || mkdir "$venv_storage"
python3 -m venv "$venv_location"
source "${venv_location}/bin/activate"
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```
