# Feature-Analyse der Referenzbilder → Bauliste

Stand 2026-11-15. Quelle: alle Bilder in `brain/references/img/` (nur lokal). Roman: „alle Features, die du auf den
Bildern erkennst, implementieren – es müssen extrem viele Features sein.“ Das Spiel ist für Roman und Elli
(PC + Handys). **Funktionen dürfen 1:1 so arbeiten wie im Vorbild; Grafiken, Figuren und Namen bleiben eigene**
(CLAUDE.md Regel 3, öffentliches Repo).

Legende: ✅ im Spiel · 🟡 teilweise · ⬜ offen. Reihenfolge = Bau-Reihenfolge.

## A. Bauen & Dekorieren (Roman: „Grasbüschel, Wege – eigentlich alles ist platzierbar“)
- ✅ Deko-Reiter im Laden, frei platzierbare Deko (Blumen, Büsche, Bäume, Steine, Kisten, Fässer, Brunnen)
- ✅ Wege mit dem Finger malen, Antippen entfernt (weiche Ränder über die Bodenmaske)
- ✅ Grasbüschel, Kürbisse, Strohballen (einzeln + Stapel) als neue Modelle
- ✅ Zaunstücke einzeln setzen; Deko antippen → Verschieben / Verkaufen
- ⬜ Mehr Wegarten (Kopfsteinpflaster, Trittsteine, Holzsteg), Weg-Ecken sauber
- ⬜ Bearbeiten-Modus: alles (auch Gebäude, Gehege) verschieben, drehen, einlagern
- ⬜ Mehr Deko: Vogelscheuche, Windrad, Bank, Laterne, Blumenbeet, Hecke, Steinmauer, weißer Lattenzaun,
  Teich, Hundehütte, Reifenschaukel, Milchkannen, Leiter, Schubkarre, Heuwagen, Wegweiser, Gartenzwerg
- ⬜ Saison-Deko (Herbst: Laubhaufen, toter Baum, Kürbislaterne; Winter: Schneemann)

## B. Felder & Ernte
- ✅ Felder kaufen/verschieben, Zieh-Säen, Wisch-Ernte, 5 Pflanzen
- ⬜ Weizen als dichter goldener Teppich (Grafik), Äcker mit Furchen-Struktur
- ⬜ Mehr Pflanzen (Soja, Zuckerrohr, Kürbis, Indigo, Baumwolle, Chili …), Obstbäume/-büsche mit Ernte + Verwelken/Wiederbeleben
- ⬜ Fortschrittsbalken „Reif in …“ über dem Feld / „Fertig zum Einsammeln“ über Gebäuden

## C. Tiere
- ✅ Huhn, Kuh, Schaf (freigegeben) · 🟡 Schwein (Prototyp fehlerhaft)
- ⬜ Ziege, Pferd, Hunde, Katzen, Hasen, Esel als Haustiere mit Hütte/Futternapf
- ⬜ Füttern per Ziehen, Sammeln per Ziehen (Korb-Symbol mit Pfeil), Tiere zeigen Hunger/Fertig

## D. Produktion
- ✅ 9 Produktionsgebäude mit Warteschlange · ⬜ Meisterschafts-Sterne je Gebäude
- ⬜ Weitere: Grill, Zuckermühle, Saftpresse, Eismaschine, Kuchenofen, Schmelzofen (Mine)

## E. Mine (Bild `hd_style_mine_tools`)
- ⬜ Mineneingang im Fels, Werkzeuge: Schaufel, Spitzhacke, Dynamit, TNT-Fass (je Zahlenschild + Pfeil)
- ⬜ Erze: Silber, Gold, Platin, Eisen, Kohle → Schmelzöfen → Barren → Schmuck
- ⬜ Schienen mit Lore

## F. Handel & Aufträge
- ✅ Auftragstafel + Lieferwagen · ⬜ Besucher-Händler (Layout 05) · ⬜ Straßenstand (eigene Waren zum Preis einstellen)
- ⬜ Schiff am Steg (Kisten füllen, Frist), Zug/Stadt-Besucher, Zeitung mit Angeboten
- ⬜ Freunde: Hof von Elli besuchen, helfen, handeln (braucht Supabase – Entscheidung offen)

## G. Fortschritt & Belohnungen
- ✅ Level/XP, Land-Parzellen, Hindernisse mit Werkzeug, Silo/Scheune-Ausbau, Erfolge, Feste
- ⬜ Glücksrad (täglich), Schatzkisten auf der Farm, tägliche Belohnung, Briefkasten
- ⬜ Helfer (sammeln/säen automatisch für eine Zeit), Booster

## H. Oberfläche
- 🟡 UI v2 (7 Layouts gezeigt, warten auf Urteil): HUD mit runden Eck-Knöpfen, Laden, Scheune, Ausbau, Dialoge
- ⬜ Item-Blasen: weißes Zahlenschild + 3D-Icon + gelber Pfeil auf das Ziel
- ⬜ Freunde-Knopf, Briefe-Knopf, Lupe/Suche, Bearbeiten-Knopf unten rechts

## I. Grafik (Ziel-Look, siehe REFERENCES.md „Artstyle-Zielbilder“)
- ⬜ Gras satter + Büschel, Wege weicher, Fels-Kante/Klippe am Kartenrand, Fluss mit Steg
- ⬜ Gebäude gedrungener mit mehr Kleinteilen (Leitern, Kisten, Milchkannen), Kantenglanz
- 🟡 Grasbüschel-Modell wirkt noch zu dick („Sellerie“) → dünnere, spitze Halme
