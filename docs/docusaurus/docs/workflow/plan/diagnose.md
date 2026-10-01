---
title: Diagnose
description: For a bug, agree on how to reproduce it, why it happens and what should happen instead.
---

![The Bug route with Diagnose highlighted](pathname:///img/diagrams/track-diagnose-light.svg)
![The Bug route with Diagnose highlighted](pathname:///img/diagrams/track-diagnose-dark.svg)

On the Bug route, diagnosis takes the place of research and design. The agent reproduces the bug and finds its cause before it plans a fix.

![Diagnosis: how to reproduce the bug, its root cause in the code, and the behaviour the fix must have](pathname:///img/diagrams/diagnose-light.svg)
![Diagnosis: how to reproduce the bug, its root cause in the code, and the behaviour the fix must have](pathname:///img/diagrams/diagnose-dark.svg)

## In the Cockpit

| Section | What it holds |
| --- | --- |
| Reproduction | The steps or input that make the bug happen |
| Symptom and root cause | What goes wrong, and the reason in the code |
| Behaviour contract | What should happen instead, edge cases included |
| Fix approach | Where the fix belongs and what it changes |
| Not doing | Related work left out on purpose |

`01-diagnosis.md` is for you; `01-diagnosis-details.md` holds the reproduction output and the investigation.

## You decide

Check that the reproduction matches what you saw and that the behaviour contract is the result you need. Then approve.

Next: [Outline](outline.md).
