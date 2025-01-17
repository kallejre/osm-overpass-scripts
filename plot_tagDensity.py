#!/usr/bin/env python3
# Python-script to process and plot tag usage data world-wide
# usage: ./plot_tagDensity.py [-i input.csv] [-o output.png|.jpg|.pdf] [--tag tag_name] [-w <num>] [-b <lat,lon,lat,lon>] [-c <yes|no>]
#        -i|--input          - input file in csv format with header and two columns containing lat, lon coordinates [default or -: stdin]
#        -o|--output         - output picture file formats: png, jpg, pdf (default: .png with autogenerated name)
#        -t|--tag            - name of tag to displey in plot title
#        -w|--binwidth       - size of square for object counting in degrees. 1 means 1˚x1˚ square (defalut: 1)
#        -b|--bbox           - plot only area within bbox. Four coordinates seprated by , [lat,lon,lat,lon] (defalut: -55,-180,90,180)
#        -c|--countries      - plot countries' borders [yes|no] (default: no)
# binning idea from: https://stackoverflow.com/questions/11507575/basemap-and-density-plots

print('Python script was started')
import datetime
import sys
import csv
import argparse
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from matplotlib import rc
from datetime import date

# SOurce of this list: https://matplotlib.org/stable/gallery/color/colormap_reference.html
cmap_names = ['cividis', 'inferno', 'magma', 'plasma', 'viridis', 'Blues', 'BuGn', 'BuPu', 'GnBu', 
        'Greens', 'Greys', 'OrRd', 'Oranges', 'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds',
        'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd', 'Wistia', 'afmhot', 'autumn', 'binary', 'bone', 'cool', 
        'copper', 'gist_gray', 'gist_heat', 'gist_yarg', 'gray', 'hot', 'pink', 'spring', 'summer', 
        'winter', 'BrBG', 'PRGn', 'PiYG', 'PuOr', 'RdBu', 'RdGy', 'RdYlBu', 'RdYlGn', 'Spectral', 
        'bwr', 'coolwarm', 'seismic', 'hsv', 'twilight', 'twilight_shifted', 'Accent', 'Dark2', 
        'Paired', 'Pastel1', 'Pastel2', 'Set1', 'Set2', 'Set3', 'tab10', 'tab20', 'tab20b', 'tab20c',
        'CMRmap', 'brg', 'cubehelix', 'flag', 'gist_earth', 'gist_ncar', 'gist_rainbow', 'gist_stern',
        'gnuplot', 'gnuplot2', 'jet', 'nipy_spectral', 'ocean', 'prism', 'rainbow', 'terrain', 'turbo']

def get_defaults():
    with open('defaults.sh') as f:
        config=list(map(lambda x: tuple(x.split('=', 1)),filter(lambda x:'=' in x,f.readlines())))
    return dict(config)
defaults=get_defaults()


parser = argparse.ArgumentParser(description='Script for creating files contating names of reads that bear given number of mutations')
parser.add_argument('-i', '--input', type=str,
                    help='Input CSV file lat, lon coordinates')
parser.add_argument('-o', '--output', type=str,
                    help='Outputfile for plot (.png, ,jpg, .pdf)',
                    default="plot_" + str(datetime.datetime.now()) + ".png")
parser.add_argument('-t', '--tag', type=str,
                    help='tag name',
                    default=defaults["DEFAULT_TAG1"])
parser.add_argument('-w', '--binwidth', type=float,
                    help='size of square for object counting in degrees',
                    default=1)
parser.add_argument('-b', '--bbox', type=str,
                    help='four coordinates separeatd by comma',
                    default="-55,-180,90,180")
parser.add_argument('-c', '--countries', type=str, choices=['yes', 'no'],
                    help='whether to plot borders (default: no)',
                    default='no')
parser.add_argument('-C', '--colmap', type=str, choices=cmap_names,
                    help='Name of the pyplot color map used for heatmap',
                    default='plasma')  # I liked rainbow.


args = parser.parse_args()
bbox = args.bbox.split(",")
print("BBOX:", bbox)
# input()
if bbox != [""]:
    bbox = [float(x) for x in bbox]
else:
    bbox = [-90,-180,90,180]


if args.input == '-':
    overpass = np.genfromtxt(sys.stdin, delimiter=',', skip_header=1)
else:
    overpass = np.genfromtxt(args.input, delimiter=',', skip_header=1)


world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
if args.countries == 'no':
    world = world.dissolve()

# Calculate how many bins do we need to split the world
nx = int(360 / args.binwidth)
ny = int(180 / args.binwidth)

# Create bin edges
lon_bins = np.linspace(-180, 180, nx+1)
lat_bins = np.linspace(-90, 90, ny+1)

# Calculate frequency in each square bin
density, _, _ = np.histogram2d(overpass[:, 0], overpass[:, 1], [lat_bins, lon_bins])

# Turn the lon/lat bins into 2 dimensional arrays
lon_bins_2d, lat_bins_2d = np.meshgrid(lon_bins, lat_bins)


fig, ax = plt.subplots()
# ax.set_aspect('equal')
ax.set_facecolor('black')
ax.axis([bbox[1], bbox[3], bbox[0], bbox[2]])
ax.set_title(args.tag, fontsize=15)

plt.pcolormesh(lon_bins_2d, lat_bins_2d, np.log10(density), cmap=args.colmap, zorder=1)
world.boundary.plot(ax=ax, edgecolor='grey', linewidth=0.25, zorder=2)

plt.colorbar(label=r'$log_{10}$', fraction=0.04, aspect=6)
fig.text(.77, .22, str(date.today()), ha='center')

plt.savefig(args.output, dpi = 300, bbox_inches='tight')

