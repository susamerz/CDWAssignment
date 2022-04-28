SHELL=/bin/bash

.PHONY: all print_countries

all: results/authors_by_country.csv print_countries

results/authors_by_country.csv:
	python src/authors_by_country.py

countries = 'states' 'finland' 'france' 'germany' 'india' 'japan' 'china'
print_countries: results/authors_by_country.csv
	cat '$<' | grep $(countries:%=-e %)
	
clean:
	find . -regex './processed_data/.*\.pkl' -delete
	find . -regex './results/.*\.csv' -delete