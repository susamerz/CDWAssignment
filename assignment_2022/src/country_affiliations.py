from collections import defaultdict

# helper function to check if affiliation is in country
# stops when finds an affiliation.
def is_affiliated_with_country(affiliations, country_names, match_method):
	for affiliation in affiliations:
		for country_name in country_names:
			if match_method(affiliation, country_name):
				return True
	return False

def get_country_affiliations(author_affiliations, countries, match_method):
	# author --> countries affiliated to
	country_affiliations = defaultdict(set)
	for author, affiliations in author_affiliations.items():
		author_countries = set()
		for country_code, country_names in countries.items():
			if is_affiliated_with_country(affiliations, country_names, match_method):
				author_countries.add(country_code)
		country_affiliations[author].update(author_countries)
	return country_affiliations

def get_n_authors_by_country(country_affiliations, all_country_codes):
	# country --> number of authors
	authors_by_country = {country_code:0 for country_code in all_country_codes}
	for author, countries in country_affiliations.items():
		for country_code in countries:
			authors_by_country[country_code] += 1    
	return authors_by_country