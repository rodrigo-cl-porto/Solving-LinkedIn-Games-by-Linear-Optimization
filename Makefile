.PHONY: clean setup start build deploy
JUPYTER_BOOK = book

clean:
	deactivate
	rm -rf .venv

setup:
	uv venv --python 3.13
	source .venv/Scripts/activate
	uv python pin 3.13
	uv sync

start:
	export NODE_TLS_REJECT_UNAUTHORIZED=0
	cd $(JUPYTER_BOOK)
	jupyter-book start
	cd ..

build:
	export NODE_TLS_REJECT_UNAUTHORIZED=0
	cd $(JUPYTER_BOOK)
	jupyter-book build --html
	cd ..

deploy:
	cd $(JUPYTER_BOOK)
	jupyter-book init --gh-pages
	cd ..