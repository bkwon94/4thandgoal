#!/bin/bash
# One pass of the analyzer flow with agent-browser: $1 = media motion (reduced-motion or no-preference), $2 = theme, $3 = shot prefix or "".
AB=agent-browser
R='(() => { const h=document.querySelector("[data-halo]"); const o=h.querySelector("[data-orbit]"); const b=[...document.querySelectorAll("button")].find(x=>/Grade the Trade|Grading/.test(x.textContent)); return "level="+h.dataset.level+" opacity="+getComputedStyle(h).opacity+" halo transition-duration="+getComputedStyle(h).transitionDuration+" orbit="+(o?("display:"+getComputedStyle(o).display+" animation:"+getComputedStyle(o).animationName+" "+getComputedStyle(o).animationDuration):"none")+" grade button disabled="+b.disabled; })()'
clickText='(t) => { const b=[...document.querySelectorAll("button")].find(x=>x.textContent.trim().startsWith(t)); b.click(); return b.textContent.trim(); }'
$AB set viewport 375 900 >/dev/null
$AB set media $2 $1 >/dev/null
$AB open http://127.0.0.1:4173/analyze/ >/dev/null
$AB eval "localStorage.setItem('cpc.theme','$2')" >/dev/null; $AB reload >/dev/null; $AB wait 1500 >/dev/null
$AB eval 'matchMedia("(prefers-reduced-motion: reduce)").matches' | sed 's/^/reduced-motion matches: /'
$AB fill 'input[type=password]' localtest >/dev/null; $AB click 'button[type=submit]' >/dev/null; $AB wait 2500 >/dev/null
echo "no team: $($AB eval "$R")"
$AB click 'button[aria-label="Pick Your Team"]' >/dev/null; $AB wait 900 >/dev/null; $AB click 'ul[aria-label="Teams"] li:nth-child(1) button' >/dev/null; $AB wait 900 >/dev/null
echo "one team (The Blue Tent): $($AB eval "$R")"
$AB click 'button[aria-label="Pick Team Two"]' >/dev/null; $AB wait 900 >/dev/null; $AB click 'ul[aria-label="Teams"] li:nth-child(3) button' >/dev/null; $AB wait 900 >/dev/null
echo "two teams (The Blue Tent, Lil Fridge): $($AB eval "$R")"
$AB eval "($clickText)('Add a player Your Team gets')" >/dev/null; $AB wait 1200 >/dev/null; $AB click '[role=dialog] ul[aria-label^="Players of"] li:first-child button' >/dev/null; $AB wait 400 >/dev/null; $AB press Escape >/dev/null; $AB wait 900 >/dev/null
echo "one player (Your Team gets the first player of Lil Fridge): $($AB eval "$R")"
$AB eval "($clickText)('Add a player Team Two gets')" >/dev/null; $AB wait 1200 >/dev/null; $AB click '[role=dialog] ul[aria-label^="Players of"] li:first-child button' >/dev/null; $AB wait 400 >/dev/null; $AB press Escape >/dev/null; $AB wait 900 >/dev/null
echo "full trade (each team gets one player): $($AB eval "$R")"
[ -n "$3" ] && $AB screenshot "$3-375-$2.png" >/dev/null && echo "screenshot: $(basename $3)-375-$2.png"
$AB eval "($clickText)('Add a player Team Two gets')" >/dev/null; $AB wait 1200 >/dev/null; $AB click '[role=dialog] button[aria-checked="true"]' >/dev/null; $AB wait 400 >/dev/null; $AB press Escape >/dev/null; $AB wait 900 >/dev/null
echo "one player removed (Team Two gets none): $($AB eval "$R")"
