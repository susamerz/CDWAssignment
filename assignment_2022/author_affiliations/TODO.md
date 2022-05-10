### Todo

- [ ] Use snakemake for the workflow
  - [ ] Divide scripts into smaller scripts, one output per script
  - [ ] Use smaller scripts in Snakefile
  - [ ] Remove try-except blocks, let snakefile handle dependencies between scripts in the workflow
  - [ ] Visualize DAG of the workflow
- [ ] Use classes to group code, at least for author_network
    - [ ] get_co_author_graph --> update/add to graph
- [ ] Separate scripts from package code
- [ ] Remove `/data` folder and give path to data as command line arg or as config var
