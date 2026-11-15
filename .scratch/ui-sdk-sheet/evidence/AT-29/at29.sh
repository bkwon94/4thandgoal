#!/bin/bash
# The bundle sum of AT-29: the gzip size, level 9, of each /_next/static/**/*.js file that out/<page>/index.html loads.
# Usage: at29.sh <site dir>. It lists each chunk with its gzip size, then the sum of the page.
cd "$1/out" || exit 1
for page in rankings ""; do
  total=0
  echo "page /$page"
  for f in $(grep -oE '/_next/static/[^"]+\.js' ${page:+$page/}index.html | sort -u); do
    n=$(gzip -9 -c ".$f" | wc -c | tr -d ' '); total=$((total+n))
    echo "  $n $f"
  done
  echo "sum /$page : $total"
done
