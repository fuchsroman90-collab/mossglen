# Entscheidungen

Neueste oben. Format: Datum – Entscheidung – Begründung – wer.

- **2026-11-13 – Wünsche aus Romans erstem Test (Pflicht für den nächsten Meilenstein „M9.5 Hay-Day-Qualität“):** – Roman
  - Leerer Starthof, alles selbst bauen; Land in Stücken freischalten (Werkzeug sammeln).
  - Weizen: gedrückt halten und über mehrere Felder ziehen zum Säen/Ernten (wie Hay Day).
  - Hover- und Klick-Feedback für alles (Felder, Tiere, Gebäude, Knöpfe).
  - **Lieferwagen** an der Auftragstafel: fährt nach Abgabe weg, kommt mit Geld zurück, Geld per Klick
    einsammeln; solange er weg ist, keine neue Bestellung abgeben.
  - **Silo** (Feldfrüchte) mit sichtbarem Füllstand, **Scheune** (Werkzeuge + Waren); beide haben ein Maximum
    und müssen ausgebaut werden.
  - Werkzeuge zum Bäume fällen und Steine sprengen (Hindernisse auf dem Land).
  - Baustellen-Look für Gebäude im Bau.
  - Figma für die UI.
- **2026-11-13 – Jahreszeiten nach echtem Kalender** (Nordhalbkugel), nicht nach Spieltagen: fühlt sich an wie
  draußen, kein Grind. Jede Saison hat eine Bonus-Pflanze. – Claude
- **2026-11-13 – Musik als Ogg Vorbis**, Soundeffekte bleiben WAV (kurz, latenzfrei). – Claude
- **2026-11-13 – Atlas VRAM-komprimiert (BPTC Desktop, ASTC Handy).** ~4x weniger Grafikspeicher fürs
  iPhone 11; die APK wird dafür ~15 MB größer. Tipp-Erkennung über eigene Alpha-Masken. – Claude
- **2026-11-13 – Anleitung nur für neue Spielstände**, jederzeit in den Einstellungen neu startbar. – Claude

- **2026-11-13 – Welt 3D, UI 2D.** Spielwelt bleibt vorgerendertes 3D, die Benutzeroberfläche (HUD, Knöpfe,
  Icons, Menüs) wird flach in 2D gezeichnet (SVG aus Code), angelehnt an das Referenz-HUD. – Roman

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
