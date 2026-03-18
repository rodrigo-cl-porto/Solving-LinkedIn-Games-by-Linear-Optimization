clean:
	deactivate
	rm -rf .venv

setup:
	uv venv
	source .venv/Scripts/activate
	uv sync

start:
	export NODE_TLS_REJECT_UNAUTHORIZED=0
	cd book
	jupyter-book start

build:
	export NODE_TLS_REJECT_UNAUTHORIZED=0
	cd book
	jupyter-book build --html

deploy:
	cd ..
	jupyter-book init --gh-pages