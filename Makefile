include .env
export

.PHONY: start-api start-fastapi install test

#receiving snapshots of market data
start-market-data:
	LOG_DATA=1 LOG_LEVEL=DEBUG python ./marketdepth_client.py -n $${DTC_HOST} -p $${DTC_PORT} -q $${DTC_HISTORY_PORT} -l

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

# Install dependencies
install:
	pip install -r requirements.txt

# Run tests (installs dependencies first)
test: install
	PYTHONPATH=. pytest tests/test_flaskapi_server.py -v