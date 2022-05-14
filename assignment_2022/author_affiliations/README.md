# Country Affiliator

### `src/authors_by_country.py`

Produces a table with author affiliations by country.

Parses author information from `.xml` files in `data/arxiv` and `data/pubmed`. Groups affiliated authors by country for each country listed in `data/AltCountries.csv`. The table is saved to `results/authors_by_country.csv`.


### `src/co_author_graph.py`

Produces a graph of co-authors. The largest connected sub-graph of Finnish co-authors with at least ten co-authored papers is saved to `results/fin_co_author_graph.json`.

### `src/country_network.py`

Produces a network of countries where edge weights represent the number of co-authored papers between two countries. The largest connected sub-graph of countries with at least 1000 co-authored papers is saved to `results/country_network.json`.

## Usage

## Data

Place data in `data/` in the following format:

```
data
├── arxiv
│   ├── author1.xml
│   └── ...
├── pubmed
│   ├── author1.xml
│   └── ...
└── AltCountries.csv
```

### Automated workflow

```shell
conda create -c bioconda -c conda-forge -n snakemake-minimal snakemake-minimal -y
conda activate snakemake-minimal
snakemake -c --use-conda
```

### Manual workflow

Install environment:

```shell
conda env create --name author-affiliations --file env.yml
conda activate author-affiliations
```

Or you can just install the dependencies to your own environment:

```shell
pip install networkx==2.7.1
```

Then, run:

```shell
python src/authors_by_country.py

python src/co_author_graph.py

python src/country_network.py
```