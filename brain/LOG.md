# Arbeitslog

Neueste oben. Jede Sitzung: Datum, Rechner, was gemacht, was offen.

## 2026-11-13 – PC-Sitzung: M3 Angeln

- 40 Fischarten (`game/data/fish.json`): 14 Teich, 14 Bach, 12 Meer (Meer kommt mit dem Dorf in M5).
  Bedingungen: Ort + Tageszeit (Tag/Dämmerung/Nacht), Seltenheit 1–4, Größenbereich, Preis.
- Fisch-Icons werden per Code erzeugt (`ui.fish_icon`: Körperlänge, Schwanztyp, Flossen, Farben, Muster).
- Minispiel `fishing_ui.gd`: Auswerfen → Biss → weißer Ring schrumpft auf goldenen Zielring, Tippen =
  Qualität (seltener/größer). Kein Scheitern: ohne Tippen gibt es trotzdem einen Fisch. Fangkarte mit
  NEU/REKORD, Verkaufen oder Freilassen (XP).
- Pro Angelplatz 5 Fische, +1 alle 90 s (gespeichert). Ruten: Holz, Bambus (Lv 4), Gold (Lv 8) im Laden.
- Bach am Ostrand (Wasser-Maske, mäandernd), zwei Stege (3D), gefangene Teichfische schwimmen als Schatten
  im Farmteich. Album (Buch-Knopf links) mit Rekordgrößen.

## 2026-11-13 – PC-Sitzung: M2b (M2 komplett)

Roman: „Mach weiter alles hintereinander.“ → Meilensteine nacheinander, nach jedem Push + Brain.
- 3D: Schaf (Wolle aus Laub-Ballen-Technik), Schwein (Trüffel statt Speck, cozy), Bienen-Korb (Skep) mit
  fliegenden Bienen (eigenes Sprite), Marmeladenküche, Webstuhl (offenes Pultdach, sonst verdeckt das Dach alles),
  Popcornwagen (offener Kessel; Glas rendert undurchsichtig weiß → vermeiden), Soßenküche, Kerzenzieherei.
- 15 neue 2D-Icons, Daten (Schaf-/Schweinefutter, 10 Rezepte), Lager 80 Plätze.
- Bienenstock = Produktion mit `"auto": true` (füllt sich selbst, Honig ohne Zutaten).
- Neue Sounds: Muh, Mäh, Grunzen, Platschen, Rolle, Level-Jingle, Graben.
- Schwebende Sprites (Mühlenflügel, Biene) ohne Bodenschatten (`NO_SHADOW` in render.py).
- Feste Apfelbaum-Positionen prüfen jetzt freie Felder (standen im Schweinegehege).

## 2026-11-13 – PC-Sitzung: XP-Leiste + M2a (Wirtschaftsschleife)

- Roman: XP-Leiste muss an der rechten Sternspitze hängen („in einem“) → `taste/LIKES.md`, Soll-Bild
  `taste/xp_bar_soll.png`. Umsetzung: fester Leistenrahmen `xp_frame.png` (kein 9-Slice), Position aus der Sternspitze.
- 3D neu: Kuh (Idle/Laufen/Fressen, se/ne), Futtermühle (+ drehende Flügel als eigenes Sprite), Bäckerei mit
  Kuppelofen (Rauch aus dem Schornstein), Molkerei, Auftragstafel.
  Korrekturen: Mühlendach-Schindeln standen stachelig ab → Ziegelringe; zwei Rundfenster wirkten wie ein Gesicht;
  Tafel zeigte die Rückseite; Kuh-Halsband stand ab.
- 2D-Icons: Hühner-/Kuhfutter, Ei, Milch, Brot, Maisbrot, Karottenkuchen, Sahne, Butter, Käse.
- Daten: `items.json`, `buildings.json` (Rezepte, Slots, Effekte), `animals.json`.
- Systeme: `production.gd` (Warteschlange auf Echtzeit, läuft offline weiter, Abholen per Antippen, Blase mit
  Produkt), Tiere füttern/abholen (ein Tipp bedient das ganze Gehege), Aufträge (6 Karten, Liefern, Verwerfen ohne
  Strafe, neuer Auftrag nach kurzer Wartezeit), alles im Spielstand gespeichert.
- HUD: Produktionsfenster (Warteschlange mit Fortschritt, Rezepte mit Zutaten habe/brauche), Auftragsfenster,
  Scheune zweispaltig bei vielen Waren.
- Selbsttest erweitert (Brot backen, Hühner füttern + Eier holen, Auftrag liefern, Speichern).

Offen für M2b: Schaf, Schwein (Trüffel statt Speck, cozy), Bienen; 5 weitere Gebäude (Marmeladenküche, Webstuhl,
Popcorn, Saucenküche, Honig/Kerzen). Danach M2 fertig.

## 2026-11-13 – PC-Sitzung: M1 Vertical Slice

- 4 neue Pflanzen in 3D (Mais, Karotte, Tomate, Erdbeere, je 4 Stufen). Karotte erst „Salat-Look“ → fedriges Kraut.
- 2D-Item-Icons (Weizen, Mais, Karotte, Tomate, Erdbeere, Feld) + Slot, Badge, Schloss, Pill-Knopf, Häkchen, Kreuz.
- Daten: `game/data/crops.json` (Wachstum 30 s–7 min, Verkaufspreis, XP, Freischalt-Level, Ertrag 2).
- `game_state.gd`: Lager (50 Plätze), Säen kostet 1 Stück, Ernte gibt 2, Verkauf, Level-Freischaltung mit
  Geschenk (2 Stück), Feldpreis/Max-Felder, **lokales Speichern** (`user://save.json`, Autosave 5 s, beim
  Schließen/Pausieren; Wachstum läuft offline weiter).
- HUD: Saat-Auswahl am Feld, Wachstums-Blase (Restzeit), Scheune mit Verkauf, Laden (Feld kaufen),
  Platzier-Leiste ✓/✗, Meldungen (Level-up, neue Pflanze, Scheune voll, keine Saat).
- Welt: Antippen = Saat-Auswahl, Wischen = säen/ernten, **langes Drücken = Feld verschieben**,
  gekaufte Felder per grün/rot-Vorschau platzieren, Scheune antippen = Lager. **Tag/Nacht** (20 Min, CanvasModulate).
- Selbsttest prüft den ganzen Ablauf (säen, reifen, ernten, verkaufen, Level-up, Feld kaufen, verschieben,
  Speichern). Screenshot-Schalter: `--ui=picker|barn|shop|place`, `--time=0..1`.
- Fehler gefunden: Godot schaltet `_process` automatisch ein → leere Felder suchten Sprite „_0“. Behoben.

Offen: Romans Bewertung von M1; echte Geräte-FPS; danach M2 (Tiere + Produktion + Aufträge).

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
