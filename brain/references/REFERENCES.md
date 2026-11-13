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
