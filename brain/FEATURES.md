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
- ✅ Gebäude und Gehege verschieben: gedrückt halten → neuer Platz → Haken (Hof wird aus dem Spielstand neu aufgebaut, Kamera springt dabei zurück)
- ⬜ Drehen, Einlagern; Verschieben ohne Neuaufbau
- ✅ Vogelscheuche, Bank, Laterne, Hecke, weißer Lattenzaun, Milchkannen, Wegweiser, Holzstapel, Trittsteine
- ⬜ Mehr Deko: Windrad, Blumenbeet, Steinmauer, Teich, Hundehütte, Reifenschaukel, Leiter, Schubkarre, Heuwagen
- 🟡 Saison-Deko: ✅ Laubhaufen, kahler Baum · ⬜ Kürbislaterne, Schneemann

## B. Felder & Ernte
- ✅ Felder kaufen/verschieben, Zieh-Säen, Wisch-Ernte, 5 Pflanzen
- ✅ Reifer Weizen aus dünnen Einzelhalmen (Teppich mit dicken Kolben verworfen) · ✅ flache Äcker mit Furchen
- ⬜ Junger Weizen und übrige Pflanzen ebenso fein
- ⬜ Mehr Pflanzen (Soja, Zuckerrohr, Kürbis, Indigo, Baumwolle, Chili …), Obstbäume/-büsche mit Ernte + Verwelken/Wiederbeleben
- ⬜ Fortschrittsbalken „Reif in …“ über dem Feld / „Fertig zum Einsammeln“ über Gebäuden

## C. Tiere
- ✅ Huhn, Kuh, Schaf (freigegeben) · 🟡 Schwein v3 (v2 abgelehnt; v3 auf Kuh-Bauplan, wartet auf Romans OK)
- ⬜ Ziege, Pferd, Hunde, Katzen, Hasen, Esel als Haustiere mit Hütte/Futternapf
- ⬜ Füttern per Ziehen, Sammeln per Ziehen (Korb-Symbol mit Pfeil), Tiere zeigen Hunger/Fertig

## D. Produktion
- ✅ 9 Produktionsgebäude mit Warteschlange · ⬜ Meisterschafts-Sterne je Gebäude
- ⬜ Weitere: Grill, Zuckermühle, Saftpresse, Eismaschine, Kuchenofen, Schmelzofen (Mine)

## E. Mine (Bild `hd_style_mine_tools`)
- ✅ Mine als Eingang in der Klippe am Westrand (ab Level 3), Fenster mit Schaufel/Spitzhacke/Dynamit/TNT-Fass
- ✅ Erze im Lager (Kohle, Eisen, Silber, Gold, Platin), verkaufbar; Spitzhacke/TNT als Fund und in Kisten
- ✅ Schmelzofen (Level 4): Eisen-, Silber-, Gold-, Platinbarren
- ✅ Schmelzofen neu aus Ziegeln (blaues Dach, Blasebalg, Kohlekiste) · ✅ Minenfels kantig
- ⬜ Schmuck aus Barren; Grasdecke auf dem Minenfels (zwei Versuche: erst Neon-Scheiben, dann im Fels versunken)
- ⬜ Schienen mit Lore

## F. Handel & Aufträge
- ✅ Auftragstafel + Lieferwagen · ✅ Besucher an der Auftragstafel (alle 5 Min, zahlt 1,6× Lagerpreis; nutzt vorerst die Figur von Händler Pip)
- ✅ Straßenstand (Laden → Deko, Level 3): 4 Plätze, günstig/normal/teuer – teurer dauert länger, dann kassieren
- ⬜ Eigene Besucher-Figuren
- ⬜ Schiff am Steg (Kisten füllen, Frist), Zug/Stadt-Besucher, Zeitung mit Angeboten
- ⬜ Freunde: Hof von Elli besuchen, helfen, handeln (braucht Supabase – Entscheidung offen)

## G. Fortschritt & Belohnungen
- ✅ Level/XP, Land-Parzellen, Hindernisse mit Werkzeug, Silo/Scheune-Ausbau, Erfolge, Feste
- ✅ Glücksrad (1× täglich gratis, sonst 3 Smaragde), Schatzkisten auf der Farm, tägliches Geschenk (7 Tage)
- ⬜ Briefkasten
- ⬜ Helfer (sammeln/säen automatisch für eine Zeit), Booster

## H. Oberfläche
- 🟡 UI v2 (7 Layouts gezeigt, warten auf Urteil): HUD mit runden Eck-Knöpfen, Laden, Scheune, Ausbau, Dialoge
- ⬜ Item-Blasen: weißes Zahlenschild + 3D-Icon + gelber Pfeil auf das Ziel
- ⬜ Freunde-Knopf, Briefe-Knopf, Lupe/Suche, Bearbeiten-Knopf unten rechts

## I. Grafik (Ziel-Look, siehe REFERENCES.md „Artstyle-Zielbilder“)
- ⬜ Gras satter + Büschel, Wege weicher, Fels-Kante/Klippe am Kartenrand, Fluss mit Steg
- ⬜ Gebäude gedrungener mit mehr Kleinteilen (Leitern, Kisten, Milchkannen), Kantenglanz
- ✅ Grasbüschel mit dünnen Halmen · ✅ Tannen bleiben im Herbst grün
