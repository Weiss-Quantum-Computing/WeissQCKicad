# Circuit design review brief

You are reviewing KiCad circuit designs from an atomic-physics / quantum-computing research lab. The lab's experiment is run by a timing program called "supertime" that drives National Instruments cards (PCI-6713 and PCI-6733 analog output, PCI-6534 digital pattern I/O). Other boards are analog support electronics: coil drivers (often around the OPA549 power op amp), summing amplifiers, laser intensity-lock servos, filters, magnetic-field noise cancellation.

The owner wants, for every circuit: (1) a short plain-English description a future lab member can read to know what they are looking at, (2) a list of design problems with recommended fixes, especially anything that "could trip us up in a big way", and (3) a table of parts whose values are missing or generic in the schematic so they can be filled in later.

## Rules

- READ-ONLY. Never modify anything under ~. Work only from the copies and generated files in the scratchpad paths given below. You may write new files only inside the scratchpad `out/` and `work/` folders.
- Do not use the web unless you need a datasheet fact (pinout, absolute max, stability condition) that you are not sure of. If you look one up, say so in the evidence.
- Do not guess. Every issue needs evidence you actually saw: net names, reference designators, pin numbers, values. If you are unsure, still report it but mark confidence "low" and say what would confirm it.
- Trace the real connectivity from the `*.nets.txt` file (it is generated from the schematic by kicad-cli and is authoritative), not from how the schematic PDF looks.
- ERC and DRC reports are noisy in these projects (missing power flags, library mismatches, courtyard overlaps). Triage them: only report the ones that indicate a real electrical or manufacturing problem (unconnected pins that matter, shorts, unrouted nets, schematic/board mismatch, clearance on power nets). Summarise the rest in one "note" issue with counts.
- Some schematics are unfinished, experiments, or superseded versions. Say so in `status` rather than listing every loose end as a defect. For a family of versions, review the newest/most complete one in depth and for older ones give a description, status, and only differences or issues that still matter.

## Inputs (all under the scratchpad root given in your task)

- `src/<project>/` — copy of the project: `.kicad_sch`, `.kicad_pcb`, `.kicad_pro`, sometimes `.net`, `.csv`, `.pdf`, legacy `.sch`.
- `prep/<project>/<name>.nets.txt` — component list (ref | value | footprint | lib part) and every net with its pins as `REF.pin[pin name|pin type]`.
- `prep/<project>/<name>.erc.rpt` — KiCad 9 electrical rules check.
- `prep/<project>/<name>.sch.pdf` — schematic plot. Read it with the Read tool (it renders the page as an image) to see the designer's intent, text notes, and layout.
- `prep/<project>/<name>.pcb.txt` — board summary: layers, outline size, every footprint with pad→net mapping and pad geometry, track widths per net, vias, zones, silkscreen text. Only exists if there is a real board.
- `prep/<project>/<name>.drc.rpt` — KiCad 9 design rules check with schematic parity.
- `prep/<project>/<name>.top.png` — 3D render of the top of the board.
- `src/LTspice/*.asc` — LTspice simulations, some matching these circuits by name.
- kicad-cli is at `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli` if you need another export; write its output only into the scratchpad `work/` folder.

## What to look for

Work out what the circuit is for first, then check it against that purpose. Typical problems worth finding:

- Wiring that does not do what the designer evidently intended: swapped op-amp inputs (positive feedback), wrong pin numbers versus the real part's datasheet pinout, outputs shorted together, floating inputs (CMOS logic inputs, op-amp inputs with no DC path), enables/resets with no pull resistor, nets that connect to only one pin.
- Things that can damage hardware: no input protection on connectors that go to other equipment, no current limiting, reverse-polarity or power-sequencing hazards, parts run beyond voltage/current/power ratings, power op amps (OPA549 etc.) without thermal or current-limit provision, inductive loads without flyback/snubber, missing supply decoupling.
- Stability and analog performance: op amps driving capacitive loads or long cables directly, missing feedback capacitors on integrators/transimpedance stages, gain/bandwidth obviously inconsistent with purpose, filters whose component values do not give the frequency in the title, ground/return current paths on the board (signal return sharing a path with coil current), thin traces on high-current nets.
- Digital timing: ripple-clocked cascades, glitches on combinational outputs used as clocks/triggers, logic-family level mismatches (74HC needs 3.5 V high at 5 V supply; TTL sources may not reach it), unterminated fast edges into cables.
- Build problems: footprint that does not match the likely package, mirrored connector footprints (PinSocket vs PinHeader), pin-1 orientation, parts with no value (plain "R", "C", "D"), DNP ambiguity, mounting, connector pinouts that are not documented on silkscreen.

Severity scale:
- `critical` — can damage hardware, or the circuit cannot work as drawn.
- `major` — likely to malfunction or mislead in normal use; the kind of thing that costs days.
- `minor` — real but low impact, or easy workaround.
- `note` — documentation gaps, cosmetic, things to be aware of.

## Output

Write ONE JSON file to the output path given in your task, UTF-8, valid JSON (validate it with `python3 -I -c "import json,sys; json.load(open(sys.argv[1]))" <file>` before you finish). Plain text only inside strings: no markdown, no HTML. Use Ω, µ, etc. directly. Schema:

```
{
  "group": "<group name>",
  "circuits": [
    {
      "id": "<short-kebab-case-id, unique>",
      "name": "<human name>",
      "folder": "<folder name relative to the KiCAD directory, as given in src/>",
      "files": ["<main schematic/board file names reviewed>"],
      "last_modified": "<YYYY-MM-DD of newest design file if you can tell, else ''>",
      "status": "<one of: 'built board' | 'board laid out' | 'schematic only' | 'unfinished' | 'superseded' | 'empty'> ",
      "status_note": "<one sentence: why you chose that status, and which version supersedes it if any>",
      "description": "<3-6 plain sentences for a future lab member: what it does, what goes in and comes out, supply rails, the key ICs, and how the signal flows. No jargon you would not say out loud.>",
      "description_confidence": "high|medium|low",
      "issues": [
        {
          "severity": "critical|major|minor|note",
          "title": "<under 70 characters, states the problem>",
          "detail": "<2-4 sentences: what is wrong and what happens because of it>",
          "evidence": "<the refs/pins/nets/values you saw, e.g. 'U3.2 (IN-) and U3.6 (OUT) both on net /FB; R7 = 10k'>",
          "fix": "<1-3 sentences: the recommended change>",
          "confidence": "high|medium|low"
        }
      ],
      "unknown_parts": [
        {
          "refs": "<e.g. R1-R16>",
          "kind": "resistor|capacitor|diode|inductor|ic|connector|other",
          "schematic_value": "<what the schematic says, e.g. 'R' or '' or '?'>",
          "role": "<what the part does in the circuit, one phrase>",
          "suggested": "<a sensible value or part if one follows from the design, else ''>"
        }
      ],
      "open_questions": ["<things only the owner can answer that affect whether an issue is real>"]
    }
  ]
}
```

Order issues most severe first. Prefer a few well-evidenced issues over a long list of speculative ones; a typical board yields 3-10. `unknown_parts` is only for parts whose value/part number is genuinely missing or generic in the schematic (group identical ones by ref range).

When done, reply with a summary under 150 words: how many circuits, the count of critical/major issues, and the one or two most important findings. Do not paste the JSON into your reply.
