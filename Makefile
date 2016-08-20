
all: metrics dashboard

dashboard:
	python update-html.py

metrics:
	python update-metrics.py