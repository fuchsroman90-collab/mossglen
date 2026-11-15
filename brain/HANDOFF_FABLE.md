# Auftrag an Claude Fable 5.2: Mossglen auf Referenz-Niveau bringen

Du übernimmst Mossglen, Romans cozy Farm-Spiel (Godot 4.7.2, Windows/Android/iOS). Repo:
`fuchsroman90-collab/mossglen`, Branch `main`. Sprich mit Roman **Deutsch**, Code und Kommentare auf Englisch.

## Ziel

Das Spiel soll im Spiel-Screenshot **genauso hochwertig aussehen wie die Referenzbilder**: dieselbe Qualität,
dieselbe Bildsprache und Lesbarkeit, dieselbe Art von UI. Roman hat mehrfach gesagt, dass die aktuelle UI
„schrecklich“ aussieht, dass Bereiche nicht unterscheidbar sind und dass alles „wie aus einem Guss“ wirken muss.
Du setzt das um: UI komplett neu, Grafik verbessern, Terrain verbessern, bis nichts mehr neben den Referenzen abfällt.

**Wichtig – rechtliche Grenze, nicht verhandelbar:** Die Referenzen sind Screenshots von Hay Day. Hay Day ist
**Qualitäts- und Stilmaßstab, keine Vorlage**. Übernimm keine Hay-Day-Grafiken, -Namen, -Figuren, -Logos oder
pixelgenaue Layouts. Baue eigene Assets, die auf demselben Niveau sind und sich genauso anfühlen.

## Zuerst lesen (Pflicht, in dieser Reihenfolge)

1. `CLAUDE.md` – Regeln des Projekts und das Brain-System.
2. `brain/GOAL.md` – Plan, Meilensteine, Status (Abschnitt 14b „M9.5 Hay-Day-Qualität“ ist dein Auftrag).
3. `brain/taste/LIKES.md` und `brain/taste/DISLIKES.md` – **jede Zeile**. Roman hat hier sehr genau gesagt, was er
   will und was nicht. Bilder dazu in `brain/taste/` und `brain/taste/rejected/`.
4. `brain/DECISIONS.md`, `brain/LOG.md` (neueste Einträge oben).
5. `brain/references/REFERENCES.md` – Auswertung jedes Referenzbilds.
6. **Alle Bilder in `brain/references/img/`** – jedes einzeln ansehen. Diese Bilder sind aus Urheberrechtsgründen
   **nicht im Git**. Wenn der Ordner bei dir leer ist, bitte Roman, sie dir hochzuladen, bevor du mit Grafik/UI
   anfängst. Ohne die Bilder nicht raten.
7. Skills: `.claude/skills/mossglen-art/SKILL.md` (Blender-Pipeline) und `.claude/skills/mossglen-dev/SKILL.md`
   (Bauen, Testen, Screenshots, CI).

## Was Roman schon freigegeben hat (Maßstab, nicht wieder kaputt machen)

- Welt in 3D (Blender-Pre-Render), UI in 2D.
- Huhn, Kuh und Schaf (`brain/taste/hen_approved.png`, `cow_approved.png`, `sheep_approved.png`): Cartoon-Stil,
  Körper **aus einem Guss**, Anbauteile per Raycast auf der Oberfläche, Kontrastlicht für Figuren.
- Item-Icons als 3D-Renders (`tools/art/blender/assets/items.py`), große weiße Zahl mit Kontur, **keine runden
  Rahmen**, eckige weiche Felder.
- XP-Leiste hängt an der rechten Spitze des Sterns.
- Lager: Ausbauen und Verkaufen in klar getrennten Rahmen.

## Was du umsetzen musst

### 1. UI komplett neu (höchste Priorität)
- Festes Raster und gemessene Abstände; jedes Fenster sauber zentriert, nichts „offset“.
- **Differenzierung**: jede Funktion hat einen eigenen, klar abgegrenzten Bereich mit eigener Rahmenfarbe
  (z. B. Ausbauen ≠ Verkaufen ≠ Information). Niemand darf Aktionen verwechseln.
- HUD nach `hd_ui_redesign_hud.png`: Stern + XP, Münzen/Smaragde als Kapseln, Shop-Knopf rechts unten.
- Shop als **waagrechte Karten unten** mit Reitern oben (Romans Wahl), gesperrte Karten grau mit Schloss.
- Ausbau-Dialoge nach `hd_upgrade_dialog.png`: senkrechte Liste, 3D-Material-Icon, große Zahl „x/y“, grüner Haken,
  runder gelber Bestätigen-Knopf.
- Dialoge mit Figur + Sprechblase + großen Antwortknöpfen (`hd_dialogs_wheel.png`), Pop-ups nach `hd_popups.png`,
  Ladebildschirm nach `hd_loading_shop_vertical.png`.
- Figma-Connector ist verbunden: Lege die neuen Layouts zuerst in Figma an und zeig sie Roman, bevor du sie baust.
- Ein Bildschirm nach dem anderen: bauen, Screenshot neben die Referenz legen, Roman zeigen, erst nach seinem OK weiter.

### 2. Grafik
- Restliche Tiere (Schwein, 10 Dinos, Haustiere) im freigegebenen Stil – **eins nach dem anderen**, jedes mit
  Vergleichsbild neben der Referenz, erst nach Romans OK alle Animationsframes rendern.
- Terrain nach `hd_winter_farm.png`: Gras mit Halmen, hellere Flecken, Grasbüschel, Ränder, Felsen.
- Gebäude im Bau mit Baustellen-Look (gibt es als Grundversion: `site_big`/`site_small`).

### 3. Offene Spielwünsche aus `brain/GOAL.md` 14b
Besucher-Händler, Haustiere, Glücksrad, Helfer.

## Arbeitsweise (Pflicht)

- **Geschmack schlägt Annahme.** Vor jeder Grafik-/UI-Arbeit `brain/taste/*` lesen.
- Jede Bewertung durch Roman **sofort** ins Brain (LIKES/DISLIKES mit Zitat und Bild).
- Immer selbst rendern und ansehen; Screenshots mit `--time=0.5`. Ein Asset ist erst fertig, wenn es im
  Spiel-Screenshot neben der Referenz nicht abfällt.
- Nach jedem fertigen Schritt: Smoke-Test (`godot --headless --path game -- --smoke`), Brain-LOG, Commit, Push,
  CI prüfen (`gh run list -R fuchsroman90-collab/mossglen`).
- Öffentliches Repo: keine Geheimnisse und keine Referenzbilder committen.
- Nicht blind iterieren: Wenn Roman etwas zweimal ablehnt, lege die Referenz daneben und frag konkret nach.
