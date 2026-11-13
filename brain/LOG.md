# Arbeitslog

Neueste oben. Jede Sitzung: Datum, Rechner, was gemacht, was offen.

## 2026-11-13 – PC-Sitzung: HUD auf 2D umgestellt

- Roman: „Die UI bitte in 2D und mehr an den Referenzbildern orientieren.“ → in taste/DISLIKES + DECISIONS.
- `tools/art/ui.py` neu: SVG aus Code (resvg): runder gelber/grüner Knopf, blauer Stern, Münze, Smaragd,
  XP-Leiste (9-Slice), Panel, Symbole Zahnrad/Note/Shop/Plus. Ausgabe nach `game/art/generated/ui/`.
- `hud.gd` neu im Referenz-Aufbau, Einstellungs-Panel (Musik, Sprache), Shop-Knopf (Signal `shop_pressed`).
- GitHub-Zugriff ist eingerichtet, Push klappt.

## 2026-11-13 – PC-Sitzung (Cloud, Opus 5.5): M0 neu mit 3D-Grafik + Brain

**Anlass:** Roman fand die SVG-Grafik enttäuschend (siehe `taste/DISLIKES.md`), schickte 14 Hay-Day-Referenzen
und wollte das Fundament komplett neu, mit Blender und einem „Brain“.

Gemacht:
- Brain angelegt: `CLAUDE.md`, `brain/` (GOAL = alter PLAN.md, LOG, DECISIONS, taste, references), Skills
  `mossglen-art`, `mossglen-dev`, dazu `vendor-blender-scripting` (Apache-2.0) und `vendor-godot` (MIT) von GitHub.
- Neue Grafik-Pipeline `tools/art/` mit Blender 5.3 (`pip install bpy`): Toolkit `blender/kit.py`
  (Kamera 2:1, Licht, Materialien mit Randabdunklung, Metaballs, `chain()`, Raycast-`Surface`),
  Assets in `blender/assets/` (animals, nature, farm, buildings, icons), Cache, Nachbearbeitung, Atlas-Packer.
- 104 Frames: Scheune (eigenes Design, Schieferdach mit Moos, Rundfenster, Fensterkästen), Feld, Weizen 0–3,
  Eiche ×2, Herbstbaum, Apfelbaum, Tanne ×2, Busch, Beerenbusch, Steine mit Moos ×2, Blumen ×4, Zäune,
  Heu, Fass, Kiste, Trog, Huhn (Idle 6, Laufen 8, Picken 6, je se/ne), Baby-Dino „Moosaurus“ (Idle 8, Laufen 8,
  je se/ne), Icons Münze/Smaragd/Stern/Weizen, Effekte.
- Godot: Welt in 2x (Kachel 256 × 128), Boden-Shader (Gras, Erde, weiche Ränder, Teich mit Wellen),
  `animal.gd` für Huhn und Dino, neues HUD (Level-Stern, XP-Leiste, Münz-/Smaragd-Kapseln, runde Knöpfe,
  Schrift Fredoka), XP/Level in `game_state.gd`, Mipmaps.
- Testfarm verdichtet: Teich, Blumenränder, Dino-Wiese, Hühnergehege mit Erdboden.
- CI rendert keine Grafik mehr (nur Prüfung, dass die Dateien da sind).
- `--smoke` grün. Screenshots (fern/nah) geprüft.

Lehren (stehen auch im Skill `mossglen-art`):
- Metaball-Ketten statt einzelner Kugeln, Details per Raycast auf die Oberfläche setzen.
- Laub über Relief (Bump), nicht über Farbflecken. Tannen als Stern-Etagen.
- Gebäude-Sockel kommt vom Boden-Shader.

Offen / nächste Schritte:
- Roman muss den neuen Look bewerten → Reaktion in `taste/` eintragen.
- Echte FPS auf iPhone 11 / Windows messen (hier nur Software-Rendering).
- CI-Lauf auf GitHub prüfen.
- Danach M1 (Vertical Slice): weitere Pflanzen (Karotte, Mais, Tomate, Erdbeere) im neuen Stil, Inventar, Bau-Modus.
- Laptop-Sitzung: alte SVG-Arbeit für M1 nicht weiterführen; vor Arbeit `git pull`.

## 2026-11-13 – Laptop-Sitzung: M0 erster Stand (SVG)

Godot-Projekt, SVG-Grafik-Pipeline, Audio-Pipeline, Testfarm, CI geschrieben. Grafik später verworfen.
