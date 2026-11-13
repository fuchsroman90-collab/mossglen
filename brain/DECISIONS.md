# Entscheidungen

Neueste oben. Format: Datum – Entscheidung – Begründung – wer.

- **2026-11-13 – Grafik als Blender-Pre-Render statt SVG.** Roman fand den SVG-Stil enttäuschend und
  wollte 3D-Tiere wie in Hay Day. Blender (bpy) ist kostenlos, läuft headless, und vorgerenderte Sprites
  kosten auf dem iPhone 11 nicht mehr als die alten SVG-Sprites. – Roman + Claude
- **2026-11-13 – Welt in 2x-Auflösung (Kachel 256 × 128).** Scharf beim Heranzoomen und auf
  hochauflösenden Handys, Mipmaps für das Herauszoomen. – Claude
- **2026-11-13 – Boden als Shader mit Zellen-Maske statt Kachel-Sprites.** Wege und Gehege bekommen weiche,
  natürliche Ränder wie in den Referenzen; ein einziger Draw Call. – Claude
- **2026-11-13 – Gebäude-Sockel kommt aus dem Boden-Shader**, nicht aus dem Sprite (ein Brett-Sockel sah
  unnatürlich aus). – Claude
- **2026-11-13 – CI rendert keine Grafik.** Blender ist für CI zu schwer; generierte Assets werden committed. – Claude
- **2026-11-13 – Referenzbilder nicht ins öffentliche Repo** (Urheberrecht Supercell), nur die Auswertung. – Claude
- **2026-11-13 – Brain im Repo** (`CLAUDE.md`, `brain/`, `.claude/skills/`), damit Laptop und PC dasselbe Wissen haben. – Roman
- **2026-11-13 – Figma vorerst nicht nötig.** Für Tiere/Gebäude hilft es nicht; für UI später, wenn Roman
  ein Layout oder Kit in Figma hat. Connector kann über claude.ai verbunden werden. – Claude
- **Früher (siehe GOAL.md Abschnitt 0 und 14):** Free-to-play, Zielgruppe alle, Budget 0 €, iPhone 11 als
  Referenz, öffentliches GitHub-Repo, Launch zuerst itch.io + APK.
