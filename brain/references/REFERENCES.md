# Referenzen – Auswertung

Quelle: 14 Hay-Day-Screenshots von Roman (13.11.2026). Die Bilder liegen nur lokal in `img/`
(nicht im öffentlichen Repo, Urheberrecht Supercell). Wer sie auf einem anderen Rechner braucht,
kopiert sie manuell dorthin.

Ziel: **gleiche Qualitätsstufe und Gemütlichkeit, aber eigene Welt.** Kein Asset, keine Figur und
kein Name wird übernommen.

## Bilder

| Datei | Zeigt | Wichtig daran |
|---|---|---|
| `hd_farm_overview_ui.png` | Ganze Farm mit HUD | Dichte, Farbigkeit, HUD-Stil (runde gelbe Buttons, dicke Zahlen mit Kontur) |
| `hd_promo_pig_bakery.png` | Werbebild Schwein + Backofen | Figur-Charme: große Schnauze, Glanz, freundlicher Blick |
| `hd_buildings_wheat_trees.png` | Molkerei, Weizen, Apfelbäume | Weizenfeld als dichte goldene Masse, Gebäude auf Pflaster-Sockel |
| `hd_animals_sheet.png` | Ziege, Schaf, Schwein, Kuh, Huhn, Haustiere | **Tier-Stil**: 3D, weiche Schattierung, große Augen, leicht freche Mimik |
| `hd_animal_pens.png` | Gehege-Übersicht | Gehege = Erdfläche + Zaun + Tränke/Futter, Tiere klein aber lesbar |
| `hd_trees_paths_pets.png` | Bäume, Wege, Hundehütte | Wege mit weichen, organischen Rändern; Bäume mit Blattstruktur |
| `hd_horses_stables.png` | Pferde, Stall, Blumenrand | Blumen- und Busch-Ränder als Rahmen, sattes Gras |
| `hd_wildlife_elephant.png` | Elefant, Giraffe | Übertriebene Proportionen, glänzende Augen mit Lidern |
| `hd_valley_autumn_water.png` | Herbsttal, Wasserfall | Wasser türkis mit hellem Rand, Herbstfarben, Felsen mit Moos |
| `hd_buildings_tierlist.png` | Viele Produktionsgebäude | Jedes Gebäude: eigener Sockel + Kleinkram (Fässer, Bank, Säcke) |
| `hd_building_kiln.png` | Brennofen freigestellt | Weiche Formen, Punkte-Muster, Pflaster-Sockel mit weichem Rand |
| `hd_building_bakery.png` | Backofen (Kuppel) freigestellt | Ziegel, Holz, Säcke – Materialien klar unterscheidbar |
| `hd_building_grill.png` | Grill-Ofen freigestellt | Kanten leicht gerundet, Ziegel einzeln modelliert, Stern-Akzent |
| `hd_building_machine.png` | Saftpresse freigestellt | Glänzendes Metall, kräftiges Rot, Holzfässer mit Metallreifen |
| `hd_animals_pets.png` | Nutztiere + Haustiere (Katzen, Hunde) | **Mindest-Qualität für Tiere** (Roman): Mimik, Glanz, freche Gesichter, klare Silhouette |
| `hd_orderboard_truck.png` | Auftragstafel + Lieferwagen | Tafel mit Zetteln und Häkchen, roter Oldtimer-Laster mit grüner Ladefläche |
| `hd_winter_farm.png` | Winterhof mit HUD | **Terrain-Vorbild**: Gras mit Halmen und hellen Flecken, Tannen mit Schnee, Felsen, Silo, Haus mit Lichterkette |
| `hd_ui_redesign_hud.png` | HUD-Umbau-Studie | Stern füllt sich, Münzen/Edelsteine als dunkle Kapseln, Shop-Knopf rechts unten (Daumen), Menü statt Zahnrad |
| `hd_ui_redesign_shop.png` | Shop als waagrechte Karten | Karten mit Bild, Name, Text, Preis; gesperrte Karten grau mit Schloss; Reiter oben; Laufleiste unten |
| `hd_ui_redesign_shop2.png` | Shop senkrecht vs. waagrecht | Gelbe Karten, Reiter-Symbole, „5/6“-Zähler |
| `hd_dialogs_wheel.png` | Glücksrad, Helfer, Händler-Dialoge | Sprechblase + Figur, große gelbe Antwort-Knöpfe, Tauschangebot „6 Weizen → 50 Münzen“ |
| `hd_loading_shop_vertical.png` | Ladebildschirm, Shop senkrecht | Logo + Ladebalken mit Tipp, Shop-Kategorien Felder/Gebäude, Zähler „6/9“ |
| `hd_item_icons_3d.png` | Scheunen-Inhalt: Werkzeuge + Waren | **Icon-Vorbild** (Roman): 3D-gerenderte Objekte, große weiße Zahl mit Kontur, kein Kästchen |
| `hd_upgrade_dialog.png` | Ausbau-Dialog Scheune | Senkrechte Liste: 3D-Material-Icon, große Zahl „82/82“ mit Kontur, grüner Haken rechts wenn genug; runder gelber Bestätigen-Knopf mit grünem Haken; Kopfzeile „Kapazität auf X erhöhen“ |
| `hd_popups.png` | Pop-ups: Katalog, Angebote, gesperrtes Gebiet, Belohnung | Gesperrtes Gebiet als Bild mit Schloss + Schleife, Zeitungs-/Katalog-Optik |

## Was den Look ausmacht (Regeln für Mossglen)

### Technik
- **Alles ist 3D, vorgerendert zu 2D-Sprites.** Feste Schrägkamera, ca. 30° von oben, orthografisch.
- Weiches Licht von **oben links vorne**, starkes Umgebungslicht (kaum harte Schatten), weicher Kontaktschatten unter jedem Objekt.
- **Dunklere Randkante** an der Silhouette (keine schwarze Linie, sondern abgedunkelte Eigenfarbe, 1–2 px).

### Farbe
- **Gesättigt und hell.** Gras ist ein leuchtendes Gelbgrün (~#8CC63F bis #A8D84A), nicht graugrün.
- Akzentfarben kräftig: Rot (Scheune, Maschinen), Gold (Weizen), Türkis (Wasser).
- Schatten sind farbig (Grün-/Blauton), nie grau.

### Formen
- **Leicht übertrieben und gedrungen.** Gebäude dick, Dächer weit überstehend, Kanten abgerundet (Bevel).
- **Einzelteile sind modelliert**: Ziegel, Bretter, Pflastersteine, Metallreifen. Das gibt Detail ohne Unruhe.
- Gebäude stehen auf einem **eigenen Sockel** (Pflaster, Sand, Holzbohlen) mit **Kleinkram** drumherum.

### Tiere
- Rund, weich, **große Augen mit Glanzpunkt**, deutlicher Ausdruck (leicht frech/freundlich).
- Körper glatt schattiert, kein Fell-Rauschen. Wenige klare Farbflächen.
- Klein im Spiel, daher **Silhouette und Kopf** müssen stark sein.

### Natur
- Bäume: Kronen aus **vielen Blatt-Büscheln** mit hell/dunkel-Wechsel, nicht eine glatte Kugel.
- Gras hat feine Struktur (dunklere Halm-Tupfer), Wege sind sandig mit weichen Rändern.
- Viel Kleinvegetation: Blumen, Büsche, Steine als Rahmen.

### UI
- Runde, dicke Buttons mit Glanz und dunklem Rand. Große Zahlen mit dicker dunkler Kontur.
- Leisten (XP, Lager) als Kapseln mit Verlauf.

## Mossglen-eigene Abgrenzung
- **Moos** als Signatur: Dachkanten, Steine, Zäune tragen Moospolster.
- **Dinos** (Chibi-Fantasy) als Alleinstellung.
- Eigene Gebäudeformen (z. B. Scheune mit Rundfenster und Moosdach statt klassischer Hay-Day-Scheune).

## 2026-11-15 – Artstyle-Zielbilder (Roman: „bekommst du so ein Artstyle hin?“)

Lokal: `hd_style_harvest_corner.png`, `hd_style_mine_tools.png`, `hd_style_autumn_barn.png`, `hd_style_farm_full.png`.
Das ist der Ziel-Look für Schritt 3 (Terrain/Grafik). Was den Look ausmacht:

- **Boden:** sattes, warmes Grün mit sichtbaren Grasbüscheln; Erdwege mit weich ausgefransten Rändern, nie harte Kachelkanten.
- **Weizen:** dichtes, goldgelbes Volumen mit heller Oberkante und dunklerem Fuß – wirkt wie ein Teppich, nicht wie Einzelpflanzen.
- **Äcker:** rotbraune Bretter-/Furchenstruktur, klar vom Gras abgesetzt.
- **Objekte:** gedrungene, übertriebene Proportionen, runde Kanten, kräftige Grundfarbe + heller Kantenglanz, weicher Kontaktschatten.
- **Licht:** warmes Hauptlicht von oben links, kühle Schatten, hohe Sättigung, nichts Graues.
- **Kleinkram:** Kürbisse, Kisten, Leitern, Steine, Blumen am Rand – jede Ecke erzählt etwas.
- **Bäume:** Tannen aus gestuften Zweiglagen, Laubbäume als klumpige Kronen mit hellen Blattflecken; Herbst in Orange/Rot.
- **Item-Blasen:** weißes Zahlenschild + großes 3D-Icon + gelber Pfeil auf das Ziel.
- **HUD (hd_style_farm_full):** große runde gelbe Knöpfe in den Ecken, Level-Stern an der XP-Leiste, Zahlen groß und weiß mit dunklem Rand.

## 2026-11-16 – 15 Bilder „so hat es auszusehen“ (lokal `hd2_*.png`)
Roman: selbstständig analysieren, einordnen, einbauen. Einordnung → Bauauftrag:

| Bild | Was es zeigt | Bauauftrag |
|---|---|---|
| `hd2_prod_anim_1..3` | Produktionsgebäude **arbeiten sichtbar**: Rührarme drehen, Staubwölkchen steigen auf | Arbeitende Gebäude wippen im Takt und stoßen Wölkchen aus; stehende sind ruhig |
| `hd2_butterflies_visitor` | Schmetterlinge über dem Hof, Besucher mit Sprechblase + Ware | Schmetterlinge als Ambiente; Besucher-Blase (haben wir) |
| `hd2_build_clouds_xp` | Bau fertig: Staubwolken mit Glitzern, blauer Stern „+17“ | Enthüllen = Wolken + XP-Stern |
| `hd2_build_tarp` | Baustelle = weiße geflickte Plane über 4 Stangen | Baustellen-Modell „Plane“ |
| `hd2_build_gift` | Fertig, noch nicht enthüllt = Plane mit roter Schleife | Fertig-Zustand „Geschenk“, Antippen enthüllt |
| `hd2_timer_bar_bubbles` | Unten: Name, blauer Zeitbalken, Blitz-Knopf mit Edelstein-Preis; oben Werkzeug-Blasen mit Zahlenschild + Pfeil + Lichtkegel | Zeitbalken mit Beschleunigen; Blasen-Stil |
| `hd2_roadside_shop_ui` | Stand-Fenster: gestreifte Markise, Holzschild als Titel, Holzkisten als Plätze | Straßenstand-Fenster so gestalten |
| `hd2_tool_bubble_axe/saw` | Baum antippen → Blase: Zahl, Plus-Knopf, Werkzeug, Pfeil, Lichtkegel | Hindernis-Blase statt Fenster |
| `hd2_locked_land_walls/edge/selected` | Gesperrtes Land: olivgelbe Wiese, niedrige bemooste Steinmauern als Raster, Herbstbäume, Tümpel; gewähltes Feld heller | Mauern-Raster + Olivton; Antippen wählt Feld |
| `hd2_locked_land_popup` | „Erweiterungen ab Level 22“: Bild im roten Band-Rahmen, blaues Banner, Schloss an der Schleife | Land-Popup so gestalten |
| alle | HUD: Stern + Balken links oben, runde Knöpfe links als Spalte, Münzen/Edelsteine rechts oben, runde Knöpfe rechts unten; leichte Nebelschwaden | HUD-Anordnung, Nebel |
