include .env
export

.PHONY: start-api start-fastapi install test

# Default Flask version
start-api:
	python example_client.py \
		-n $${DTC_HOST} \
		-p $${DTC_PORT} \
		-q $${DTC_HISTORY_PORT} \
		-r $${DTC_REST_PORT} \
		-s
#		-u $${DTC_USERNAME} \
#		-x $${DTC_PASSWORD}

# FastAPI version
start-fastapi:
	python rest/run_fastapi.py -p $${DTC_REST_PORT}

# Install dependencies
install:
	pip install -r requirements.txt

# Run tests (installs dependencies first)
test: install
	pytest tests/test_flaskapi_server.py -v