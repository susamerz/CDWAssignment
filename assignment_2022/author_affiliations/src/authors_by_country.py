import sys
from pathlib import Path

from country_affiliations import get_countries_of_author, get_n_authors_by_country
from utils import has_substring, list_to_csv, merge_values_from_dicts, save_to, load_from, get_short_path
from parsers import ArxivParser, PubmedParser, parse_countries_from_csv

def main():
    cwd = Path(__file__).parents[1]
    author_affiliations_path =  cwd/'processed_data'/'author_affiliations.pkl'
    country_affiliations_path =  cwd/'processed_data'/'country_affiliations.pkl'
    results_path = cwd/'results'/'authors_by_country.csv'

    try:
        author_affiliations = load_from(author_affiliations_path)
        print(f'loaded {get_short_path(author_affiliations_path)}')
    except:
        print(f'no {get_short_path(author_affiliations_path)} found. Writing {get_short_path(author_affiliations_path)}.')
        arxiv_author_affiliations = ArxivParser().get_author_affiliations()
        pubmed_author_affiliations = PubmedParser().get_author_affiliations()
        author_affiliations = merge_values_from_dicts(arxiv_author_affiliations, pubmed_author_affiliations)
        save_to(author_affiliations, author_affiliations_path)
    
    countries = parse_countries_from_csv()

    try:
        country_affiliations = load_from(country_affiliations_path)
        print(f'loaded {get_short_path(country_affiliations_path)}')
    except:
        print(f'no {get_short_path(country_affiliations_path)} found. Writing {get_short_path(country_affiliations_path)}.')
        country_affiliations = get_countries_of_author(author_affiliations, countries, match_method=has_substring)
        save_to(country_affiliations, country_affiliations_path)
    
    authors_by_country = get_n_authors_by_country(country_affiliations, countries.keys())
    # map country code to country primary name
    authors_by_country = {countries[country_code][0]:n_authors for country_code, n_authors in authors_by_country.items()}
    list_to_csv(sorted(authors_by_country.items()), results_path)
    print(f'results saved to {get_short_path(results_path)}')

if __name__ == '__main__':
    sys.exit(main())