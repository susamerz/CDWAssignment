'''
Country network

1. Go through the co_author_graph edges and add the edge's `weight` to edges between all countries in the node's `affiliated_countries` attribute.
2. Filter the graph by removing edges with weight less than a given threshold.
3. Filter the graph by removing nodes with no edges.
4. Find the largest connected subgraph.
5. Export the largest connected subgraph in nx.cytoscape.json format.
'''

import sys
from pathlib import Path
import networkx as nx 

from author_affiliations.author_network import export_cytoscape, weight_gte_threshold_filter, apply_edge_filter, get_country_network
from author_affiliations.utils import load_from, save_to, get_short_path

def main():
	cwd = Path(__file__).parent
	co_author_graph = load_from(cwd/'processed_data'/'co_author_graph.pkl')
	country_network_path = cwd/'processed_data'/'country_network.pkl'
	try:
		country_network = load_from(country_network_path)
		print(f'loaded country network from {get_short_path(country_network_path)}')
	except FileNotFoundError:
		print(f'no {get_short_path(country_network_path)} found, creating new country network')
		country_network = get_country_network(co_author_graph)
		save_to(country_network, country_network_path)

	# filter out edges with weight less than 1000
	country_network = apply_edge_filter(country_network, weight_gte_threshold_filter(country_network, threshold=1000))
	# drop nodes that have no edges
	country_network.remove_nodes_from(list(nx.isolates(country_network)))
	# get the largest connected subgraph
	country_network = country_network.subgraph(next(nx.connected_components(country_network)))
	export_cytoscape(country_network, cwd/'results'/'country_network.json')

if __name__ == '__main__':
	sys.exit(main())