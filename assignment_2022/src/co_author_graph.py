import json
from pathlib import Path
from itertools import combinations
import networkx as nx

from parsers import ArxivParser, PubmedParser
from utils import get_short_path, load_from, remove_duplicates, save_to

def export_cytoscape(G, filepath):
	with open(filepath, 'w') as f:
		json.dump(nx.cytoscape_data(G), f, indent=0)
		print(f'exported {get_short_path(filepath)}')

def add_co_author(G, pair, country_affiliations):
	'''
	Add the given co-author pair to the graph. If the pair already exists, increment the weight by 1. Sets attribute 'affiliated_countries' for each node.

	Parameters
	----------
	G : networkx.Graph
		The graph to add the pair to.
	pair : tuple(str, str)
		Tuple of the names of the co-authors.
	'''
	if G.has_edge(*pair):
		G.edges[pair]['weight'] += 1
	else:
		G.add_edge(*pair, weight=1)
		for node in pair:
			G.nodes[node]['affiliated_countries'] = country_affiliations[node]

def get_co_author_graph(parser, country_affiliations, initial_graph=None):
	'''
	Create a co-author graph from articles in the given parser. The graph is weighted by the number of times the authors have collaborated. Can be initialized with an existing graph.

	Parameters
	----------
	parser : XMLParser
	country_affiliations : dict
	initial_graph : networkx.Graph, optional

	initial_graph : networkx.Graph, default=None

	Returns
	-------
	G : networkx.Graph
	'''
	co_author_graph = nx.Graph() if initial_graph is None else initial_graph.copy()
	article_gen = parser.get_article_generator_from_xml()
	articles = remove_duplicates(article_gen)
	for article in articles:
		nodes = set()
		for author_element in article.author_elements:
			author_name = parser.get_name_from_author(author_element)
			if author_name is not None:
				nodes.add(author_name)
		co_author_pairs = list(combinations(nodes, 2))
		for pair in co_author_pairs:
			add_co_author(co_author_graph, pair, country_affiliations)
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

def country_affiliation_filter(G, country_code):
	'''
	Returns a filter function that returns True if the node has the given country code in its `affiliated_countries` attribute.

	Parameters
	----------
	G : networkx.Graph
	country_code : str

	Returns
	-------
	filter_function : function
	'''
	return lambda node: country_code in G.nodes[node]['affiliated_countries']

def apply_edge_filter(G, filter_function):
	'''
	Returns a copy of the graph with edges filtered by the given filter function.

	Parameters
	----------
	G : networkx.Graph
	filter_function : function

	Returns
	-------
	filtered_G : networkx.Graph
	'''
	filtered_G = G.copy()
	for edge in G.edges:
		if not filter_function(*edge):
			filtered_G.remove_edge(*edge)
	return filtered_G

def apply_node_filter(G, filter_function):
	'''
	Returns a copy of the graph with nodes filtered by the given filter function.

	Parameters
	----------
	G : networkx.Graph
	filter_function : function

	Returns
	-------
	filtered_G : networkx.Graph
	'''
	filtered_G = G.copy()
	for node in G.nodes:
		if not filter_function(node):
			filtered_G.remove_node(node)
	return filtered_G

if __name__ == '__main__':
	cwd = Path(__file__).parents[1]
	co_author_graph_path = cwd/'processed_data'/'co_author_graph.pkl'
	try:
		co_author_graph = load_from(co_author_graph_path)
		print(f'loaded {get_short_path(co_author_graph_path)}')
	except FileNotFoundError:
		print(f'no {get_short_path(co_author_graph_path)} found. Creating new graph...')
		country_affiliations = load_from(cwd/'processed_data'/'country_affiliations.pkl') # TODO: what to do if the file is not found? proper makefile?
		arxiv_co_author_graph = get_co_author_graph(ArxivParser(), country_affiliations)
		co_author_graph = get_co_author_graph(PubmedParser(), country_affiliations, initial_graph=arxiv_co_author_graph)
		save_to(co_author_graph, co_author_graph_path)
	
	fin_co_author_graph_path = cwd/'processed_data'/'fin_co_author_graph.pkl'
	try:
		fin_co_author_graph = load_from(fin_co_author_graph_path)
		print(f'loaded {get_short_path(fin_co_author_graph_path)}')
	except:
		print(f'no {get_short_path(fin_co_author_graph_path)} found. Creating new graph...')
		# filter out non-finnish authors 
		fin_co_author_graph = apply_node_filter(co_author_graph, country_affiliation_filter(co_author_graph, 'fin'))
		# filter out edges with weight less than 10
		fin_co_author_graph = apply_edge_filter(fin_co_author_graph, weight_gte_threshold_filter(fin_co_author_graph, 10))
		# drop nodes that have no edges
		fin_co_author_graph.remove_nodes_from(list(nx.isolates(fin_co_author_graph)))
		save_to(fin_co_author_graph, fin_co_author_graph_path)

	# get the largest connected subgraph
	fin_co_author_graph = fin_co_author_graph.subgraph(next(nx.connected_components(fin_co_author_graph)))

	# convert affiliated_countries to a list to allow for json serialization
	for node in fin_co_author_graph.nodes:
		fin_co_author_graph.nodes[node]['affiliated_countries'] = list(fin_co_author_graph.nodes[node]['affiliated_countries'])

	export_cytoscape(fin_co_author_graph, cwd/'results'/'fin_co_author_graph.json')