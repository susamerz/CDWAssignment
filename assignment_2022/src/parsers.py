from collections import defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET
import csv

from utils import format_name, get_short_path, remove_duplicates

class XMLParser():
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
        self.article_xpath = None
        self.article_id_xpath = None
    
    def get_author_affiliations(self):
        '''
        Parse the XML files in the given directory to dict(author, set(author's affiliations)).

        Returns
        -------
        author_affiliations : dict(str, set(str))
        '''
        self.author_affiliations = defaultdict(set)
        for article in self.get_article_generator_from_xml():
            authors = self.get_authors_from_article(article)
            for author_element in authors:
                author_name = self.get_name_from_author(author_element)
                if author_name is not None:
                    affiliation = author_element.find(self.affiliation_xpath)
                    if affiliation is not None:
                        self.author_affiliations[author_name].add(affiliation.text.lower())
        return self.author_affiliations
        
    def get_article_generator_from_xml(self):
        '''
        Get the XML files from dir_path and yield the article elements.
        
        Yields
        ------
        article : ElementTree.Element
            XML article element.
        '''
        filenames = sorted(self.dir_path.glob('*.xml'))
        for filename in filenames:
            try:
                tree = ET.parse(self.dir_path/filename)
            except:
                print(f'Skipping file: {get_short_path(self.dir_path/filename)}')
                continue
            root = tree.getroot()
            for article in root.findall(self.article_xpath):
                yield article

    def get_authors_from_article(self, article):
        '''
        Get the authors from the given article.

        Parameters
        ----------
        article : ElementTree.Element
            XML article element.

        Returns
        -------
        authors : set(ElementTree.Element)
            Set of XML author elements.
        '''
        return set(article.findall(self.author_xpath))

    def get_id_from_article(self, article):
        '''
        Get the article's ID from the given article element.
        '''
        return article.find(self.article_id_xpath).text

    def get_name_from_author(self, author_element):
        '''
        Get the author's name from the given author element. Returns None if the author's name is not valid.

        Parameters
        ----------
        author_element : ElementTree.Element
            XML author element.
        
        Returns
        -------
        author_name : str
            Author's name. None if the author's name is not valid.
        
        '''
        raise NotImplementedError

class ArxivParser(XMLParser):
    def __init__(self, dir_path=Path(__file__).parent/'../data/arxiv'):
        super().__init__(dir_path)
        self.author_xpath = './/{http://www.w3.org/2005/Atom}author'
        self.affiliation_xpath = './/{http://arxiv.org/schemas/atom}affiliation'
        self.article_xpath = './/{http://www.w3.org/2005/Atom}entry'
        self.article_id_xpath = './/{http://www.w3.org/2005/Atom}id'
        
    def get_name_from_author(self, author_element):
        author_name = author_element.find('.//{http://www.w3.org/2005/Atom}name')
        if author_name is not None:
            return format_name(author_name.text)
        else:
            return None

class PubmedParser(XMLParser):
    def __init__(self, dir_path=Path(__file__).parent/'../data/pubmed'):
        super().__init__(dir_path)
        self.author_xpath = './/Affiliation/../..'
        self.affiliation_xpath = './/AffiliationInfo/Affiliation'
        self.article_xpath = './/PubmedArticle'
        self.article_id_xpath = './/PMID'

    def get_name_from_author(self, author_element):
        last_name = author_element.find('.//LastName')
        if last_name is not None:
            last_name = last_name.text # use last name if available
        else:
            last_name = author_element.find('.//CollectiveName') # use collective name if last name is not available
            if last_name is not None:
                last_name = last_name.text
            else:
                return None # not a valid author name
        initials = author_element.find('.//Initials') # use initials as first name if available
        if initials is not None:
            first_names = initials.text
        else:
            forename = author_element.find('.//ForeName') # use forename if initials are not available
            if forename is not None:
                first_names = forename.text
            else:
                return None # not a valid author name
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
