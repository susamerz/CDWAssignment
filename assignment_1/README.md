# Running the pipeline

Workflow is implemented with snakemake (`python -m pip install snakemake`).

* Run the workflow:

        snakemake -j 1

  Average brain is plotted in `plots/average.png`
  and individual brains in `plots/subjX.png`.

* (Optional) To visualize the workflow to `dag.svg`:

        snakemake --dag | dot -Tsvg > dag.svg

