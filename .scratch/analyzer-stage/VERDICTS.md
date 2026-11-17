ACCEPTANCE.md: f4fc4b13a02eb901be038d2d2a90b7d0743ed4f0
EVIDENCE.md: e07d5d19d26f30191e16149059e88addb1af665b

Test verdicts
AT-1: PASS
AT-2: FAIL The Then line holds in the after shots, but the Observation says both rows show before the add, and the before shots show no stage rows at all.
AT-3: FAIL The Observation gives the line at 13 to 29 ms and the shots at 12 to 34 ms, but output.txt shows 6.2 to 23.1 ms and 8 to 52 ms.
AT-4: PASS
AT-5: FAIL The Observation gives the turns as 168-1152 ms and 1415-2402 ms, but output.txt shows 173-1134 ms and 1420-2387 ms.
AT-6: PASS
AT-7: PASS
AT-8: PASS
AT-9: FAIL The Then line asks for one status, but each aria snapshot at 2 s and 7 s holds two status nodes, `status "Grading the Trade"` and `status: Grading the trade`.
AT-10: PASS
AT-11: PASS
AT-12: FAIL The Then line says the lines of the favored side flash, but the flash shots light the mesh under both the Bo Girds row and the Teehee row, and the log gives one flash value with no side.
AT-13: FAIL The Then line says the mesh does not move in the wait, but output.txt shows the wait canvas pixels change between 1 s and 3 s at each width, with 34026 px at 375 light.
AT-14: PASS
AT-15: FAIL The Then line allows no frame over 50 ms, but output.txt and frames-375-4x-run2.txt show a frame of 66.6 ms.
AT-16: PASS
AT-17: FAIL The Then line allows no dark box, but output.txt and the shots show filled dark boxes behind hero text on the manager page, the midseason opener, and the 404 page.
AT-18: PASS
AT-19: PASS
AT-20: FAIL The Observation says the cpc row labels read 16.50:1 or more, but output.txt shows Bo Girds at 14.09:1 in the 1280 dark wait and 15.13:1 at idle.
AT-21: PASS
AT-22: PASS
AT-23: PASS
AT-24: PASS
AT-25: PASS
AT-26: PASS
AT-27: PASS
AT-28: PASS
AT-29: FAIL The Then line asks for all headshots within 1 s, but output.txt shows the last token at rest 1324 ms after the tap at 375 light.
AT-30: PASS
AT-31: PASS
AT-32: PASS
AT-33: PASS
AT-34: PASS
