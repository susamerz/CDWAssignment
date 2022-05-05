import json
from pathlib import Path
from itertools import combinations
import networkx as nx

from parsers import ArxivParser, PubmedParser
from utils import load_from, save_to

def add_weight_to_edge(G, edge):
	'''
	Adds 1 to the weight of the edge. If the edge does not exist, it is created.

	Parameters
	----------
	G : networkx.Graph
	edge : tuple(str, str)
	'''
	if G.has_edge(*edge):
		G.edges[edge]['weight'] += 1
	else:
		G.add_edge(*edge, weight=1)

def get_co_author_graph(parser, country_code):
	'''
	Returns a networkx.Graph of co-authors. The graph is weighted by the number of times the authors have collaborated.

	Parameters
	----------
	parser : XMLParser
	country_code : str

	Returns
	-------
	G : networkx.Graph
	'''
	article_gen = parser.get_article_generator_from_xml()
	co_author_graph = nx.Graph()
	processed_article_ids = set()
	for article in article_gen:
		article_id = parser.get_id_from_article(article)
		if article_id in processed_article_ids:
			continue # skip duplicate articles
		processed_article_ids.add(article_id)

		authors = parser.get_authors_from_article(article)
		nodes = [parser.get_name_from_author(author) for author in authors]
		author_pairs = list(combinations(nodes, 2))
		for pair in author_pairs:
			# check if both authors are affiliated to country_code
			# TODO move to separate function
			if all([country_code in country_affiliations[author] for author in pair]):
				add_weight_to_edge(co_author_graph, pair)
	return co_author_graph

def weight_gte_threshold_filter(G, threshold=10):
		'''
		Returns a filter function that returns True if the edge weight is greater than or equal to the threshold.

		Parameters
		----------
		G : networkx.Graph
		threshold : int, default=10

		Returns
		-------
		filter_function : function
		'''
		return lambda *edge: G.edges[edge]['weight'] >= threshold

if __name__ == '__main__':

	cwd = Path(__file__).parents[1]
	country_affiliations_path =  cwd/'processed_data'/'country_affiliations.pkl'
	country_affiliations = load_from(country_affiliations_path)

	co_author_graph =  get_co_author_graph(ArxivParser(), 'fin')

	with open(cwd/'processed_data'/'co_author_graph.json', 'w') as f:
		json.dump(nx.cytoscape_data(co_author_graph), f, indent=0)
