import sys
from pathlib import Path

from author_affiliations.parsers import ArxivParser, PubmedParser
from author_affiliations.utils import get_short_path, load_from, save_to
from author_affiliations.author_network import get_co_author_graph, apply_node_filter, apply_edge_filter, country_affiliation_filter, weight_gte_threshold_filter, remove_isolates, get_largest_connected_subgraph, export_cytoscape

def main():
	cwd = Path(__file__).parent
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
		
		fin_co_author_graph = remove_isolates(fin_co_author_graph)
		save_to(fin_co_author_graph, fin_co_author_graph_path)

	fin_co_author_graph = get_largest_connected_subgraph(fin_co_author_graph)

	# convert affiliated_countries to a list to allow for json serialization
	for node in fin_co_author_graph.nodes:
		fin_co_author_graph.nodes[node]['affiliated_countries'] = list(fin_co_author_graph.nodes[node]['affiliated_countries'])

	export_cytoscape(fin_co_author_graph, cwd/'results'/'fin_co_author_graph.json')

if __name__ == '__main__':
	sys.exit(main())