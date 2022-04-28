import os
import csv
from collections import defaultdict
import xml.etree.ElementTree as ET

from utils import format_name, get_short_path, remove_duplicates

def read_country_csv(filename, countries=defaultdict(list)):
    with open(filename, newline='') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        next(rows, None) # skip header
        for row in rows:
            country_code = row[0].lower()
            main_name = row[1].lower()
            alt_names = row[2].lower().split('\t')
            if len(country_code) != 3:
                country_code = main_name[:3]
            updated_name_list = remove_duplicates([*countries[country_code], main_name, *alt_names])
            countries[country_code] = updated_name_list
    return countries

def read_xml_files(dir_path, author_xpath, affiliation_xpath, get_name_from_author, namespace={}, author_affiliations = defaultdict(set)):
    filenames = sorted([filename for filename in os.listdir(dir_path) if filename[-4:] == '.xml'])
    for filename in filenames:
        try:
            tree = ET.parse(os.path.join(dir_path, filename))
        except:
            print(f'skipping {get_short_path(os.path.join(dir_path, filename))}')
            continue
        root = tree.getroot()
        for author_element in root.findall(author_xpath, namespace):
            author_name = get_name_from_author(author_element, namespace)
            affiliation = author_element.find(affiliation_xpath, namespace).text.lower()
            author_affiliations[author_name].add(affiliation)
    return author_affiliations

def get_name_from_arxiv_author(arxiv_author, namespace):
    author_name = arxiv_author.find('.//w3:name', namespace).text
    return format_name(author_name)

def get_name_from_pubmed_author(pubmed_author, namespace=None):
        last_name = pubmed_author.find('.//LastName')
        if last_name is not None:
            last_name = last_name.text
        else:
            last_name = pubmed_author.find('.//CollectiveName')
            if last_name is not None:
                last_name = last_name.text
            else:
                last_name = ''
        initials = pubmed_author.find('.//Initials')
        if initials is not None:
            first_names = initials.text
        else:
            forename = pubmed_author.find('.//ForeName')
            if forename is not None:
                first_names = forename.text
            else:
                first_names = ''
        return format_name(f'{first_names} {last_name}')