# Bye week on the manager page: map

App: both.
Spec branch: `zz-dry-run`.

## DESTINATION

One spec: each player on the manager page shows the NFL bye week of his team, from the pipeline data. (dry run)

## DECISIONS SO FAR

- The top performer rows and the best add rows show the bye week. The page gets no roster list. `decisions/01-grill-which-rows-show-the-bye.md`.
- A coming bye reads "Bye 9", and a passed bye reads "Bye done". `decisions/02-spec-the-bye-week-text.md`.

## NOT YET SPECIFIED

None yet.

## OUT OF SCOPE

- The bye line of the next-week game cards. It exists, and the `next-week-byes` feature owns it. (dry run)
- A roster list on the manager page. It is a feature of its own (decision 01). (dry run)
