# Was Roman nicht gefällt

Neueste oben. Format: Datum – was – Anlass/Zitat – Folge.

- **2026-11-14 (03:41) – „Die Benutzeroberfläche sieht weiterhin schrecklich aus, man hat keine Differenzierung.“**
  Besonders: **Ausbauen stand direkt neben Verkaufen** → man denkt, man könne die Axt ausbauen.
  **Folge:** Lager-Fenster getrennt in blauen Ausbau-Rahmen oben (Kapazität + Knopf) und warmen Verkaufs-Rahmen
  unten (nur zur gewählten Ware). Allgemein: Bereiche mit eigener Rahmenfarbe trennen. Kompletter UI-Umbau bleibt
  Aufgabe M9.5e.

- **2026-11-13 (23:37) – Schaf-Prototyp 1: „Schaf ist schrecklich“.** Bild: `rejected/m95_sheep_proto1.png`.
  Riesige Wolkenkugel, kleiner dunkler Kopf tief vergraben, lange Stelzenbeine, grimmige Augen.
  **Folge:** zwei Varianten zur Auswahl zeigen (Hay-Day-Proportionen vs. süßes Lamm).

- **2026-11-13 (23:20) – Tiere nach Durchgang 1 (Augenlider, neues Schwein/Schaf): „Die tiere sehen schrecklich aus“.**
  Bild: `rejected/m95_animals_pass1.png`. Knetmassen-Look aus Metaball-Klumpen, Zylinder-Beine, keine klaren Formen.
  **Folge:** Tiere werden von Grund auf neu gebaut, ein Tier als Prototyp zuerst (Huhn), erst nach Romans OK alle.
- **2026-11-13 (23:23) – Prototyp-Huhn 1: „sieht besser aus aber noch unnatürlich“.** Bild: `rejected/m95_hen_proto1.png`.
  Glatte Plastik-Oberfläche, Kulleraugen vorne, dicker Schlauch-Hals, gleich geformte Schwanz-Blobs.
  **Folge:** natürlicher – Federstruktur, Vogelaugen seitlich mit oranger Iris, schlankerer Hals mit Halsfedern,
  geschichtete Flügel- und Sichel-Schwanzfedern, schuppige Beine mit Krallen.

- **2026-11-13 (Abend, erster eigener Test am PC) – großes Feedback:**
  - **Tiere sehen „extrem schlecht“ aus** (Bild: `rejected/m9_dinos_pen.png`). Sie müssen mindestens die Stufe
    von `references/img/hd_animals_pets.png` haben: echte Charakter-Modelle mit Mimik, Glanz, frecher Ausdruck.
  - **Baumkronen flackern in den Herbstfarben**, wenn man mit gedrückter Maustaste zieht. → behoben (Zufall
    pro Pflanze kommt jetzt aus dem Farbkanal statt aus der Position).
  - **Kein Feedback**: Hover und Klick müssen überall sichtbar sein – Felder, Tiere, Gebäude.
  - **Icons über den Tieren hüpfen**, wenn das Tier läuft (Blase wackelt mit). Muss ruhig stehen.
  - **UI ist „so schlecht und offset“** – Abstände/Ausrichtung stimmen nicht, muss deutlich schöner werden
    (Vorbild: `hd_ui_redesign_*.png`, `hd_dialogs_wheel.png`, `hd_popups.png`, `hd_loading_shop_vertical.png`).
  - **Terrain muss besser werden** (Vorbild: `hd_winter_farm.png`).
  - **Tutorial mit fertigem Hof ist falsch**: Es muss mit einem komplett leeren Hof starten, alles selber bauen.
  - **Runde Item-Rahmen** (Kreis-Slots, Ring als Auswahl): „die Item rahmen dürfen nicht rund sein sondern müssen
    so wie in den Referenzen sein“ → weiche, abgerundete Quadrate ohne dunkle Kontur, Auswahl gelb hinterlegt.
  - **Flache SVG-Item-Icons** (Werkzeuge, Waren) – sollen 3D-gerendert sein wie `hd_item_icons_3d.png`.
  - **Zu viel Platz von Anfang an**: Land muss Stück für Stück erweitert werden, dafür Werkzeug sammeln.

- **2026-11-13 – HUD mit 3D-gerenderten Icons und Creme-Kapseln.** „Die UI bitte in 2d und mehr an den
  Referenzbildern orientieren.“ Bild: `rejected/m0_hud_3d.png`.
  **Folge:** UI ist ab jetzt **flach gezeichnete 2D-Grafik** (Vektor, kräftige Verläufe, dicke Kontur, Glanz),
  Aufbau wie im Referenz-HUD: Stern + XP-Leiste oben, große weiße Zahlen mit dicker Kontur, runde gelbe Knöpfe.

- **2026-11-13 – Flache SVG-Grafik (M0, erster Stand).** „sieht überhaupt nicht so schön aus wie es sein soll“.
  Bild: `rejected/m0_svg_atlas.png`. Flache Vektorformen mit Kontur, wenig Volumen, wirkt wie Clipart.
  **Folge:** Grafik-Pipeline auf Blender-3D-Pre-Rendering umgestellt.
- **2026-11-13 – Unfertig/Prototyp-Look.** Roman will ausdrücklich nichts, das „nach Enttäuschung“ oder
  „nach einem unfertigen Prototypen“ aussieht. **Folge:** Jedes Asset vor Abgabe im Spiel-Screenshot gegen
  die Referenzen prüfen.
