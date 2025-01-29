include .env
export

.PHONY: start-api start-fastapi install

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
	PYTHONPATH=. python -c "from rest.fastapi_server import RESTServer; RESTServer().start(None, $${DTC_REST_PORT})"

install:
	pip install -r requirements.txt