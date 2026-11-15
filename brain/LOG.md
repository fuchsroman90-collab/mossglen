# Arbeitslog

Neueste oben. Jede Sitzung: Datum, Rechner, was gemacht, was offen.

## 2026-11-15 (spät) – Look-Pass Teil 2

- Pflanzen dichter und schlanker (Raster bis an die Zellkante, Mais 3×3 mit dünnen Stängeln, Karotte/Erdbeere 4×4,
  Tomate 3×3), Zäune dünner (Pfosten 0,06, Latten 0,03), Landschilder 0,72 skaliert, Wiese mit hellen Büscheln
  und Blümchen im Boden-Shader. Screenshot `--ui=wheatdemo --at=13,9`.
- Offen im Look: Gebäude-Kleinteile, Grasdecke der Mine, Deko verschlanken, UI v2 einbauen.

## 2026-11-15 (spät) – Look-Pass nach Romans Kritik

- Roman: Weizen wie Mais, Gesamtlook nicht stimmig, Boden „fett“, ich höre zu früh auf (DISLIKES).
- Umgesetzt (siehe DECISIONS „Look-Pass“): Boden-/Wegfarben, flache Äcker mit Furchen, Weizen als dünne Halme,
  Kamera weiter weg, Laubbäume kleiner. Alle 25 Pflanzen-Frames neu gerendert (wegen `FIELD_TOP`).
- Vergleichsbild oben Spiel / unten Referenz gebaut (`/tmp/cmp.png`, nicht im Repo).

## 2026-11-15 (abends) – Schwein v3.1

- Roman zu v3: „du hast mit deiner Einschätzung recht beim Schwein, änder das“ (Schwanz zu lang, Lächeln unsichtbar).
- Schwanz jetzt kurzer Kringel direkt am Po. Lächeln neu auf die Kopffläche gelegt – aus der Spielkamera weiterhin
  vom Rüssel verdeckt (offen). Roman fragte nach Drachen-/Dino-Eiern: Dino-Eier gibt es (Urzeit-Ei + 10 Arten-Eier,
  Brutnest), Drachen gibt es nicht.

## 2026-11-15 (abends) – Schwein v3

- Roman zu v2: „Das Schwein sieht schrecklich aus.“ → DISLIKES + `rejected/pig_v2_2026-11-15.png`.
- v3 komplett neu **auf dem Bauplan der freigegebenen Kuh**: gleicher Kettenkörper mit verschmolzenem Kopf, gleiche
  müde Augen, Blob-Beine (kürzer); Schwein-Teile: Tonnen-Rüssel mit dunkler Front, Dreieck-Ohren, Backen, Ringelschwanz.
  40 Frames gerendert. Wartet auf Romans Urteil.

## 2026-11-15 (abends) – Fable 5.2: Block 4 („ganzen Plan fertig“ – Teil)

- Roman: „mach alles fertig, ganzen Plan“. Der Plan ist zu groß für eine Sitzung; weiter Block für Block.
- **Schwein**: Rüsselscheibe saß in der NE-Ansicht daneben (Welt/Lokal vertauscht) → behoben; Beine höher angesetzt
  und kurz; Grinsen dicker. Alle 40 Frames neu gerendert. **Noch nicht von Roman freigegeben.**
- **Straßenstand**: `Game.stand` (4 Plätze), Preisstufen 0,8×/1,2×/1,8× mit Zeitfaktor 0,5/1/2,5, Fenster mit
  getrennten Rahmen (Theke oben, Auswahl unten), Modell `stall`. Screenshot `--ui=stand`.
- Preis-Abfrage für Besucher/Stand über `Game.price()` (Feldfrüchte stehen nicht in items.json).
- Offen aus dem Plan: UI v2 einbauen, Dinos + Haustiere im neuen Stil, Item-Blasen, Helfer, übrige Pflanzen
  dicht, Furchen, Felskante, Schmuck, Freunde/Supabase, iPhone-Test.

## 2026-11-15 (abends) – Fable 5.2: Block 3 „alles noch schöner“

- **Weizen reif** (`farm.py::_wheat_carpet`): 9×9 Halme bis an die Zellkante, dunkler Fuß, dicke helle Ähren →
  Felder wachsen zu einem goldenen Block zusammen (Zielbild `hd_style_harvest_corner`).
- **Schmelzofen** neu: rote Ziegelringe mit hellen Steinen, cremefarbener Bogen, blaues Kegeldach, Blasebalg, Kohlekiste.
- **Mine**: Fels aus kantigen Brocken in zwei Tönen. Grasdecke fehlt noch (sitzt im Fels, nicht sichtbar).
- Screenshot-Modus `--ui=wheatdemo` (Weizenblock + Mine + Deko bei Zelle 14,10; `--at=16,11.5 --zoom=0.8`).

## 2026-11-15 – Fable 5.2: Block 2 („komplett weitermachen“)

- **Schmelzofen** (Produktionsgebäude, Level 4, 700 Münzen): Erz + Kohle → Eisen-/Silber-/Gold-/Platinbarren, neue Icons.
- **Besucher**: erscheint ab Level 2 alle 5 Min neben der Auftragstafel mit Waren-Blase; Fenster mit Angebot,
  „Ja, bitte sehr!“ / „Heute leider nicht“. Zahlt 1,6× Lagerpreis. Figur vorerst `npc_pip_0`.
- **Gebäude/Gehege verschieben**: lange drücken → Geist mit Grundfläche → Haken. Umsetzung: Eintrag in
  `Game.placed` ändern, speichern, Szene neu laden (`Game.skip_intro`). Real getestet mit `--ui=movetest`.
- Smoke-Test deckt Besucher-Handel und Verschieben (ohne Reload) ab.

## 2026-11-15 – Fable 5.2: „alles jetzt machen“ – Block 1

- Roman: „okay los gehts alles jetzt machen“ → Bauliste `brain/FEATURES.md` wird der Reihe nach abgearbeitet.
- 12 weitere Deko-Modelle (Vogelscheuche, Bank, Laterne, Lattenzaun, Hecke, Wegweiser, Milchkannen, Laubhaufen,
  kahler Baum, Trittsteine, Holzstapel), Grasbüschel dünner. Deko gesamt: 37 Teile.
- `reward_ui.gd`: **Glücksrad** (8 Felder, gratis 1×/Tag), **tägliches Geschenk** (7-Tage-Reihe), **Mine**-Fenster.
- **Schatzkisten** erscheinen alle 4 Min auf freiem Land (max. 2), antippen gibt Münzen/Smaragd/Werkzeug.
- **Mine**: platzierbar (2×2), 4 Werkzeuge (1/2/3/5 Erz), 5 Erze als Lager-Waren, neue 3D-Icons.
- Smoke-Test deckt Kiste, Rad, Geschenk, Mine, Deko ab. Screenshot-Modi `--ui=wheel|daily|mine`.
- Nicht von Hand gespielt, nur Selbsttest + Screenshots. Offen: Bearbeiten-Modus, Item-Blasen, Schmelzofen,
  Schwein/Haustiere, Besucher-Händler, Straßenstand, UI v2 einbauen, Terrain-Grafik.

## 2026-11-15 – Fable 5.2: Deko-System (Bauliste A)

- 4 neue Zielbilder ausgewertet (REFERENCES.md), Feature-Analyse + Bauliste in `brain/FEATURES.md`.
- **Deko-System**: `decos.json` (24 Teile), Laden-Reiter „Deko“, Platzieren mehrfach hintereinander, Wege mit dem
  Finger malen/entfernen (Bodenmaske live), Deko antippen → Verschieben/Verkaufen (halber Preis), Spielstand
  speichert `decos`. Neue Modelle: `grass_tuft(_b)`, `pumpkin(_pile)`, `hay_bale(_stack)`.
- Screenshot-Modi `--ui=deco`, `--ui=decodemo`. Smoke-Test um Deko erweitert.
- Offen: Grasbüschel dünner modellieren; Romans Urteil zu UI v2 und zur Deko-Ecke.

## 2026-11-15 – Fable 5.2: UI v2 Layouts (Schritt 1, wartet auf Romans OK)

- Brain + alle 26 Referenzbilder gelesen. UI komplett neu entworfen, **noch nichts im Spiel geändert**.
- 7 Layouts 1600×900: 01 HUD, 02 Laden (Reiter oben, Karten unten), 03 Scheune (Inhalt / Verkaufen / Lagerplatz
  als drei getrennte Rahmen), 04 Ausbau-Dialog, 05 Besucher-Händler, 06 Neues Land, 07 Ladebildschirm.
- Figma: Datei „Mossglen UI v2“ (https://www.figma.com/design/zm0UwtMpk8NHiM1r1zMR8D), Seite „UI v2 Layouts“ –
  editierbare Rahmen mit Bild-Platzhaltern (Schrift Fredoka). Der HTML-Import nach Figma ging aus der
  Cloud-Umgebung nicht (403), daher per Plugin-API gebaut.
- Vorschau mit echten Spiel-Grafiken: `python3 tools/ui_mockup/build.py <welt.png> <out.html>` (Welt-Bild per
  `--shot=… --nohud`, neuer Schalter in `world.gd`).
- Offen: Romans Urteil zu den Layouts → dann Bildschirm für Bildschirm in Godot bauen.

## 2026-11-15
- Schaf freigegeben (aus einem Guss, Kapuze), alle Frames im Spiel. Schwein-Prototyp nach Referenz begonnen
  (ein Guss, Rüsselscheibe, Grinsen mit Zähnen, Spitzohren) – noch nicht gezeigt, **noch fehlerhaft**: Beine
  hängen unter dem Körper ab (Hüfte zu tief), Rüsselscheibe/Nasenlöcher schweben in der NE-Ansicht (place_on mit
  Weltnormale bei gedrehtem Root), Grinsen kaum sichtbar.
- Roman: Übergabe an Claude Fable 5.2 → Auftrag in `brain/HANDOFF_FABLE.md`.

- Schaf Prototyp 3 (Skin-Mesh) abgelehnt („noch schlimmer“). Prototyp 4 direkt am Referenz-Schaf aus
  `hd_animals_pets.png` ausgerichtet: cremefarbenes glattes Woll-Ei mit Locken-Relief, großer brauner Kopf nach
  vorn, große Augen, kurze dünne Beine. Vergleichsbild Referenz/Prototyp an Roman geschickt.

## 2026-11-14 – Nacht

- Roman fragte nach einem Low-Poly-Konzept fürs Schaf → `kit.skin_mesh()` (Skin + Subsurf aus Skelett, Material
  per Region). Schaf-Prototyp 3 als ein Mesh: Wollkörper mit Locken-Relief, dunkler Kopf/Beine, Wollkappe,
  Augen/Ohren/Schwanz per Raycast. Wartet auf Romans Urteil.
- Lager-Fenster: Ausbauen (blauer Rahmen oben) und Verkaufen (warmer Rahmen unten) getrennt.
- PC auf Romans Wunsch per Computer-Use heruntergefahren.

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
- Roman: „Die tiere sehen schrecklich aus“ → Prototyp-Huhn komplett neu (aufrechter Körper, S-Hals, großer Kopf,
  4-lappiger Kamm, zweiteiliger Schnabel, Kehllappen, Feder-Schwanzfächer, Tropfen-Flügel, Federhosen, Zehen +
  Sporn) und **Kontrastlicht für Figuren** (`kit.character_light()`: Sonne 4.6, Himmel 0.55; `render.py` setzt
  vor jedem Frame `kit.set_light()` zurück). Wartet auf Romans OK, bevor alle Tiere so neu gebaut werden.
- Roman: „besser aber noch unnatürlich“ → Prototyp 2: `feather_mat()` (Voronoi-Federstruktur in Farbe + Relief),
  Vogelaugen seitlich mit oranger Iris, kleinerer Kopf, gebogener Schnabel, Halsfedern, Sichel-Schwanzfedern,
  geschichtete Schwungfedern, schuppige Beine mit Krallen, Ohrläppchen.
- Roman: Version 1 war besser → zurück auf V1 + Korrekturen: Flügel 32° nach hinten-unten geneigt und tiefer,
  Schnabel wächst aus dem Kopf (Basis im Kopf versenkt), Kamm-Lappen stehen entlang der Kopfrundung
  (Normalen-Ausrichtung) auf einem Grat, der dem Schädel folgt. (`feather_mat` wieder entfernt.)
- Roman: hinterer Kamm schwebte noch → Kamm-Lappen und Grat werden per Raycast (`Surface.toward`) auf die echte
  Kopf-Oberfläche gesetzt (Metaball-Fläche liegt innerhalb des Radius), Lappen etwas größer.
  Lehre: **Anbauteile immer per Raycast auf die Fläche setzen, nie mit geschätztem Radius.**
- Huhn freigegeben, alle Huhn-Frames im Spiel. Kuh-Prototyp im selben Stil: Kontrastlicht, Flecken flach als
  Muster im Material (`patched_mat`, Noise statt aufgesetzter Kugeln), kompakter Körper, größerer Kopf, breites
  Maul aus dem Gesicht, Ohren/Hörner/Stirnlocke per Raycast, Wimpern, gespaltene Hufe. → freigegeben, im Spiel.
- Schaf-Prototyp: weiche Wolke (glattes Wollmaterial statt Voronoi-Sprenkel, fester Kern + 16 Bauschen),
  langer dunkler Kopf weiter vorne, Hängeohren + Wollkappe per Raycast, große Augen mit Lid, gespaltene Hufe.
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
