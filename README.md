# osm-overpass-scripts
Shell scripts for manipulating OpenStreetMap overpass queries

Currently, these scripts only handle tag comparison.  However, the intent is to build up a library of generic scripts that can be used for tag comparisons and statistics generation.

Usage:

	./csv_compare_tags.sh --server <overpass server url> --tag1 "waterway=river" --tag2 "water=river" | tee <output file>.csv
    ./csv_compare_tags.sh --server <overpass server url> --tag1 "waterway=river" --tag2 "water=river" | ./plot_overPass.R [-o output.png|.jpg|.pdf]

Requires:
    R https://cran.r-project.org/

## Installation

Install the following pre-requisites:
* R script

Run:
	sudo ./install.R
