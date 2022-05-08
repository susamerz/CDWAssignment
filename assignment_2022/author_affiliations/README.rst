===================
author_affiliations
===================

Produces a table with author affiliations by country.

Parses author information from `.xml` files in `data/arxiv` and `data/pubmed`.
Groups affiliated authors by country for each country listed in `data/AltCountries.csv`.
The table is saved to `results/authors_by_country.csv`.

## Usage

Install environment:

```shell
conda env create --name author-affiliations --file environment.yml
conda activate author-affiliations
```

Run

`make`

or

`python src/authors_by_country.py`

Features
--------

