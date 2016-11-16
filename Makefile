all:
	( \
		virtualenv --python=python3 venv; \
		source venv/bin/activate; \
		pip install -r requirements.txt; \
		cp Info.plist venv/bin/; \
	)
