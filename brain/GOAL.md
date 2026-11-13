# Projektplan: "Mossglen" – Cozy Farm & Valley Game

> Name: **Mossglen** (EN) / **Moosental** (DE-Untertitel). Vom Nutzer bestätigt.
> Vor dem Launch: Markenrecherche (DPMA / EUIPO / App Stores).

## 0. Festgelegte Entscheidungen

| Thema | Entscheidung |
|---|---|
| Modell | **Free-to-play.** Werbung nur freiwillig (Rewarded): z. B. max. **5 Werbungen pro Tag → je 5 Smaragde** (Premium-Währung), plus Beschleunigungen auf Wunsch. Nie erzwungen. |
| Zielgruppe | **Alle Altersgruppen** → kindgerechte Regeln (siehe Abschnitt 10) |
| Budget | **0 €.** Alles muss mit kostenlosen Tools und Free-Tiers laufen (siehe Abschnitt 9) |
| Testgeräte | iPhone 11 vorhanden (Referenzgerät). Android-Gerät offen |
| Name | Mossglen |
| Dinos | Niedliche Fantasy-Dinos (Chibi-Proportionen, runde Formen, große Augen) |
| Qualität | Arbeit mit höchster Modellstufe/Effort (vom Nutzer eingestellt) |
| Grafik | **3D in Blender modelliert, zu 2D-Sprites vorgerendert** (seit 13.11.2026, SVG-Stil abgelehnt). Maßstab: Hay-Day-Qualität, eigene Welt |
| Brain | Projektwissen liegt in `brain/` (Ziel, Log, Entscheidungen, Geschmack, Referenzen), Regeln in `CLAUDE.md` |

---

## 1. Vision und Design-Säulen

Ein gemütliches 2.5D-Farm-Spiel für zwischendurch. Kurze Sessions (2–5 Min), kein Zeitdruck, keine Strafen.

1. **Cozy first:** Nichts verdirbt, nichts läuft ab, kein Verlust. Weiche Farben, runde Formen, ruhige Musik.
2. **Kurze Intervalle:** Produktionszeiten 10 s – 15 Min. Längere Dinge (Dino-Aufzucht, Bauprojekte) laufen offline weiter.
3. **Alles drin:** Farm, Tiere, Dinos, Angeln, Produktion, Handel, Besuchen, Dorf, Events.
4. **Fair monetarisiert:** Werbung ist freiwillig (Beschleunigung), IAP rein kosmetisch/Komfort, kein Pay-to-win im Handel.
5. **Flüssig überall:** Referenz iPhone 11 (A13, 4 GB RAM), 60 FPS stabil. Windows, Android, iOS aus einer Codebasis.
6. **Eigener Stil:** Keine Hay-Day-Assets, -Figuren, -Namen. Eigene Welt und eigene Charaktere.

**Welt/Story (kurz):** Du erbst einen verwilderten Hof im Moosental. Das Tal ist voller Geheimnisse: ein See mit seltenen Fischen, ein Urzeit-Tal mit zahmen Dinos, ein Dorf, das du wieder aufbaust. Die NPCs (Müller Brumm, Fischerin Lotte, Paläontologin Dr. Fenna, Händler Pip) geben Aufträge.

---

## 2. Technik-Stack

| Bereich | Wahl | Begründung |
|---|---|---|
| Engine | **Godot 4.x** (Mobile- bzw. Compatibility-Renderer) | Kostenlos, kein Revenue-Share, leicht, 2D stark, Text-Szenen (gut für meine Arbeit), Export Win/Android/iOS |
| Sprache | **GDScript** (Gameplay), optional C++ GDExtension für Hotspots | Schnelle Iteration; nur bei Messung nach C++ auslagern |
| Darstellung | 2D mit Schrägansicht (isometrisch/dimetrisch), Y-Sorting, TileMap + Sprites | Auf iPhone 11 günstiger als echtes 3D, gleicher "2.5D"-Look |
| Backend | **Supabase Free-Tier** (Postgres, Auth, Edge Functions, Realtime) für den Start; Alternative: Nakama selbst gehostet auf Oracle Cloud "Always Free" | 0 €. Accounts, Cloud-Save, Freunde, Handel. Free-Tier pausiert bei Inaktivität und ist limitiert, ein Upgrade ist erst bei echten Spielerzahlen nötig (dann aus Werbeeinnahmen) |
| Datenbank | PostgreSQL (über Nakama/Supabase) | Server-autoritativer Zustand für Handel/Währung |
| Werbung | **Google AdMob** (Rewarded Ads) über Godot-Plugin | Standard für "Beschleunigen durch Werbung" |
| IAP | Google Play Billing, Apple StoreKit 2 (Godot-Plugins), Steam/MS Store für Windows | Serverseitige Receipt-Validierung |
| Analytics/Crash | Firebase Crashlytics + eigene schlanke Events | Stabilität und Balancing |
| CI/CD | GitHub Actions (macOS-Runner für iOS-Build) | **Kein eigener Mac nötig** |
| Lokalisierung | Godot `.po`/Translation-Server, DE + EN | Von Anfang an, keine fest codierten Texte |
| Inhalte | Daten in JSON/Godot-Resources (Pflanzen, Rezepte, Fische, Dinos, Gebäude) | Neue Inhalte ohne Code |

**Offline-first:** Das Spiel ist offline voll spielbar. Der Server synchronisiert den Spielstand. Handel und Besuche brauchen Verbindung.

---

## 3. Grafik-Pipeline (komplett von mir erzeugt, Blender-Pre-Render)

**Geändert am 13.11.2026:** Der flache SVG-Stil wurde abgelehnt. Neu: echte 3D-Modelle in Blender,
per Skript gebaut und zu 2D-Sprites gerendert (wie es auch Hay Day macht).

1. **Modelle per Python** (`tools/art/blender/`, Blender 5.3 als Python-Modul `bpy`, kostenlos, ohne GUI):
   Metaball-Körper für Tiere/Dinos, Einzelteile mit Bevel für Gebäude, Laub-Ballen mit Relief für Bäume.
2. **Feste Schrägkamera** (orthografisch, 2:1), weiches Licht von oben links, farbiges Fülllicht,
   Cycles-Renderer mit Denoiser. Weicher Bodenschatten über einen Shadow-Catcher-Pass.
3. **Nachbearbeitung** (numpy): getönter Schatten, 2-px-Kontur in abgedunkelter Eigenfarbe, Zuschnitt.
4. **Atlas** in 2048er-Seiten, Ankerpunkt pro Frame (`atlas.json`). Auflösung 2x (Kachel 256 × 128 px).
5. **Animation:** Tiere als Frame-Animationen (Idle mit Blinzeln, Laufen, Picken), 2 Blickrichtungen,
   im Spiel gespiegelt. Wind-Shader für Pflanzen, Squash & Stretch per Code.
6. **Boden:** nahtlose Gras- und Erdtexturen, ein Shader mischt sie über eine Zellen-Maske
   (Wege, Gehege, Gebäudeflächen mit weichen, natürlichen Rändern).
7. **UI:** glänzende Kapseln und Knöpfe (numpy), 3D-Icons, Schrift Fredoka (OFL).
8. **Cache:** Nur geänderte Assets werden neu gerendert. Volle Neuberechnung ca. 10–15 Min.

Stil-Regeln: `docs/STYLE_BIBLE.md`. Arbeitsweise und Lehren: Skill `.claude/skills/mossglen-art`.
Ein Illustrator/3D-Artist kann später einzelne Modelle ersetzen, ohne Code zu ändern (gleiche Frame-Namen).

---

## 4. Audio-Pipeline (komplett selbst erzeugt)

- **Musik:** Komposition als MIDI/Noten per Code (Python, `mido`/`pretty_midi`), gerendert mit **frei lizenzierten SoundFonts** (Lizenz prüfen, kommerziell erlaubt) oder per eigener Synthese. Stil: Akustikgitarre, Marimba, Flöte, Klavier, weiche Streicher.
  - Pro Biom/Tageszeit ein Loop (Morgen, Tag, Abend, Nacht, See, Dino-Tal, Dorf, Regen, Event).
  - Adaptive Schichten (Layer blenden ein, wenn du aktiv bist).
- **SFX:** Prozedurale Synthese (Python/NumPy, Envelopes, Filter): Pflanzen, Ernten, Münzen, Klicks, Wasser, Tiergeräusche (stilisiert), Angel-Plop, Dino-Brummen.
- **Ambience:** Vögel, Wind, Grillen, Wasser, geschichtet nach Tageszeit und Wetter.
- **Mix:** Eigene Busse (Musik/SFX/Ambience/UI), Lautstärkeregler, "Ducking" bei Dialogen.
- **Dateien:** OGG (Android/Windows), kleine Samples, gestreamte Musik, damit der Speicher auf dem iPhone 11 geschont wird.

Auch hier gilt: Es klingt sauber und stimmig, aber synthetisch. Später kann ein Komponist die Tracks ersetzen.

---

## 5. Spielsysteme (vollständiger Umfang)

1. **Farm:** Raster-Bauen/Platzieren (Drag & Drop), Felder, Bäume/Büsche, Dekoration, Zäune, Wege, Erweiterung der Fläche, Tag/Nacht, Wetter, Jahreszeiten.
2. **Anbau:** Getreide, Gemüse, Obst, Blumen. Wachstumsstufen sichtbar, Dünger, Wetterbonus.
3. **Tiere:** Hühner, Kühe, Schafe, Schweine, Pferde, Bienen. Füttern, Produkte einsammeln, Streicheln (Bindung = kosmetische Boni).
4. **Dinos (Urzeit-Tal):** Fossilien ausgraben → Eier ausbrüten → zahme Baby-Dinos aufziehen. Sie liefern Spezialprodukte (z. B. Urzeit-Ei, Bernstein) und sind Sammelobjekte mit Dino-Pedia. Cozy: Alle sind freundlich, keine Kämpfe.
5. **Angeln:** Eigener See, Fluss, Meer. Entspanntes Minispiel (Timing-Ring, ohne Scheitern), Köder, Ruten, Fischarten je nach Zeit/Wetter/Ort, Fisch-Sammelalbum, Fischteich auf der Farm.
6. **Produktion:** Mühle, Bäckerei, Molkerei, Marmeladenküche, Webstuhl, Zuckermühle, Räucherei, Brauerei, Töpferei, Werkbank usw. Mit Warteschlangen und kurzen Zeiten.
7. **Aufträge und NPCs:** Dorf-Lieferungen, Sonderwünsche, Story-Quests, Tagesaufgaben (sanft, ohne Streak-Strafe).
8. **Dorf/Stadt:** Dorfplatz, Café, Markt, Bibliothek, Museum (Dino/Fisch), Leuchtturm. Freischaltbar durch Beitrag.
9. **Handel (Spieler):** Marktstand mit Angeboten, Suche, Preise, Tauschhandel, Geschenke. Server-autoritativ.
10. **Soziales:** Freunde, Hof besuchen, beim Gießen/Füttern helfen, Gästebuch, Emotes, Chat (gefiltert), Nachbarschaften/Gilden mit gemeinsamen Zielen und Events.
11. **Sammlungen und Erfolge:** Fische, Dinos, Pflanzen, Dekos, Sticker, Titel.
12. **Events:** Saisonale (Erntefest, Winterlichter, Fischturnier), rein kosmetische und Sammel-Belohnungen.
13. **Fortschritt:** Level, Ruf pro NPC, Forschungsbaum (Komfort, keine Pflicht-Mauer).
14. **Komfort:** Cloud-Save, Mehrgeräte-Sync (Handy ↔ PC), Barrierefreiheit (Schriftgröße, Farbenblind-Modi, Bewegung reduzieren), Controller/Maus/Touch-Eingabe.

---

## 6. Multiplayer-Architektur und Sicherheit

- **Server-autoritativ** für: Währung, Handel, Gegenstände, IAP-Käufe, Belohnungen. Der Client schlägt vor, der Server validiert.
- **Lokal-autoritativ** für: reines Singleplayer-Farmen (zur Offline-Fähigkeit), mit **Sync-Reconciliation** und Plausibilitätsprüfungen (Zeitstempel, Raten), damit Manipulation nicht den Handel vergiftet.
- **Zeit:** Server-Zeit als Referenz gegen Uhr-Manipulation.
- **Besuch:** Asynchron (Snapshot des Hofs + einfache Interaktionen), kein Echtzeit-Netcode nötig, das spart Kosten und Latenz.
- **Chat:** Wortfilter, Melden/Blockieren, Moderationsqueue. Option: nur vordefinierte Phrasen/Emotes für junge Spieler.
- **Skalierung:** Start auf einem VPS, später horizontale Skalierung.

---

## 7. Monetarisierung (fair und cozy)

- **Rewarded Ads (freiwillig, nur auf Knopfdruck):**
  - **Smaragde:** max. 5 Werbungen/Tag → je 5 Smaragde (Limit serverseitig, Zähler setzt um Mitternacht zurück).
  - Produktion/Wachstum beschleunigen, Bonus-Lieferung, doppelte Belohnung (ebenfalls freiwillig, mit Tageslimit).
  - Keine Banner, keine Interstitials, kein Pop-up-Spam.
  - AdMob als "kinderfreundlich" markiert (Child-directed Treatment), nur nicht-personalisierte Werbung.
- **IAP:**
  - Kosmetik (Hof-Skins, Dekoration-Sets, Charakter-Outfits)
  - "Cozy Pass" (Abo oder einmalig): keine Werbung, mehr Lagerplatz, mehr Speicherplätze
  - Währungspakete (Edelsteine) nur für Komfort/Kosmetik
- **Modell ist Free-to-play** (entschieden). IAP/Cozy-Pass sind optional und erst ab Phase "Launch" möglich, weil die Store-Konten Geld kosten (siehe Abschnitt 9). Bis dahin: Smaragde nur durch Spielen und Werbung.
- **Regeln:** Kein Glücksspiel/Lootboxen, Preise transparent, Handel nicht durch Geld verzerrt (Ressourcen sind nicht für Echtgeld kaufbar).

---

## 8. Performance-Budget (iPhone 11, 60 FPS)

- Ziel-Frametime **≤ 16,6 ms**, besser ≤ 12 ms (Reserve für Thermal Throttling).
- **Draw Calls:** ≤ ~150 pro Frame (Atlanten, Batching, ein Material pro Ebene).
- **Sprites/Nodes sichtbar:** Culling außerhalb des Bildschirms, Chunking der Karte. Objekt-Pooling.
- **Texturen:** Atlanten ≤ 2048², komprimiert (ASTC iOS/Android, BPTC/S3TC Desktop). Gesamt-Textur-RAM ≤ ~300 MB.
- **RAM gesamt:** ≤ ~700 MB auf iPhone 11 (4 GB, System frisst viel).
- **Shader:** Wenige, einfache Fragment-Shader. Keine teuren Echtzeit-Schatten (Blob-Schatten als Sprite).
- **Simulation:** Zeitbasiert/event-basiert statt Tick pro Objekt. Nichts rechnet, wenn nichts sichtbar/aktiv ist.
- **Akku/Hitze:** Optionaler 30-FPS-Sparmodus, Pause bei Hintergrund.
- **Messung:** Automatisierte Benchmark-Szene (volle Farm, 200 Objekte), Profiling auf echten Geräten (iPhone 11, Mittelklasse-Android), Mindest-Gate in CI.
- **Android-Referenz:** Ca. Snapdragon 730 / 4 GB, z. B. Pixel 4a / Galaxy A52 als Untergrenze.

---

## 9. Plattformen und Release (Budget 0 €, ohne Mac)

**Entwicklung kostet nichts.** Godot, Python, SVG-Tools, GitHub, Supabase-Free-Tier und AdMob-Konto sind kostenlos. Geld verlangen nur die **Store-Konten zum Veröffentlichen**. Das ist die einzige harte Grenze:

| Plattform | Entwicklung/Test kostenlos | Veröffentlichung |
|---|---|---|
| **Windows** (Primärziel) | Ja, direkt hier | **itch.io: kostenlos.** Steam: 100 $ einmalig pro App. Microsoft Store: Konditionen prüfen |
| **Android** | Ja: APK per USB/Download auf das Gerät oder Emulator | Direkt-APK/itch.io kostenlos. **Google Play: 25 $ einmalig** |
| **iOS** | Teilweise: Build über **GitHub Actions macOS-Runner** (kostenlose Minuten, bei öffentlichem Repo großzügig, privat begrenzt). Installation auf deinem iPhone 11 mit kostenloser Apple-ID per **Sideloading** (AltStore/Sideloadly, Signatur läuft nach 7 Tagen ab) | **App Store: Apple Developer 99 $/Jahr, nicht umgehbar.** TestFlight braucht das Konto ebenfalls |

**Konsequenz für die Roadmap:**
- M0–M9 laufen komplett kostenlos: Windows-Builds, Android-APK, iPhone-11-Tests per Sideload.
- Der **Launch-Meilenstein (M10)** braucht Store-Gebühren. Erst Windows/itch.io + Android-APK kostenlos veröffentlichen, mit den Werbeeinnahmen (AdMob) und ersten Spielern später Google Play und App Store finanzieren. Oder die 124 $ (25 + 99) als einmalige Investition einplanen.
- **Das Wunsch-Ziel "auf allen drei Stores" ist ohne Geld nicht möglich.** Die Technik dafür bauen wir trotzdem von Anfang an ein.
- **Werbung/AdMob:** Das Konto ist kostenlos, Einnahmen gibt es erst, wenn die App öffentlich läuft. Auszahlung erst ab 70 € (AdMob-Schwelle), Steuerthema klären.
- **Eingabe:** Touch (Primär), Maus/Tastatur (Windows), Controller optional.
- **Android-Testgerät:** Fehlt noch. Kostenlose Alternative: Android-Emulator (liefert aber keine verlässlichen FPS-Werte). Notfalls Mittelklasse-Gerät von Freunden leihen.

---

## 10. Recht und Compliance (Deutschland/EU)

- **DSGVO:** Datenschutzerklärung, Einwilligungen, Datenlöschung ("Konto löschen" im Spiel), AVV mit Backend-Anbietern, Ad-Consent (Google UMP/CMP).
- **Impressum**, AGB, Widerrufsbelehrung für Käufe, Preisangaben.
- **Zielgruppe "Alle" = auch Kinder.** Daraus folgt:
  - **Kein freier Chat als Standard.** Standard sind vordefinierte Phrasen und Emotes. Freitext nur optional, gefiltert und erst ab Altersangabe 13+/16+ mit Elternhinweis.
  - **Altersabfrage** (neutral, ohne Hinweis auf "richtige" Antwort). Bei Kindern: keine personalisierte Werbung, wenig Datenerhebung, ggf. Einwilligung der Eltern (DSGVO Art. 8, in DE/AT meist 16 bzw. 14).
  - **Werbung:** AdMob "Child-directed", nur familiengeeignete Anzeigen, ausschließlich freiwillig (bereits so geplant).
  - **Keine Käufe ohne Hürde** (Eltern-Gate/Bestätigung bei IAP), keine Druck- oder Verknappungs-Mechaniken (passt zu "cozy").
  - **Soziales:** Besuche/Handel für Kinder nur mit Freunden per Freundescode, keine offene Suche nach fremden Spielern.
  - Altersfreigabe (USK/IARC-Fragebogen), COPPA (USA), Apple "Kids"-Regeln prüfen.
- **Lizenzen:** Nur selbst erzeugte Assets und frei lizenzierte Tools/SoundFonts mit dokumentierter Lizenz (`LICENSES.md`).
- **Marke/Name:** Recherche, bevor Branding gebaut wird. **Kein Hay-Day-Material**, auch keine Ähnlichkeit in Figuren/Namen/Icons.
- **Firma:** Ein Verkauf mit IAP ist gewerblich. Gewerbeanmeldung bzw. Steuerberatung klären (nicht Teil meiner Arbeit).

---

## 11. Projektstruktur (Repo)

```
mossglen/
  CLAUDE.md              # Brain-Regeln, wird von Claude Code automatisch geladen
  brain/                 # GOAL.md (dieser Plan), LOG, DECISIONS, taste/, references/
  .claude/skills/        # mossglen-art, mossglen-dev, vendor-Skills
  game/                  # Godot-Projekt
    scenes/ scripts/ shaders/ data/ i18n/ audio/ art/ fonts/
  tools/
    art/                 # Blender-Modelle (bpy) + Render/Pack -> Atlanten
    audio/               # Komposition/Synthese -> OGG
    balance/             # Balancing-Tabellen -> JSON
  server/                # Nakama-Module (Go/Lua/TS), Migrationen
  ci/                    # GitHub Actions, Build-Skripte
  docs/                  # Stil-Bibel, Design-Docs, Lizenzen
```

---

## 12. Roadmap (Meilensteine)

Jeder Meilenstein endet mit einem **spielbaren, getesteten Stand**.

| # | Meilenstein | Inhalt | Fertig, wenn … |
|---|---|---|---|
| **M0** | Fundament | Repo, Godot-Projekt, CI (Windows+Android-Build), **Stil-Bibel**, Asset-Pipeline-Prototyp (1 SVG → Atlas → Spiel), Audio-Pipeline-Prototyp, Benchmark-Szene | Ein Testgebäude samt Sound läuft auf Windows und Android mit 60 FPS |
| **M1** | Kern-Loop (Vertical Slice) | Schräg-Raster, Kamera (Zoom/Pan), Platzieren, Felder, 5 Pflanzen, Ernte, Inventar, Münzen, Tag/Nacht, Speichern lokal, UI-Grundset | 10 Min Spielspaß, cozy Look, stabil 60 FPS auf iPhone 11 |
| **M2** | Tiere und Produktion | 5 Tierarten, 8 Produktionsgebäude, Rezepte, Warteschlangen, Offline-Fortschritt, Aufträge (lokal) | Komplette Wirtschaftsschleife Feld → Tier → Produkt → Auftrag |
| **M3** | Angeln | Seen/Flüsse/Meer, Minispiel, Köder/Ruten, 40+ Fische, Album, Fischteich | Angeln komplett inkl. Sammlung und Sound |
| **M4** | Dinos | Urzeit-Tal, Ausgrabung, Ausbrüten, 10+ Dino-Arten, Dino-Pedia, Spezialprodukte | Dino-Loop komplett, Rigs animiert |
| **M5** | Dorf und Story | NPCs, Dialoge (DE/EN), Dorfgebäude, Story-Quests, Museum | Story-Bogen 1 spielbar |
| **M6** | Backend und Cloud | Nakama, Accounts, Cloud-Save, Mehrgeräte-Sync, Server-Zeit, Konto löschen | Spielstand wandert zwischen PC und Handy |
| **M7** | Soziales und Handel | Freunde, Besuch, Marktstand, Tausch, Geschenke, Chat, Nachbarschaften, Moderation | 2 Konten handeln und besuchen sich sicher |
| **M8** | Monetarisierung | AdMob-Rewarded, IAP (Win/Android/iOS), Cozy-Pass, Receipt-Validierung, Consent-Flow | Käufe und Werbung getestet in Sandbox |
| **M9** | Inhalt und Politur | Events, Jahreszeiten, Erfolge, Musik/SFX komplett, Barrierefreiheit, Balancing, Tutorial | Content-complete, FPS-Gate grün |
| **M10** | Beta und Launch | Geschlossene Beta (TestFlight/Play Internal/Steam), Crash-Fixing, Store-Seiten, Datenschutz/Impressum, Soft-Launch, Release | Veröffentlicht auf Steam + Google Play + App Store |
| **M11** | Live-Betrieb | Saison-Events, neue Inhalte, Community-Support, Telemetrie-Balancing | laufend |

**Reihenfolge-Prinzip:** Zuerst Spielgefühl und Look beweisen (M0–M1), dann Breite (M2–M5), dann Online (M6–M8), dann Politur und Launch. So scheitert das Projekt nicht erst am Ende.

---

## 13. Risiken und Gegenmaßnahmen

| Risiko | Gegenmaßnahme |
|---|---|
| Umfang ("alles gleichzeitig") ist riesig | Strikte Meilensteine, jeder Teil einzeln spielbar. Daten-getriebener Content |
| Selbst erzeugte Grafik wirkt zu "generisch" | Starke Stil-Bibel früh (M0), Austausch-Pipeline für spätere Illustratoren, Fokus auf Animation und Juice |
| Synthetische Musik wirkt flach | Hochwertige SoundFonts, adaptive Layer, später optional Komponist |
| 60 FPS auf iPhone 11 | Budget und Benchmark-Gate ab M0, Messungen auf echten Geräten |
| iOS ohne Mac | CI-macOS-Runner, TestFlight, Gerätefarm. Das Risiko liegt vor allem beim Signing und beim Test auf einem echten iPhone |
| Cheating im Handel | Server-autoritativ, Raten-Limits, Audit-Log |
| Rechtliches (DSGVO, Kinder, IAP) | Früh Checkliste (M6/M8), ggf. Anwalt für AGB/Datenschutz |
| Server-Kosten/Skalierung | Lean starten (VPS), Last-Tests vor Launch |
| Wirtschaftliches Risiko ("Hay Day"-Niveau braucht Marketing) | Soft-Launch, Wishlist auf Steam, Community früh aufbauen |

---

## 14. Entscheidungen und Restpunkte

Entschieden: Free-to-play, Zielgruppe alle, Budget 0 €, iPhone 11 vorhanden, Name Mossglen, Chibi-Dinos (siehe Abschnitt 0).

**Zusätzlich entschieden:**
1. **Launch-Reihenfolge:** Zuerst kostenlos (itch.io/Windows + Android-APK). **Ziel bleibt Google Play und Apple App Store** sobald Geld da ist (Werbeeinnahmen oder 124 $ einmalig). Die Technik (IAP, Signing, Store-Assets, Altersfreigabe) wird von Anfang an dafür vorbereitet.
2. **Kein Android-Testgerät.** Konsequenzen:
   - Android-Leistung wird über den **iPhone 11 als Referenz** (strenger als viele Android-Mittelklasse-Geräte), Godot-Profiler, ein **künstlich gedrosselter Android-Emulator** (CPU/GPU-Limit) und die niedrigste Qualitätsstufe abgesichert.
   - Zusätzlich: Performance-Budget bewusst **20–30 % unter dem Limit** halten, Qualitätsstufen (Niedrig/Mittel/Hoch) und 30-FPS-Sparmodus.
   - Vor Google-Play-Launch: Tester aus der Community (offener Test/itch.io) auf echten Geräten gewinnen.
3. **Öffentliches GitHub-Repo.** Folgen:
   - **Keine Geheimnisse im Repo:** Supabase-Service-Keys, AdMob-Schlüssel, Signing-Zertifikate, Passwörter gehören in GitHub Secrets/lokale `.env`-Dateien (in `.gitignore`).
   - Server-Logik für Handel/Währung läuft auf dem Server. Der Client-Code ist öffentlich einsehbar, daher darf **kein Client-seitiges Vertrauen** nötig sein (ohnehin so geplant).
   - Lizenz für den Code wählen (z. B. proprietär mit "All rights reserved" oder Source-available), damit niemand das Spiel einfach kopiert und verkauft. Assets (Grafik/Audio) separat lizenzieren.
   - Vorteil: kostenlose GitHub-Actions-Minuten inkl. macOS-Runner für iOS-Builds.

**Weiter offen:**
- **Steuer/Gewerbe** für Werbeeinnahmen klärst du selbst (keine Rechts-/Steuerberatung durch mich).
- **Code-Lizenz** für das öffentliche Repo (Vorschlag: "All rights reserved" für Code und Assets).

---

## 14b. M9.5 „Hay-Day-Qualität“ (nach Romans erstem Test, 2026-11-13) – beschlossen, Antworten in DECISIONS

Kommt **vor** M6. Ziel: Spielgefühl, Look und Progression auf Referenz-Niveau.

1. **Progression & Land:** leerer Starthof (Bauernhaus, Scheune, Silo, Auftragstafel + Lieferwagen, 3 Felder),
   der Rest der Karte liegt unter Bäumen, Büschen, Steinen und Zäunen in Parzellen. Hindernisse brauchen
   Werkzeug (Axt, Säge, Sprengstoff, Schaufel), Parzellen brauchen Erweiterungs-Material. Werkzeuge fallen
   zufällig beim Ernten/Herstellen/Liefern. Gebäude und Tiere schalten sich über Level frei, Felder kosten mehr.
2. **Lager:** Silo (nur Feldfrüchte) mit sichtbarem Füllstand am Gebäude, Scheune (Waren + Werkzeuge);
   beide Ausbau-Stufen mit eigenem Baumaterial.
3. **Lieferwagen:** Bestellung abgeben → Wagen fährt los, kommt mit Münzen-Kiste zurück, Antippen kassiert;
   während der Fahrt ist die Tafel gesperrt.
4. **Bedienung wie Hay Day:** Feld antippen → Saat-/Sichel-Kreis am Finger, gedrückt halten und über Felder
   ziehen; Hover-/Druck-Feedback an allem (Leuchtrand, Hüpfer, Klick-Sound); Blasen über Tieren stehen ruhig.
5. **Baustellen:** Gebäude erscheinen erst als Baustelle (Gerüst, Planen, Kisten), Bauzeit, dann Enthüllung.
6. **Tiere neu modelliert** auf Niveau `hd_animals_pets.png` (Unterteilungsflächen statt Metaballs,
   Augenlider, Glanz, Mimik, sauberes Rig), alle Tiere inkl. Dinos.
7. **Terrain neu** nach `hd_winter_farm.png`: Halm-Textur, hellere Flecken, Grasbüschel, Ränder, Felsen.
8. **Extras:** Besucher-Händler, Haustiere (Katze, Hund), Glücksrad (täglich), Helfer (für Tage anheuerbar).
9. **UI neu** mit festem Raster und gemessenen Abständen, Shop als Kartenliste mit Reitern und Laufleiste,
   Dialoge mit Figur + Sprechblase + großen Antwortknöpfen, Ladebildschirm.


**M9 Inhalt und Politur – fertig bis auf Gerätetest (2026-11-13)**
- Jahreszeiten nach echtem Kalender (Mär–Mai Frühling … Dez–Feb Winter): Boden-Tönung, Herbstlaub an Bäumen/Büschen,
  Schnee auf Wiese und Laub, fallende Blüten/Blätter/Flocken, Glühwürmchen in Sommernächten,
  je Saison eine Pflanze 20 % schneller (Erdbeere, Tomate, Mais, Karotte).
- 12 Erfolge mit Bronze/Silber/Gold, Smaragd-Belohnung, Pokal-Knopf mit Zähler.
- Musik: 4 Loops (Wiese, Nacht, Dorf, Urzeit-Tal) als Ogg, weiche Überblendung nach Ort und Tageszeit.
- Einstellungen neu: Musik, Geräusche, Weniger Bewegung, Größe der Anzeige (100/115/130 %), Sprache, Anleitung.
- Anleitung für neue Spieler (Zeigehand, 5 Schritte: säen, füttern, ernten, Auftragsbrett, Brumms Aufgabe).
- Leistung: Atlas-Seiten VRAM-komprimiert (BPTC/ASTC, ~150 MB → ~40 MB Grafikspeicher), Tipp-Masken statt
  Auslesen der Texturen.
- Saisonfeste (Blütenfest, Angelfest, Erntedankfest, Lichterwerkstatt): ein Ziel pro Jahreszeit, 3 Stufen mit
  Münzen/Smaragden, über die Saison-Plakette rechts oben.
- Balancing: alle Werkstatt-Rezepte mit mindestens ~4 Münzen Mehrwert pro Minute (vorher Kuhfutter im Minus,
  Kerzen/Stoff fast ohne Gewinn); Levelkurve quadratisch (Lv 2: 28 XP, Lv 5: 77, Lv 10: 220).
- Offen: FPS-Messung auf echtem iPhone 11 (braucht iOS-Build/Sideload), Romans Spielgefühl-Feedback.

**M5 Dorf und Story – fertig (2026-11-13)**
- Moosdorf mit 5 wiederaufbaubaren Gebäuden, 4 Bewohnern, Story-Bogen 1 (10 Quests), Dialoge DE/EN, Museum.

**M4 Dinos – fertig (2026-11-13)**
- Urzeit-Tal, Ausgraben, Brutnest, 10 Dino-Arten, Dino-Pedia, Farn als Futter, Urzeit-Ei + Bernstein als Spezialprodukte.

**M3 Angeln – fertig (2026-11-13)**
- Teich + Bach mit Stegen, entspanntes Timing-Minispiel ohne Scheitern, 40 Fischarten (Meer-Arten folgen mit
  dem Dorf), Ruten-Stufen, Fischalbum, Fische im Farmteich sichtbar, Platsch-/Rollen-Sounds.

**M2 Tiere und Produktion – fertig (2026-11-13)**
- 5 Tierarten: Hühner (Ei), Kühe (Milch), Schafe (Wolle), Schweine (Trüffel), Bienen (Honig, automatisch).
- 8 Produktionsgebäude + Bienenstock: Futtermühle, Bäckerei, Molkerei, Marmeladenküche, Webstuhl, Popcornwagen,
  Soßenküche, Kerzenzieherei (20 Rezepte), Warteschlangen, Offline-Fortschritt, Auftragstafel.

**M1 Kern-Loop (Vertical Slice) – fertig bis auf Gerätetest (2026-11-13, PC-Sitzung)**
- 5 Pflanzen (Weizen, Mais, Karotte, Tomate, Erdbeere) datengetrieben, je 4 Wachstumsstufen in 3D.
- Säen per Saat-Auswahl und Wischen, Ernten per Wischen, Lager (Scheune) mit Verkauf, Münzen, XP, Level,
  Freischaltung neuer Pflanzen.
- Bau-Modus: Felder kaufen und platzieren, Felder per langem Drücken verschieben.
- Tag/Nacht-Zyklus, lokales Speichern mit Offline-Wachstum, UI-Grundset in 2D (HUD, Panels, Knöpfe, Icons).
- Offen: „stabil 60 FPS auf iPhone 11“ messen (iOS-Build über CI), Romans Spielgefühl-Feedback.

**M0 Fundament – neu aufgebaut mit 3D-Grafik (2026-11-13, PC-Sitzung)**
- Grafik komplett auf Blender-Pre-Rendering umgestellt (siehe Abschnitt 3). Assets: Scheune, Feld,
  Weizen 4 Stufen, 7 Baumarten, Büsche, Steine mit Moos, 4 Blumenbeete, Zäune, Heu, Fass, Kiste, Trog,
  Huhn (Idle/Laufen/Picken, 2 Richtungen), Baby-Dino (Idle/Laufen), Icons (Münze, Smaragd, Stern, Weizen).
- Boden-Shader mit Gras/Erde und weichen Wegrändern. Neues HUD (Level, XP, Münzen, Smaragde, runde Knöpfe).
- Brain-Struktur (`CLAUDE.md`, `brain/`, Skills) angelegt.

**M0 erster Stand (2026-11-13, Laptop, SVG-Grafik – Grafik verworfen, Rest übernommen)**
- Godot 4.7.2 Projekt (`game/`), GL-Compatibility-Renderer für maximale Hardware-Abdeckung.
- Grafik-Pipeline `tools/art/` (SVG aus Code → Atlas + Bodenkacheln + UI), Stil-Bibel `docs/STYLE_BIBLE.md`.
- Audio-Pipeline `tools/audio/` (Musikloop "Meadow" 46 s + 7 Soundeffekte).
- Testfarm: säen/ernten per Wischen, Hühner, Scheune, Bäume mit Wind-Shader, Kamera mit Zoom/Pinch, HUD, DE/EN.
- Selbsttest `--smoke` grün. Benchmark `--bench` (363 Felder, 190 Objekte, 44 Hühner, max. Zoom-out): Ø 5,8 ms / p99 7,4 ms auf Intel Iris Xe.
- CI-Workflow (Windows-EXE + Android-APK) geschrieben, **noch nicht auf GitHub gelaufen**.
- Offen für M0: Test auf echtem iPhone 11 (iOS-Build über CI folgt), CI-Lauf prüfen.
