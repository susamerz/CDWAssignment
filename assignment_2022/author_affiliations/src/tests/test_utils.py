from utils import format_name, get_short_path, has_substring, has_word, merge_values_from_dicts, remove_duplicates

def test_has_word():
    assert has_word('usa', 'usa')
    assert has_word('usa.', 'usa')
    assert has_word('usa ', 'usa')
    assert has_word('a usa a', 'usa')
    assert not has_word('busan', 'usa')
    assert not has_word('busa', 'usa')
    assert not has_word('usan', 'usa')
    assert not has_word('usa1', 'usa')
    assert not has_word('u.a', 'usa')
    assert has_word('u.s.a', 'u.s.a')
    assert not has_word('umsma', 'u.s.a')

def test_has_substring():
    assert has_substring('usa', 'usa')
    assert has_substring('usa.', 'usa')
    assert has_substring('usa ', 'usa')
    assert has_substring('a usa a', 'usa')
    assert has_substring('busan', 'usa')
    assert has_substring('busa', 'usa')
    assert has_substring('usan', 'usa')
    assert has_substring('usa1', 'usa')
    assert not has_substring('u.a', 'usa')
    assert has_substring('u.s.a', 'u.s.a')
    assert not has_substring('umsma', 'u.s.a')

def test_format_name():
	correct_name = 'WE Coyote'
	full_names = [
		'Wile E. Coyote',
		'Wile Ethelbert Coyote',
		'W. E. Coyote',
		'WE Coyote',
		'Wilé E. Coyoté   '
	]
	for full_name in full_names:
		assert format_name(full_name) == correct_name

def test_remove_duplicates():
    assert remove_duplicates([1, 1, 2, 3, 3, 4, 5, 5]) == [1, 2, 3, 4, 5]

def test_get_short_path():
    assert get_short_path('/cwd/src/./../processed_data/file.txt') == 'processed_data/file.txt'

def test_merge_values_from_dicts():
    d1 = {'a': set([1, 2]), 'b': set([3, 4])}
    d2 = {'a': set([2, 3]), 'c': set([3, 4])}
    d3 = {'a': set([4, 3]), 'c': set([3, 4])}
    assert merge_values_from_dicts(d1, d2) == {'a': set([1, 2, 3]), 'b': set([3, 4]), 'c': set([3, 4])}
    assert merge_values_from_dicts(d1, d2, d3) == {'a': set([1, 2, 3, 4]), 'b': set([3, 4]), 'c': set([3, 4])}