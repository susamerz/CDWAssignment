import os
from country_affiliations import get_country_affiliations, get_n_authors_by_country
from utils import has_substring, list_to_csv, save_to, load_from
from read_data import get_name_from_arxiv_author, get_name_from_pubmed_author, read_country_csv, read_xml_files

if __name__ == '__main__':

    processed_data_dir = './../processed_data/'
    author_affiliations_path = os.path.join(processed_data_dir, 'author_affiliations.pkl')
    country_affiliations_path = os.path.join(processed_data_dir, 'country_affiliations.pkl')
    authors_by_country_path = os.path.join(processed_data_dir, 'authors_by_country.pkl')
    results_path = './../results/authors_by_country.csv'

    try:
        author_affiliations = load_from(author_affiliations_path)
        print(f'loaded {author_affiliations_path}')
    except:
        print(f'no {author_affiliations_path} found. Writing {author_affiliations_path}.')
        namespace = {
            'w3': 'http://www.w3.org/2005/Atom',
            'arxiv_schema': 'http://arxiv.org/schemas/atom',
        }
        author_affiliations = read_xml_files(
            dir_path='./../data/arxiv',
            author_xpath='.//arxiv_schema:affiliation/..',
            affiliation_xpath='.//arxiv_schema:affiliation',
            get_name_from_author=get_name_from_arxiv_author,
            namespace=namespace,
        )
        author_affiliations = read_xml_files(
            dir_path='./../data/pubmed',
            author_xpath='.//Affiliation/../..',
            affiliation_xpath='.//AffiliationInfo/Affiliation',
            get_name_from_author=get_name_from_pubmed_author,
            author_affiliations = author_affiliations
        )
        save_to(author_affiliations, author_affiliations_path)
    
    countries = read_country_csv('./../data/AltCountries.csv')

    try:
        country_affiliations = load_from(country_affiliations_path)
        print(f'loaded {country_affiliations_path}')
    except:
        print(f'no {country_affiliations_path} found. Writing {country_affiliations_path}.')
        country_affiliations = get_country_affiliations(author_affiliations, countries, match_method=has_substring)
        save_to(country_affiliations, country_affiliations_path)
    
    authors_by_country = get_n_authors_by_country(country_affiliations)
    list_to_csv(sorted(authors_by_country.items()), results_path)
    print(f'results saved to {results_path}')
    print(f'top 10 countries by number of authors:\n{sorted(authors_by_country.items(), key=lambda x: x[1], reverse=True)[:10]}')