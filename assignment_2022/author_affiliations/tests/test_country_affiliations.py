from author_affiliations.country_affiliations import is_affiliated_with_country, get_countries_of_author, get_n_authors_by_country
from author_affiliations.utils import has_substring

def test_is_affiliated_with_country():
	assert is_affiliated_with_country({'university of california, berkeley, usa'}, ['usa', 'u.s.a'], has_substring)
	assert not is_affiliated_with_country({'university of california, berkeley, umsma'}, ['usa', 'u.s.a'], has_substring)

def test_get_country_affiliations():
	assert get_countries_of_author(
		{
			'author1': ['university of california, berkeley, usa'],
			'author2': ['university of california, berkeley, umsma']
		},
		{
			'usa': ['usa'],
			'fra': ['france']
		}, has_substring) == {'author1': {'usa'}, 'author2': set()}

def test_get_n_authors_by_country():
	assert get_n_authors_by_country(
		{
			'author1': {'usa'},
			'author2': {'usa', 'fra'}
		},
		{'usa', 'fra', 'fin'}) == {'usa': 2, 'fra': 1, 'fin': 0}