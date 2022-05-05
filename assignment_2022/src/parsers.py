from collections import defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET
import csv

from utils import format_name, get_short_path, remove_duplicates

class Parser():
    def __init__(self, dir_path):
        '''
        Class for parsing XML files.

        Parameters
        ----------
        dir_path : Path
        '''
        self.dir_path = Path(dir_path)
        self.author_xpath = None
        self.affiliation_xpath = None
        self.author_affiliations = None
    
    def get_author_affiliations_from_xml(self):
        '''
        Parse the XML files in the given directory to dict(author, set(author's affiliations)).

        Returns
        -------
        author_affiliations : dict(str, set(str))
        '''
        self.author_affiliations = defaultdict(set)
        filenames = sorted(self.dir_path.glob('*.xml'))
        for filename in filenames:
            try:
                tree = ET.parse(self.dir_path/filename)
            except:
                print(f'skipping {get_short_path(self.dir_path/filename)}')
                continue
            root = tree.getroot()
            for author_element in root.findall(self.author_xpath):
                author_name = self.get_name_from_author(author_element)
                affiliation = author_element.find(self.affiliation_xpath).text.lower()
                self.author_affiliations[author_name].add(affiliation)
        return self.author_affiliations

    def get_name_from_author(self, author_element):
        '''
        Get the author's name from the given author element.

        Parameters
        ----------
        author_element : ElementTree.Element
            XML author element.
        
        Returns
        -------
        author_name : str
        '''
        raise NotImplementedError

class ArxivParser(Parser):
    def __init__(self, dir_path=Path(__file__).parent/'../data/arxiv'):
        super().__init__(dir_path)
        self.author_xpath='.//{http://arxiv.org/schemas/atom}affiliation/..'
        self.affiliation_xpath='.//{http://arxiv.org/schemas/atom}affiliation'
        
    def get_name_from_author(self, author_element):
        author_name = author_element.find('.//{http://www.w3.org/2005/Atom}name').text
        return format_name(author_name)

class PubmedParser(Parser):
    def __init__(self, dir_path=Path(__file__).parent/'../data/pubmed'):
        super().__init__(dir_path)
        self.author_xpath = './/Affiliation/../..'
        self.affiliation_xpath = './/AffiliationInfo/Affiliation'

    def get_name_from_author(self, author_element):
        last_name = author_element.find('.//LastName')
        if last_name is not None:
            last_name = last_name.text # use last name if available
        else:
            last_name = author_element.find('.//CollectiveName') # use collective name if last name is not available
            if last_name is not None:
                last_name = last_name.text
            else:
                last_name = '' # use empty string if neither last name nor collective name is available
        initials = author_element.find('.//Initials') # use initials as first name if available
        if initials is not None:
            first_names = initials.text
        else:
            forename = author_element.find('.//ForeName') # use forename if initials are not available
            if forename is not None:
                first_names = forename.text
            else:
                first_names = '' # use empty string if neither forename nor initials are available
        return format_name(f'{first_names} {last_name}')

def parse_countries_from_csv(filename=Path(__file__).parent/'../data/AltCountries.csv'):
    '''
    Parse the given CSV file to dict(country_code, list(country_name)).

    Parameters
    ----------
    filename : str or Path
        Path to the CSV file.

    Returns
    -------
    countries : dict(str, list(str))
        Dictionary of country codes and country names. The primary name is the first element of the list.
    '''
    countries = defaultdict(list)
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
