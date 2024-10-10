[Django based forum software using **simple** technology.

Django + Bootstrap5 + HTMX

## development setup
1. Install [uv](https://docs.astral.sh/uv/)
2. Install python 3.12 with `uv python install 3.12`
3. Create .venv with `uv venv`
4. Install deps with `uv sync`
5. Run django migrations with `uv run python manage migrate`
6. Create superuser with `uv run python manage createsuperuser`
7. Run the server with `uv run python manage runserver`
8. Develop feature 🔨

## production setup
Package this app in a docker container and use your preferrer deployment method.



Created by anti-SPA bloatware gang. You lose 200000 aura if you deploy this to GCP or other 
bullshit money incinerator.