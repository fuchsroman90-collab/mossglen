# Mossglen – Stil-Bibel (Version 2, 3D-Pre-Render)

Verbindlich für alle Grafiken. Seit 13.11.2026 ersetzt diese Fassung den flachen SVG-Stil,
den Roman abgelehnt hat (`brain/taste/rejected/m0_svg_atlas.png`).
Maßstab sind die Referenzen in `brain/references/` (Hay-Day-Qualität, eigene Welt).
Technik und Regeln zum Bauen: Skill `.claude/skills/mossglen-art/SKILL.md`.

## 1. Gefühl

- **Warm, satt, verspielt.** Sommernachmittag, alles ist rund und freundlich.
- **Echtes Volumen.** Alles ist ein 3D-Modell, weich beleuchtet, vorgerendert.
- **Moos als Erkennungszeichen** auf Dächern, Steinen, Zaunpfosten.
- Keine harten Schwarztöne, keine grauen Schatten. Schatten sind farbig (grün/blau).

## 2. Perspektive

- Orthografische Kamera, 30° Höhe, 45° gedreht: Kachel = Raute **256 × 128 px** (2x).
- 1 Kachel = 1 m. Huhn ≈ 0,5 m, Baby-Dino ≈ 0,9 m, Laubbaum ≈ 2,3 m, Scheune 3 × 3 Kacheln.
- Ankerpunkt jedes Sprites = Bodenkontakt (Ursprung des Modells).

## 3. Licht und Material

- Sonne von **oben links vorne**, warm (leicht gelblich), weiche Schatten (14° Sonnenwinkel).
- Himmel als kühles Fülllicht von oben, grünes Rücklicht vom Gras von unten.
- Materialien leicht glänzend, Silhouette dunkelt zur Eigenfarbe ab („edge“).
- **Kontur:** 2 px, abgedunkelte Eigenfarbe, nie Schwarz. Icons 2,5 px.
- Bodenschatten: weich, Farbe #243A12 mit 55 % (statische Objekte gebacken, Tiere Blob-Schatten).

## 4. Farben (Richtwerte)

| Bereich | Farben |
|---|---|
| Gras | #8FC63E Basis, #A6D64B hell, #74AE34 dunkel, Halm-Tupfer |
| Erde/Wege | #DDB87A Basis, Kiesel hell #F0DCB2 |
| Laub | #93CF3C hell → #2C7A2C dunkel, Herbst #FFC84A → #D9752A |
| Tanne | #6DBE6A → #1F6A44 |
| Scheune | Rot #D2493A, Zierleisten #FFF4E2, Schiefer #5B7184 |
| Holz | #B07547 / #9C6539 |
| Weizen reif | #F2C443, Halme #E3B23C |
| Akzente | Gold #FFC93C, Smaragd #2FD487, Apfel #E83B3B |

## 5. Formen

- Gebäude gedrungen, Dachüberstand groß, alle Kanten mit Bevel. Details als echte Einzelteile
  (Bretter, Schindeln, Steine, Fensterkästen), jedes mit leichter Farbstreuung.
- Gebäude stehen auf einer Erd-/Pflasterfläche (vom Boden-Shader gemalt) mit Kleinkram daneben.
- Tiere und Dinos: Chibi, großer Kopf, große Augen mit Glanzpunkt, die zur Kamera schauen,
  kurze Beine, wenige klare Farbflächen. Dinos haben Moos-Flecken und rosa Wangen.
- Pflanzen in Büscheln, Bäume aus vielen Laub-Ballen.

## 6. Animation

- Tiere: Idle (Atmen + Blinzeln), Laufen, Huhn zusätzlich Picken. Blickrichtungen se/ne, gespiegelt sw/nw.
- Wind-Shader für Bäume, Büsche, Pflanzen. Squash & Stretch bei jeder Interaktion.

## 7. UI (2D, seit 13.11.2026)

Roman will die UI **flach in 2D** und nah am Referenz-HUD. Die Welt bleibt 3D.
- Gezeichnet als SVG aus Code (`tools/art/ui.py`, gerendert mit resvg in 2x).
- Formen: kräftige vertikale Verläufe, **weißer Innenrand**, dicke warm-dunkle Kontur (#5A3410),
  Glanz-Ellipse oben, kleiner Schlagschatten.
- Aufbau: blauer Level-Stern links oben über der XP-Leiste (weißer Rand, dunkelblau innen, hellblaue Füllung),
  große weiße Zahlen mit dicker Kontur + Münze/Smaragd + gelber Plus-Knopf rechts oben,
  runde gelbe Knöpfe links (Einstellungen), großer Shop-Knopf links unten.
- Schrift **Fredoka** SemiBold. Auf hellen Panels dunkelbraune Schrift ohne Kontur.
- Item-Icons in Menüs sind ebenfalls 2D (gleicher Stil).
