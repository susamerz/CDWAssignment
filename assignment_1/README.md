# Running the pipeline

1. Fetch test data:

        wget http://data.pymvpa.org/datasets/haxby2001/subj1-2010.01.14.tar.gz
        tar xvf subj1-2010.01.14.tar.gz

1. Searchlight analysis:

        python src/main.py --rsa_fpath rsa.npz
        python src/plot.py rsa.npz


## Testing scripts for subtasks

1. Preprocess the data (a temporary file is created):

        python src/preprocess.py

1. Load the temporary file, calculate and visualize
   a representational dissimilarity matrix (RDM)
   and a representational similarity analysis (RSA) score:

        python src/rdm.py
