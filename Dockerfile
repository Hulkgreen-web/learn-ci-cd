FROM python:3.13-slim

WORKDIR /app

# Créer un utilisateur non-root dédié
RUN useradd --create-home --user-group app

# Récupérer l'exécutable uv depuis l'image officielle Astral
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copier les fichiers de dépendances pour exploiter le cache Docker
COPY pyproject.toml uv.lock README.md ./

# Installer les dépendances de production (sans pytest)
RUN uv sync --frozen --no-dev

# Ajouter l'environnement virtuel au PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copier l'ensemble du code de l'application
COPY . .

# Ajuster les droits sur les fichiers pour l'utilisateur app
RUN chown -R app:app /app

EXPOSE 8000

# Vérifier la santé du conteneur via la route /health
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

# Exécuter en tant qu'utilisateur non-root
USER app

# Lancer FastAPI (fastapi run écoute par défaut sur 0.0.0.0:8000)
CMD ["fastapi", "run", "main.py", "--port", "8000"]
