#!/bin/sh
# The start script of the Cornerstone API container: it seeds the /data volume from the image, then runs the server.
# The first boot copies all the tracked data. Every boot copies the hand-kept returns files again, so a deploy updates them.
# pipefail is absent: /bin/sh is POSIX sh, which may not have it, and the script has no pipe.
set -eu

SEED=/app/seed/data
DATA=/data
# A marker file, not an empty check: a new Fly volume already holds lost+found, so it is never empty.
MARKER="$DATA/.seeded"

mkdir -p "$DATA"
if [ ! -f "$MARKER" ]; then
    echo "entrypoint: first boot, so the tracked data goes onto the volume"
    cp -a "$SEED/." "$DATA/"
    touch "$MARKER"
fi

# The service never writes a returns file. The only change comes from a commit and a deploy, so the image copy wins.
for seed_returns in "$SEED"/*/returns.json; do
    [ -f "$seed_returns" ] || continue
    season_dir="$DATA/$(basename "$(dirname "$seed_returns")")"
    mkdir -p "$season_dir"
    cp "$seed_returns" "$season_dir/returns.json"
done

exec "$@"
