#!/bin/sh
# The start script of the Cornerstone API container: it seeds the /data volume from the image, then runs the server.
# The first boot copies all the tracked data. Every boot copies the hand-kept returns files again, so a deploy updates them.
# A volume in the old layout, with the season folders at its root, moves one time to the client layout.
# pipefail is absent: /bin/sh is POSIX sh, which may not have it, and the script has no pipe.
set -eu

# SEED and DATA have defaults for the image. A test sets them to temp folders.
SEED="${SEED:-/app/seed/data}"
DATA="${DATA:-/data}"
# A marker file, not an empty check: a new Fly volume already holds lost+found, so it is never empty.
MARKER="$DATA/.seeded"
# The marker of the client layout: clients/<slug>/data for the league data, and nfl/ for the shared NFL data.
LAYOUT_MARKER="$DATA/.layout-clients"
# The one client of the old layout. Its season folders sat at the root of the volume.
OLD_CLIENT=cpc

mkdir -p "$DATA"
if [ ! -f "$MARKER" ]; then
    echo "entrypoint: first boot, so the tracked data goes onto the volume"
    cp -a "$SEED/." "$DATA/"
    touch "$MARKER" "$LAYOUT_MARKER"
fi

# The old layout held data/<season>/ and data/cache/. The move keeps every file the service wrote after the seed.
if [ ! -f "$LAYOUT_MARKER" ]; then
    echo "entrypoint: the volume moves to the client layout"
    client_data="$DATA/clients/$OLD_CLIENT/data"
    mkdir -p "$client_data" "$DATA/nfl/cache"
    for season_dir in "$DATA"/[0-9][0-9][0-9][0-9]; do
        [ -d "$season_dir" ] || continue
        season="$(basename "$season_dir")"
        # The returns file is shared NFL data, so it leaves the client data.
        if [ -f "$season_dir/returns.json" ]; then
            mkdir -p "$DATA/nfl/$season"
            mv "$season_dir/returns.json" "$DATA/nfl/$season/returns.json"
        fi
        mv "$season_dir" "$client_data/$season"
    done
    # The NFL caches move to the shared NFL folder. The result cache stays, because fly.toml names its path.
    for name in players.json nflverse charts; do
        if [ -e "$DATA/cache/$name" ] && [ ! -e "$DATA/nfl/cache/$name" ]; then
            mv "$DATA/cache/$name" "$DATA/nfl/cache/$name"
        fi
    done
    # The old layout had no league file of each season. The seed gives it, and a file on the volume wins.
    for seed_league in "$SEED"/clients/*/data/*/league.json; do
        [ -f "$seed_league" ] || continue
        target="$DATA/${seed_league#"$SEED"/}"
        if [ ! -f "$target" ]; then
            mkdir -p "$(dirname "$target")"
            cp "$seed_league" "$target"
        fi
    done
    touch "$LAYOUT_MARKER"
fi

# A client that is new to the image has no data folder on a seeded volume, so its seed folder goes on one time.
# A folder on the volume stays as it is, because the service writes the history and the raw weeks into it.
for seed_client in "$SEED"/clients/*/data; do
    [ -d "$seed_client" ] || continue
    target="$DATA/${seed_client#"$SEED"/}"
    if [ ! -d "$target" ]; then
        echo "entrypoint: the data of a new client goes onto the volume: $target"
        mkdir -p "$(dirname "$target")"
        cp -a "$seed_client" "$target"
    fi
done

# The service never writes a returns file. The only change comes from a commit and a deploy, so the image copy wins.
for seed_returns in "$SEED"/nfl/*/returns.json; do
    [ -f "$seed_returns" ] || continue
    season_dir="$DATA/nfl/$(basename "$(dirname "$seed_returns")")"
    mkdir -p "$season_dir"
    cp "$seed_returns" "$season_dir/returns.json"
done

exec "$@"
