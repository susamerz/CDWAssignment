from collections import defaultdict

def is_affiliated_with_country(affiliations, country_names, match_method):
	'''
	Helper function to check if affiliation is in country. Stops when finds an affiliation.

	Parameters
	----------
	affiliations : set(str)
		Set of affiliations.

	Returns
	-------
	is_affiliated : bool
	'''
	for affiliation in affiliations:
		for country_name in country_names:
			if match_method(affiliation, country_name):
				return True
	return False

def get_countries_of_author(author_affiliations, countries, match_method):
	'''
	Get a dictionary of authors affiliations to countries.
	
	Parameters
	----------
	author_affiliations : dict(str, set(str))
		Dictionary of author --> set(affiliations).
	countries : list(str)
		List of country names.
	match_method : function
		Function to match affiliation with country.
	
	Parameters
	----------
	countries_of_author : dict(str, set(str))
		Dictionary of author --> set(affiliated countries).
	'''
	countries_of_author = defaultdict(set)
	for author, affiliations in author_affiliations.items():
		author_countries = set()
		for country_code, country_names in countries.items():
			if is_affiliated_with_country(affiliations, country_names, match_method):
				author_countries.add(country_code)
		countries_of_author[author].update(author_countries)
	return countries_of_author

def get_n_authors_by_country(country_affiliations, all_country_codes):
	'''
	Get a dictionary of countries to number of authors.

	Parameters
	----------
	country_affiliations : dict(str, set(str))
		Dictionary of author --> set(affiliations).
	all_country_codes : list(str)
		List of country codes.
		
	Returns
	-------
	n_authors_by_country : dict(str, int)
		Dictionary of country code --> number of authors.
	'''
	authors_by_country = {country_code:0 for country_code in all_country_codes}
	for author, countries in country_affiliations.items():
		for country_code in countries:
			authors_by_country[country_code] += 1    
	return authors_by_country