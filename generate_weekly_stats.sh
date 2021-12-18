echo "WARNING! This script is super slow. It collects per-week-country tag statistics since dec 2020."
echo "Please consider using get_counts.py instead!"
d=2020-12-02
while [ "$d" != 2021-12-15 ]; do 
  echo $d
  ./compare_tags_by_country.sh  --tag1 waterway=riverbank --tag2 water=river --map history/map-$d.png --server https://overpass-api.de --csv history/tags-$d.csv --date "$d"
  d=$(date -I -d "$d + 7 day")
done
