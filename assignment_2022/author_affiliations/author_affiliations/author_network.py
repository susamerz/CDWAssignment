'''
This module contains functions for creating and manipulating co-author and country networks.
'''

import json
from itertools import combinations
import networkx as nx

from author_affiliations.utils import get_short_path, remove_duplicates

def export_cytoscape(G, filepath):
	with open(filepath, 'w') as f:
		json.dump(nx.cytoscape_data(G), f, indent=0)
		print(f'exported {get_short_path(filepath)}')

def get_largest_connected_subgraph(G):
		return G.subgraph(next(nx.connected_components(G)))

def remove_isolates(G):
	'''
	Removes nodes that have no edges.
	'''
	return G.subgraph(list(nx.isolates(G)))

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

def add_co_author_to_country_network(co_author_graph, edge, country_network):
	'''
	Adds the edge's `weight` to edges between all countries in the node's `affiliated_countries` attribute.

	Parameters
	----------
	co_author_graph : networkx.Graph
	edge : tuple
	country_network : networkx.Graph
	'''
	weight = co_author_graph.edges[edge]['weight']
	for country_code in co_author_graph.nodes[edge[0]]['affiliated_countries']:
		for country_code2 in co_author_graph.nodes[edge[1]]['affiliated_countries']:
			if country_network.has_edge(country_code, country_code2):
				country_network.edges[country_code, country_code2]['weight'] += weight
			else:
				country_network.add_edge(country_code, country_code2, weight=weight)

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

def get_country_network(co_author_graph):
	'''
	Creates a country network from the given co-author graph.

	Parameters
	----------
	co_author_graph : networkx.Graph

	Returns
	-------
	country_network : networkx.Graph
	'''
	country_network = nx.Graph()
	for edge in co_author_graph.edges:
		add_co_author_to_country_network(co_author_graph, edge, country_network)
	return country_network

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
