import re
import unicodedata
import pickle
import csv
from pathlib import Path

def get_short_path(path):
    return '/'.join(Path(path).parts[-2:])

def list_to_csv(l, filename):
	with open(filename, 'w') as f:
		wr = csv.writer(f)
		for row in l:
			wr.writerow(row)

def remove_duplicates(list):
    # removes duplicates from a list while preserving order
    return [*dict.fromkeys(list)]

def has_substring(str, substr):
    return substr in str

def has_word(str, word):
    # does not match word followd by digit e.g. germany1.
    # add \d* to allow digits.
    return re.search(f'(?<!\w){re.escape(word)}(?!\w)', str, re.IGNORECASE) != None

def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def format_name(full_name):
    full_name = full_name.strip()
    full_name = strip_accents(full_name)
    names = full_name.rsplit(' ', 1)
    last_name = names.pop()
    if len(names) > 0:
        initials = ''.join([c for c in names[0] if c.isupper()])
        return f'{initials} {last_name}'
    else:
        return last_name

def save_to(obj, filename):
    with open(filename, 'wb') as f:
        pickle.dump(obj, f)

def load_from(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)