# instructions

```sh
source .venv/bin/activate
uv sync
uv format --preview-features format
uv run main.py

pytest
```

```sh
git init
touch .gitignore
uv venv -p 3.13

uv add pytest
```

```sh
git checkout -b develop
```
