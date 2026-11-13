# Mossglen – Stil-Bibel

Verbindlich für alle Grafiken. Die Werte stehen als Code in `tools/art/palette.py`.
Wer ein Asset ändert, ändert zuerst die Palette oder den Baukasten, nie Einzelfarben im Asset.

## 1. Gefühl

- **Warm, weich, ruhig.** Wie ein Bilderbuch an einem späten Sommernachmittag.
- **Rund statt eckig.** Alle Ecken abgerundet, Linien mit runden Enden.
- **Moos als Erkennungszeichen.** Dächer, Steine, Zäune tragen kleine Moospolster. Das ist der eigene Look von Mossglen und grenzt uns klar von anderen Farm-Spielen ab.
- Keine harten Schwarztöne, kein reines Weiß, keine Neonfarben.

## 2. Perspektive und Raster

- **Dimetrische Schrägansicht 2:1.** Eine Kachel ist eine Raute **128 × 64 px** (Basisauflösung 1x).
- Achse X des Rasters zeigt auf dem Bildschirm nach **rechts unten** (+64, +32), Achse Y nach **links unten** (−64, +32).
- Höhe: 1 Einheit Höhe = 1 px nach oben.
- **Ankerpunkt** jedes Sprites ist der Bodenkontaktpunkt (Mitte der Grundfläche). Danach sortiert das Spiel die Tiefe (Y-Sort).

## 3. Licht und Schatten

- Licht kommt von **oben links**.
- Flächen eines Körpers: **Oberseite hell**, **linke Seite mittel**, **rechte Seite dunkel**.
- Rundkörper (Bäume, Büsche, Tiere): radialer Verlauf, Lichtpunkt oben links, dazu 1–3 weiche Glanzflecken.
- **Bodenschatten**: weiche Ellipse, Farbe `shadow` mit 22 % Deckkraft. Keine Echtzeitschatten.

## 4. Kontur

- Farbe `outline` (#4A3A2E, warmes Dunkelbraun), nie Schwarz.
- Stärke: **3 px** außen, **1,5 px** für Innendetails.
- Runde Linienenden und -verbindungen.
- Zusammengesetzte Formen (Baumkrone aus Kreisen) bekommen nur eine **Außenkontur**: erst alle Teile dick in Konturfarbe zeichnen, dann alle Füllungen darüber.

## 5. Farbpalette

| Name | Hex | Verwendung |
|---|---|---|
| outline | #4A3A2E | Konturen |
| grass_light / grass / grass_dark | #B5D86A / #93C454 / #6FA43E | Wiese |
| moss / moss_light | #6E9E3F / #9CC95A | Moospolster, Signatur |
| soil_light / soil / soil_dark | #C98F5E / #A8714A / #7E4F33 | Ackerboden |
| path / path_dark | #E2C690 / #C4A46C | Wege |
| wood_light / wood / wood_dark | #D6955E / #B9774A / #8A5232 | Holz |
| barn / barn_dark / barn_side | #E0705A / #B8503F / #C95E4B | Scheunenwände |
| roof / roof_dark | #6F87A8 / #536A8A | Schieferdach |
| cream / cream_dark | #FFF4DC / #EAD9B5 | Zierleisten, UI |
| wheat / wheat_dark | #F4CB5B / #D9A23E | Reifes Getreide |
| leaf_light / leaf / leaf_dark | #A6D364 / #7DB547 / #4F8A34 | Laub |
| sky / water | #9FD7EC / #6FBFDD | Himmel, Wasser |
| gold / gold_dark | #FFD45E / #E3A72F | Münzen |
| emerald / emerald_dark | #4FD39A / #23A46F | Smaragde (Premiumwährung) |
| shadow | #3B4A2A | Schatten (mit Transparenz) |

Sättigung bleibt mittel. Akzente (Gold, Smaragd, Scheunenrot) dürfen kräftiger sein.

## 6. Formen und Proportionen

- Gebäude: etwas gedrungen, Dächer groß und weich überstehend (Überstand 8–12 px).
- Tiere und Dinos: **Chibi-Proportionen**, Kopf groß, Körper rund, große Augen mit Glanzpunkt, kurze Beine.
- Pflanzen: in Büscheln, nie einzelne Halme.

## 7. Animation

- Alles lebt leicht: Wind lässt Pflanzen und Bäume schwingen (Shader), Tiere wippen beim Laufen.
- **Squash & Stretch** bei jeder Interaktion (Pflanzen, Ernten, Platzieren): 0,15–0,3 s, Easing `back`/`elastic`.
- Nichts blinkt hektisch. Kein Bildschirmwackeln.

## 8. UI

- Panels: Creme (`cream`) mit Holzrahmen (`wood`), Kontur `outline`, Ecken 18 px rund.
- Zahlen groß und gut lesbar, Icons links neben der Zahl.
- Mindestgröße für Touch-Ziele: 44 × 44 pt.

## 9. Ton (Kurzfassung)

- Musik: Marimba, Zupfinstrumente, Flöte, weiche Flächen. 70–90 BPM, Dur, viel Raum.
- Soundeffekte: kurz, rund, tonal (Töne passen zur Tonart der Musik), nie schrill.
