
all: metrics dashboard

dashboard:
	python update-html.py

metrics:
	python update-metrics.py

push:
	git add kepler-dashboard.json
	git commit -m "Regular dashboard update"
	git push

