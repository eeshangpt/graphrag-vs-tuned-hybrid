set -e
PROMPT_VARIANT=prereg .venv/bin/python harness.py --ds 2wiki --n 1000 --B 1000 --methods hippo
