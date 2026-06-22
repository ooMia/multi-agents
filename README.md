# instructions

```sh
source .venv/bin/activate
uv sync

ollama create calc -f ./Modelfile
ollama list
ollama serve
ollama ps

uv format --preview-features format
uv run main.py

pytest --lf
pytest -m "not fuzz" --lf
pytest -m xfail
pytest -m fuzz

ollama create calc -f ./Modelfile && pytest -m fuzz --lf
ollama create calc -f ./Modelfile && pytest -m "not slow"
```

```sh
git init
touch .gitignore
uv venv -p 3.13

ollama pull llama3.2
ollama list

uv add pytest --dev
uv add ollama
```

```sh
git remote add origin https://github.com/ooMia/multi-agents.git
git fetch origin
git checkout -b develop

git switch develop && git pull
git merge feat/calculator && git push

git branch -d feat/calculator
git push origin --delete feat/calculator

git switch main
git merge --squash develop -i
git branch -D develop
```
