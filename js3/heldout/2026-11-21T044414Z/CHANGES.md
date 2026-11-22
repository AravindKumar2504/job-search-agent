# Changes to this held-out kit

## 2026-11-22: cards rebuilt, before any verdict

The audit (`js3/audit/2026-11-21T044414Z/AFTER-REVEAL.md`) found that the filter's sentence splitter cuts a line at
"U.S.", which hid "U.S. Person Required" from audit card 17. `tools/audit_kit.py` now keeps "U.S.", "e.g." and "i.e."
inside their lines on cards and shows every line R5's phrases match. CARDS.md here was rebuilt with the same seed: the
sample, the card order and `sealed/answers.json` are byte for byte the same (SHA-256 in README.md, which the rebuild
also reproduces unchanged). Six cards changed, all in their status lines: card 11 had shown none and now shows its
U.S.-citizen requirement; cards 03, 07, 10, 22 and 29 now show whole sentences where the old cards had cut them at
"U.S.". No verdict existed yet: VERDICTS.md was still blank.
