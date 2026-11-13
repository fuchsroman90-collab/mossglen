# Mossglen – Brain

Dieses Repo ist Romans cozy Farm-Spiel **Mossglen** (Godot 4.7.2, Windows/Android/iOS).
Diese Datei wird von jeder Claude-Code-Sitzung (Laptop und PC) automatisch geladen.
Sprache mit Roman: **Deutsch**. Code und Code-Kommentare: Englisch.

## Das Brain – Pflicht in jeder Sitzung

Alles Wissen über das Projekt liegt in `brain/`. Vor der Arbeit lesen, nach der Arbeit aktualisieren.

| Datei | Inhalt | Wann aktualisieren |
|---|---|---|
| `brain/GOAL.md` | Der Gesamtplan (Ziel, Systeme, Roadmap M0–M11, Status) | Wenn ein Meilenstein fertig ist oder eine Entscheidung den Plan ändert |
| `brain/LOG.md` | Was gemacht wurde, neueste Einträge oben | **Am Ende jeder Arbeitssitzung**, kurz und mit Datum |
| `brain/DECISIONS.md` | Entscheidungen mit Begründung | Sobald etwas entschieden ist |
| `brain/taste/LIKES.md` | Was Roman gefällt (mit Zitat/Anlass) | **Sofort**, wenn Roman etwas lobt |
| `brain/taste/DISLIKES.md` | Was Roman nicht gefällt | **Sofort**, wenn Roman etwas kritisiert |
| `brain/taste/rejected/` | Bilder von abgelehnten Ständen | Bei Ablehnung ein Bild ablegen |
| `brain/references/REFERENCES.md` | Auswertung der Referenzbilder | Wenn neue Referenzen kommen |
| `brain/references/img/` | Referenzbilder (nur lokal, **nicht im Git**, Urheberrecht) | – |

Regeln:
1. **Geschmack schlägt Annahme.** Vor jeder Grafik-/UI-Arbeit `brain/taste/*` und `brain/references/REFERENCES.md` lesen.
2. Roman sagt etwas über Look, Spielgefühl oder Arbeitsweise → sofort in LIKES/DISLIKES/DECISIONS eintragen, nicht erst am Ende.
3. Keine Hay-Day-Assets, -Namen oder -Figuren kopieren. Hay Day ist **Qualitäts- und Stilmaßstab**, nicht Vorlage.
4. Ein Asset ist erst fertig, wenn es im Spiel-Screenshot neben den Referenzen nicht abfällt. Immer selbst rendern und ansehen.

## Skills (`.claude/skills/`)

- `mossglen-art` – **Blender-Pre-Render-Pipeline** (3D-Modelle → Sprites → Atlas). Für jede Grafikarbeit laden.
- `mossglen-dev` – Godot-Projekt bauen, testen, Screenshots machen, CI.
- `vendor-blender-scripting` – allgemeine bpy-Referenz (Apache-2.0, TerminalSkills).
- `vendor-godot` – GdUnit4/Export-Referenz (MIT, Randroids Dojo).

## Kurzüberblick Technik

- `game/` Godot-Projekt. `tools/art/` Blender-Skripte (`python tools/art/build.py`), `tools/audio/` Musik/SFX.
- Welt-Einheiten: 1 Kachel = **256 × 128** (2x-Auflösung). Sprites sind in 2x gerendert.
- Selbsttests: `godot --headless --path game -- --smoke`, Screenshot: `--shot=pfad.png`, Benchmark: `--bench`.
- Öffentliches Repo: **keine Geheimnisse** committen (siehe `.gitignore`).
