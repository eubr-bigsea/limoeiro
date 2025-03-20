# Limoeiro

Serviço de catálogo de dados.
Requer Python >= 3.9.0

# Para executar o código em desenvolvimento:
uvicorn app.main:app --reload

# Comandos úteis para o desenvolvimento:

## Usando o `uv`:

Primeiro, é necessário instalar o pacote `uv`. Você pode instalá-lo usando o comando `pip`:

```
pip install uv
```

Em seguida, crie um `virtualenv` com o `uv`:
```
uv venv
```

Um diretório `.venv` será criado. Para ativar o `virtualenv`:
```
source .venv/bin/activate
```

Para instalar as dependências:
```
uv sync
```

## Criar uma revision automaticamente:
```
.venv/bin/alembic revision --autogenerate -m '
```

## Atualizar para a migração mais recente
```
.venv/bin/alembic upgrade head
```

## Execução de testes unitários
```
pytest tests/unit/ --cov app --cov-report term-missing
```
