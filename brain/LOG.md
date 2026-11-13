# Arbeitslog

Neueste oben. Jede Sitzung: Datum, Rechner, was gemacht, was offen.

## 2026-11-13 – Abend: Romans erster Test → M9.5 begonnen (Progression)

- Romans Feedback komplett ins Brain (DISLIKES, DECISIONS, 11 neue Referenzen, `rejected/m9_dinos_pen.png`).
- Herbstfarben-Flackern behoben (Zufall pro Pflanze im Blau-Kanal von self_modulate statt Positions-Hash).
- **Progression neu** (`farm.gd`, `land_ui.gd`, Spielstand-Version 2 → alte Stände starten neu):
  - Starthof: Bauernhaus, Scheune, Silo, Auftragstafel + Lieferwagen, 3 Felder; Startfläche = 4 von 25 Parzellen.
  - Parzellen-Raster (`Farm.COLS/ROWS`), gesperrtes Land im Boden-Shader abgedunkelt (`land_tex`),
    Verkaufsschild nur an Parzellen, die an eigenes Land grenzen. Kauf mit Grenzpflock, Landkarte, Maßband + Münzen.
  - Hindernisse (Bäume, Tannen, Steine, Büsche) auf allem Land, deterministisch; Axt/Säge/Dynamit/Schaufel.
  - Werkzeuge + Ausbau-Material als Funde (`Game.roll_find`): Ernte 5 %, Hindernis 30 %, Lieferwagen 35 %.
  - Silo (Feldfrüchte) und Scheune (Rest) getrennt, je 50 + 25 pro Ausbaustufe, Ausbau mit eigenen Materialien.
    Silo-Sprite zeigt Füllstand (4 Stufen).
  - Gebäude und Gehege kauft man im neuen Karten-Shop (Reiter Felder/Gebäude/Tiere, Karten unten), platziert sie
    (Grundriss grün/rot), dann **Baustelle** mit Bauzeit, Antippen enthüllt. Gehege mit 1 Tier, weitere im Shop.
  - **Lieferwagen**: Abgabe lädt Münzen+XP auf den Wagen, er fährt die Dorfstraße hoch, kommt nach 45 s mit
    Münzkiste zurück; Tafel bis dahin gesperrt; Antippen kassiert.
  - Aufträge nur noch für Waren, die der Hof wirklich herstellen kann.
  - Dino-Weide ins Urzeit-Tal verlegt.
  - Anleitung neu für den leeren Hof (7 Schritte: säen, Baum fällen, ernten, Hühnerstall, liefern, kassieren, Brumm).
- Neue 3D-Assets (`assets/progress.py`): Bauernhaus, Silo 0–3, Lieferwagen (3 Richtungen), Münzkiste,
  Baustelle groß/klein, Land-Schild. 2D-Icons für Werkzeuge/Material (werden noch 3D, s. u.).
- Roman: **Item-Icons müssen 3D-gerendert sein** (`hd_item_icons_3d.png`), Ausbau-Dialog-Vorbild `hd_upgrade_dialog.png`.
- Figma-Connector ist verbunden.
- **3D-Item-Icons**: `tools/art/blender/assets/items.py` (59 Modelle: Feldfrüchte, Waren, Futter, Eier,
  Werkzeuge, Material), Frames `uiitem_<id>` werden nicht in den Atlas gepackt, sondern von
  `build.export_item_icons()` mit Kontur als `ui/item_<id>.png` (112 px) geschrieben – überschreiben die 2D-Icons.
  Lager-Raster nach Referenz: kein Kästchen, große Zahl mit Kontur über der Ecke.
- Item-Felder eckig statt rund (Roman): `slot.png` = weiches abgerundetes Quadrat ohne dunkle Kontur,
  `slot_selected.png` gelb für die Auswahl – gilt überall, wo Slots benutzt werden.
- Tiere Durchgang 1: Augen mit Oberlid (Hautfarbe, „droop“), zwei Glanzpunkte, größere Pupille; Schwein mit
  großem Rüssel, Mund, Schlappohren, kräftigen Beinen mit Hufen; Schaf mit dickeren Beinen, Hufen, größeren
  Ohren. Gilt für alle Tiere/Dinos/NPCs über `eye()`. Vollständige Neumodellierung folgt (Aufgabe M9.5d).
- M9.5c Bedienung: Hover am PC (aufhellen, kleiner Hüpfer, Hand-Cursor) für alles Antippbare, Druck-Feedback
  beim Drücken, **Saat aus dem Saat-Kreis gedrückt halten und über Felder ziehen** (Hay-Day-Art), Saat-/Sichel-
  Symbol folgt dem Finger beim Säen/Ernten, Blasen über Tieren stehen ruhig (kein Wippen mehr).

## 2026-11-13 – PC-Sitzung: M9 Teil 1 (Jahreszeiten, Erfolge, Musik, Einstellungen, Anleitung, VRAM)

- Jahreszeiten (`Game.season()`, echter Kalender, `--season=` zum Testen): Boden-Shader `season_tint` + `snow`
  (große weiche Schneeverwehungen, Wege bleiben frei), Sway-Shader färbt nur grüne Pixel von Bäumen/Büschen
  (Herbst je Pflanze orange/rot/gold, Winter Schnee oben). `weather.gd`: Blüten, Blätter, Schnee, Glühwürmchen.
  Saisonpflanze wächst 20 % schneller (`crops.json` → `season`). Saison-Plakette rechts oben (antippen = Info).
- Erfolge: `data/achievements.json` (12 Stück, 3 Stufen), Zähler in `Game.stats` über `Game.event()` +
  Münzen + Schlüpfen, Fenster mit Medaillen, Fortschrittsbalken und Abholen-Knopf.
- Musik: `tools/audio/songs.py` (Nacht B-Dur 64 BPM, Dorf G-Dur 100 BPM, Urzeit-Tal D-dorisch 76 BPM),
  alle Loops als Ogg (Wiese 8 MB WAV → 0,7 MB). `Audio.set_area()` blendet nach 2,5 s Verweilen über.
  Neuer Sound `achieve`.
- Einstellungen als eigenes Fenster (`meta_ui.gd`) mit Schaltern; Anzeigegröße skaliert die ganze HUD.
- Anleitung `tutorial.gd` (nur neue Spielstände, alte Spielstände überspringen sie; neu startbar).
- Atlas: VRAM-Kompression + Mipmaps über `pack.py`, Tipp-Masken `atlas_N_mask.png` (1/4, als Image importiert).
- Smoke-Test prüft Jahreszeiten, Erfolge, Einstellungen, Anleitung, Musikwechsel.
- Erster Winter-Versuch: Schnee fast überall, wirkte blau/flach (Screenshot lief bei Abendlicht) → weiche
  Verwehungen mit Gras dazwischen. Screenshots immer mit `--time=0.5` beurteilen.

Teil 2 (gleicher Abend):
- Saisonfeste `data/events.json` + `Game.festival_*` (Schlüssel z. B. `autumn_2026`), Fenster über die
  Saison-Plakette, roter Punkt wenn Stufe abholbar. `--ui=fest` für Screenshots.
- Balancing per Python-Auswertung der Daten (Mehrwert/Minute je Rezept): Preise für Kuhfutter, Schweinefutter,
  Milch, Butter, Käse, Karottenkuchen, Stoff, Schal, Kerze, Festkerze, Tomatensoße, Erdbeermarmelade angehoben.
  `xp_needed = 10 + 6·L + 1,5·L²`.
- Stolperfalle: `%` in Übersetzungen, die mit `%` formatiert werden, muss `%%` sein.

Offen: M6 (wartet auf Romans Supabase-Entscheidung), iPhone-FPS-Test.

## 2026-11-13 – PC-Sitzung: M4 Dinos + M5 Dorf und Story

M4:
- 10 Dino-Arten aus einem Grundmodell + Zubehör (Kragen/Hörner, Platten, Keulenschwanz, Kamm, Segel, Kuppel,
  Stacheln, Federn, Riesenhals): Moosaurus, Trikeri, Stegolino, Ankyknubbel, Parasauri, Segelrücken, Pachyköpfchen,
  Stachelchen, Flauschi, Brontobeere (`data/dinos.json`, Seltenheit 1–4).
- Urzeit-Tal jenseits des Bachs (Brücke, Moos-Boden über Blau-Kanal der Boden-Maske, Riesenfarne, Palmfarne),
  6 Grabungshügel (voll/leer, füllen sich nach 3 Min.), Funde: Fossil, Bernstein, Dino-Eier. Ab Level 4.
- Brutnest = Produktionsgebäude mit `"spawn": true` → Baby-Dino zieht auf die Dino-Wiese (max. 8).
- Dinos fressen Farn (neue Feldpflanze, Lv 4) und legen Urzeit-Eier → Riesen-Pfannkuchen; Bernstein → Bernsteinkerze.
- Dino-Pedia (Knopf mit Fußabdruck), Icons sind die 3D-Idle-Frames aus dem Atlas.
- Farn-Wedel zuerst „Speichenrad“ → mehr, breitere Fiederblättchen.

M5:
- Moosdorf im Norden am Meer: Strand, Dorfplatz mit Brunnen, 5 Gebäude als Ruinen (Leuchtturm, Museum, Markt,
  Café, Bibliothek) → Wiederaufbau mit Waren + Münzen. Funktionen: Leuchtturm = Meeresangeln am Strandsteg,
  Museum = Fossilien spenden + Sammlungsstand, Markt = 3 Wunschwaren/Tag mit +50 %, Café = 7. Auftrag,
  Bibliothek = Tagebuch der Geschichte.
- 4 Bewohner als Tier-Leute (Bär Brumm, Otterin Lotte, Wüstenfüchsin Dr. Fenna, Maus Pip), Idle + Winken,
  „!“ wenn sie etwas zu sagen haben.
- Story-Bogen 1 „Das Moosental erwacht“: 10 Quests (`data/story.json`), Dialoge DE/EN mit Schreibmaschinen-Text,
  Quest-Anzeige links (antippen = Gespräch), Belohnungen inkl. Smaragde, Finale = Café-Fest.
- Atlas jetzt 7 Seiten (2048²). Für Mobil später VRAM-Kompression prüfen (Textur-Budget iPhone 11).

Offen: M6 Backend braucht Romans Entscheidung (Supabase-Projekt anlegen, Konto/Region).

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
