include .env
export

.PHONY: start-api install

# run this if you're not using authentication locally and to use sim mode.
start-api:
	python example_client.py \
		-n $${DTC_HOST} \
		-p $${DTC_PORT} \
		-q $${DTC_HISTORY_PORT} \
		-r $${DTC_REST_PORT} \
		-s
#		-u $${DTC_USERNAME} \
#		-x $${DTC_PASSWORD}

install:
	pip install -r requirements.txt