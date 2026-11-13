The run of `bug-recap-subject` stops. It opens no PR and pushes nothing.

Boundary: fails rule 3, no moved seam. After the red loop of item 1, the fix needs a new field in `page.json`. The `.lead` fact names the leader of a matchup only by its side, so the writer falls back to a bare "They". A field that names the team that led moves a seam.

The work stays on the branch `bug-recap-subject`: the quick file, the red loop `7b75240f`, and the finding in the quick file under `## Comments`. The queue task has the label `blocked`.

Run this to plan it as a feature:

4ag:plan name the team in each recap sentence, with a lead fact that names the team that led, so that no recap sentence opens with a bare "They"
