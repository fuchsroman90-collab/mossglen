"""Builds the Mossglen UI v2 layout mockups as one self-contained HTML file (for Figma + review).

Every `.screen` is one 1600x900 frame. All art is Mossglen's own (game renders and generated UI icons).
Run: python3 tools/ui_mockup/build.py <world_bg.png> <out.html>
"""
import base64
import io
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
UI = ROOT / "game/art/generated/ui"
CACHE = ROOT / "tools/art/.cache"


def b64(path, size=None, jpeg=False):
    im = Image.open(path)
    if size:
        im.thumbnail(size, Image.LANCZOS)
    buf = io.BytesIO()
    if jpeg:
        im.convert("RGB").save(buf, "JPEG", quality=82)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def ui(name, s=160):
    return b64(UI / f"{name}.png", (s, s))


def spr(name, s=300):
    return b64(CACHE / f"{name}.png", (s, s))


def main(bg_path, out):
    font = base64.b64encode((ROOT / "game/fonts/Fredoka.ttf").read_bytes()).decode()
    bg = b64(bg_path, (1600, 900), jpeg=True)
    I = {k: ui(k) for k in ["coin", "gem", "star", "ico_gear", "ico_shop", "ico_book", "ico_dino", "ico_trophy",
                             "ico_close", "ico_check", "ico_lock", "ico_barn", "ico_silo", "ico_plus",
                             "season_autumn", "tab_fields", "tab_buildings", "tab_animals", "item_axe",
                             "item_shovel", "item_saw", "item_dynamite", "item_nail", "item_hinge", "item_paint",
                             "item_egg", "item_milk", "item_bread", "item_wool", "item_honey", "item_wheat",
                             "item_stake", "item_land_map", "item_tape", "item_cheese", "item_butter"]}
    S = {k: spr(k) for k in ["chicken_idle_se_0", "cow_idle_se_0", "sheep_idle_se_0", "pig_idle_se_0",
                             "npc_lotte_0", "npc_brumm_0", "bakery", "feed_mill", "dairy"]}
    S["lotte_big"] = spr("npc_lotte_0", 520)

    def hud(dim=False):
        return f'''
<div class="hud{' dim' if dim else ''}">
  <div class="xp"><div class="xpbar"><div class="xpfill" style="width:38%"></div><span class="t s26">141 / 370</span></div>
    <img class="star" src="{I['star']}"><span class="t lvl">7</span></div>
  <div class="cur" style="top:22px"><img src="{I['coin']}"><span class="t s34">1.250</span><div class="plus">+</div></div>
  <div class="cur" style="top:96px"><img src="{I['gem']}"><span class="t s34">12</span><div class="plus">+</div></div>
</div>'''

    def rb(icon, x, y, size=104, extra="", badge=""):
        b = f'<span class="badge t s24">{badge}</span>' if badge else ""
        return (f'<div class="rb {extra}" style="left:{x}px;top:{y}px;width:{size}px;height:{size}px">'
                f'<img src="{I[icon]}">{b}</div>')

    def card(img, name, sub, price=None, count=None, locked=None):
        if locked:
            return (f'<div class="card locked"><img class="pic grey" src="{img}"><div class="t s32 nm">{name}</div>'
                    f'<div class="sub">Ab Level {locked}</div><img class="lk" src="{I["ico_lock"]}"></div>')
        c = f'<span class="t s28 cnt">{count}</span>' if count else ""
        return (f'<div class="card"><img class="pic" src="{img}">{c}<div class="t s32 nm">{name}</div>'
                f'<div class="sub">{sub}</div><div class="price"><img src="{I["coin"]}"><span class="t s30">{price}'
                f'</span></div></div>')

    def cell(item, n, sel=False):
        return (f'<div class="cell{" sel" if sel else ""}"><img src="{I[item]}"><span class="t s34 n">{n}</span></div>')

    def need(item, name, have, want):
        ok = have >= want
        mark = f'<img class="ok" src="{I["ico_check"]}">' if ok else '<span class="miss t s30">fehlt</span>'
        return (f'<div class="need"><img class="ni" src="{I[item]}"><div class="nn"><div class="d s26">{name}</div>'
                f'<div class="t s40{"" if ok else " red"}">{have}/{want}</div></div>{mark}</div>')

    screens = []

    # 1 ---------------------------------------------------------------- HUD
    screens.append(f'''
<div class="screen" data-name="01 HUD">{hud()}
  {rb('ico_gear', 24, 150, 84)}
  <div class="quest"><img src="{S['npc_brumm_0']}"><div><div class="d s22 b">Müller Brumm</div>
    <div class="d s20">Ernte 6 Weizen &nbsp;<b>2/6</b></div></div></div>
  <img class="season" src="{I['season_autumn']}">
  {rb('ico_book', 24, 772)}{rb('ico_dino', 144, 772)}{rb('ico_trophy', 264, 772, badge='2')}
  {rb('ico_shop', 1430, 730, 146, 'big')}
  <div class="note">HUD: Level + XP oben links (Leiste hängt an der Sternspitze) · Münzen/Smaragde oben rechts ·
   Aufgabe als Kärtchen · Sammlungen unten links · Laden groß unten rechts (Daumen)</div>
</div>''')

    # 2 ---------------------------------------------------------------- Shop
    cards = "".join([
        card(S["chicken_idle_se_0"], "Huhn", "Legt Eier in 20 Sek.", 10, "2/6"),
        card(S["cow_idle_se_0"], "Kuh", "Gibt Milch in 1 Min.", 60, "1/5"),
        card(S["sheep_idle_se_0"], "Schaf", "", locked=5),
        card(S["pig_idle_se_0"], "Schwein", "", locked=6),
        card(S["bakery"], "Bäckerei", "Backt Brot und Kuchen", 120),
        card(S["dairy"], "Molkerei", "", locked=3),
    ])
    screens.append(f'''
<div class="screen" data-name="02 Laden">{hud(True)}
  <div class="shoptitle t s48">Tiere</div>
  <div class="tabs"><div class="tab"><img src="{I['tab_fields']}"></div><div class="tab"><img src="{I['tab_buildings']}"></div>
    <div class="tab on"><img src="{I['tab_animals']}"></div></div>
  <div class="closeb" style="right:24px;top:170px"><img src="{I['ico_close']}"></div>
  <div class="shopbar"><div class="cards">{cards}</div><div class="scroll"><i></i></div></div>
  <div class="note" style="bottom:auto;top:250px">Laden: Reiter oben, Karten unten, die Farm bleibt sichtbar ·
   gelb = kaufbar, grau + Schloss = gesperrt · Zähler „2/6“ · Laufleiste zeigt die Position</div>
</div>''')

    # 3 ---------------------------------------------------------------- Storage
    grid = "".join([cell("item_axe", 3, True), cell("item_shovel", 2), cell("item_saw", 1), cell("item_dynamite", 4),
                    cell("item_egg", 12), cell("item_milk", 6), cell("item_bread", 3), cell("item_wool", 2),
                    cell("item_honey", 1), cell("item_nail", 2), cell("item_hinge", 1), cell("item_paint", 0)])
    screens.append(f'''
<div class="screen" data-name="03 Scheune">{hud(True)}<div class="shade"></div>
  <div class="win" style="left:210px;top:120px;width:1180px;height:700px">
    <div class="ribbon t s40">Scheune</div><div class="closeb" style="right:-26px;top:-26px"><img src="{I['ico_close']}"></div>
    <div class="zone cream" style="left:36px;top:70px;width:640px;height:594px">
      <div class="zt d s22 b">INHALT</div><div class="grid">{grid}</div></div>
    <div class="zone orange" style="left:700px;top:70px;width:444px;height:330px">
      <div class="zt d s22 b">VERKAUFEN</div>
      <div class="selrow"><img src="{I['item_axe']}"><div><div class="d s34 b">Axt</div>
        <div class="pr"><img src="{I['coin']}"><span class="t s30">15</span><span class="d s22">&nbsp;pro Stück</span></div></div></div>
      <div class="btnrow"><div class="btn green t s28">1 verkaufen</div><div class="btn green t s28">Alle (3)</div></div></div>
    <div class="zone blue" style="left:700px;top:424px;width:444px;height:240px">
      <div class="zt d s22 b">LAGERPLATZ</div>
      <div class="caprow"><img src="{I['ico_barn']}"><div style="flex:1"><div class="t s34">37 / 50</div>
        <div class="bar"><i style="width:74%"></i></div></div></div>
      <div class="btn yellow t s28" style="margin:18px auto 0;width:300px">Scheune ausbauen</div></div>
  </div>
  <div class="note">Scheune: drei klar getrennte Bereiche – Inhalt (creme), Verkaufen (orange, nur die gewählte Ware),
   Lagerplatz/Ausbauen (blau, betrifft das Gebäude)</div>
</div>''')

    # 4 ---------------------------------------------------------------- Upgrade dialog
    screens.append(f'''
<div class="screen" data-name="04 Ausbau">{hud(True)}<div class="shade"></div>
  <div class="win" style="left:480px;top:110px;width:640px;height:720px">
    <div class="ribbon blue t s40">Scheune ausbauen</div><div class="closeb" style="right:-26px;top:-26px"><img src="{I['ico_close']}"></div>
    <div class="capbig"><img src="{I['ico_barn']}"><span class="t s48">50</span><span class="arrow t s48">➜</span><span class="t s48 grn">75</span></div>
    <div class="d s24 ctr">Du brauchst dafür:</div>
    <div class="needs">{need('item_nail', 'Nagel', 2, 1)}{need('item_hinge', 'Scharnier', 1, 1)}{need('item_paint', 'Farbeimer', 0, 1)}</div>
    <div class="rb confirm off" style="left:262px;top:590px;width:116px;height:116px"><img src="{I['ico_check']}"></div>
  </div>
  <div class="note">Ausbau: eigener Dialog mit blauem Titel · Liste Material x/y mit Haken ·
   runder Bestätigen-Knopf (grau, solange etwas fehlt)</div>
</div>''')

    # 5 ---------------------------------------------------------------- NPC trade dialog
    screens.append(f'''
<div class="screen" data-name="05 Besucher">{hud(True)}<div class="shade"></div>
  <img class="npcbig" src="{S['lotte_big']}">
  <div class="bubble" style="left:560px;top:150px;width:760px">
    <div class="d s34 b ctr">Schönes Wetter! Hast du Eier für mich?</div>
    <div class="offer"><span class="t s48">6</span><img src="{I['item_egg']}"><span class="t s48 arrow">➜</span>
      <img src="{I['coin']}"><span class="t s48">50</span></div>
    <div class="d s24 ctr">Du hast: <b>12</b> Eier</div></div>
  <div class="answers" style="left:640px;top:480px;width:600px">
    <div class="btn green t s32 wide">Ja, bitte sehr!</div><div class="btn yellow t s32 wide">Nein, leider nicht</div>
    <div class="btn yellow t s32 wide">Warte einen Moment</div></div>
  <div class="note">Besucher-Händler: Figur groß links, Sprechblase mit Angebot, drei große Antwort-Knöpfe</div>
</div>''')

    # 6 ---------------------------------------------------------------- Land popup
    screens.append(f'''
<div class="screen" data-name="06 Neues Land">{hud(True)}<div class="shade"></div>
  <div class="win" style="left:400px;top:120px;width:800px;height:680px">
    <div class="ribbon green t s40">Neues Land</div><div class="closeb" style="right:-26px;top:-26px"><img src="{I['ico_close']}"></div>
    <div class="landpic"><img class="lockbig" src="{I['ico_lock']}"></div>
    <div class="d s26 ctr" style="margin-top:14px">Dieses Stück Land gehört dir für:</div>
    <div class="needs row">{need('item_stake', 'Grenzpflock', 1, 1)}{need('item_land_map', 'Landkarte', 1, 1)}{need('item_tape', 'Maßband', 0, 1)}</div>
    <div class="btn green t s34" style="margin:22px auto 0;width:360px"><img src="{I['coin']}" style="width:44px;margin-right:10px">250 &nbsp;Kaufen</div>
  </div>
  <div class="note">Pop-up „Neues Land“: Bild vom Grundstück mit Schloss, was man braucht, ein klarer Kauf-Knopf</div>
</div>''')

    # 7 ---------------------------------------------------------------- Loading
    screens.append(f'''
<div class="screen load" data-name="07 Laden-Bildschirm">
  <div class="cloud" style="left:120px;top:120px"></div><div class="cloud" style="left:1150px;top:90px;transform:scale(1.3)"></div>
  <div class="cloud" style="left:700px;top:330px;transform:scale(.8)"></div>
  <div class="logo"><span>Moss</span><span class="l2">glen</span></div>
  <div class="hill"></div><div class="hill h2"></div>
  <img class="lh" src="{S['chicken_idle_se_0']}"><img class="ls" src="{S['sheep_idle_se_0']}"><img class="lc" src="{S['cow_idle_se_0']}">
  <div class="loadbar"><i style="width:62%"></i><span class="t s30">Lädt …</span></div>
  <div class="t s26 tip">Tipp: Mit Axt und Säge räumst du Bäume von deinem Land.</div>
</div>''')

    css = '''
@font-face{font-family:Fredoka;src:url(data:font/ttf;base64,@FONT@);font-weight:300 700}
*{box-sizing:border-box;margin:0;padding:0}
body{background:#2b2b2b;font-family:Fredoka,sans-serif;font-weight:600;padding:20px}
.screen{position:relative;width:1600px;height:900px;overflow:hidden;margin-bottom:40px;background:url(@BG@) center/cover}
.t{color:#fff;-webkit-text-stroke:7px #5A3410;paint-order:stroke fill;font-weight:700;letter-spacing:.5px;line-height:1.05}
.d{color:#5A3410}.b{font-weight:700}.ctr{text-align:center}.red{color:#FF8A7A}.grn{color:#B6F27A}
.s20{font-size:20px}.s22{font-size:22px}.s24{font-size:24px}.s26{font-size:26px}.s28{font-size:28px}.s30{font-size:30px}
.s32{font-size:32px}.s34{font-size:34px}.s40{font-size:40px}.s48{font-size:48px}
.s24.t,.s26.t,.s28.t,.s30.t{-webkit-text-stroke-width:6px}
.dim{opacity:.55}.shade{position:absolute;inset:0;background:rgba(40,25,5,.45)}
.note{position:absolute;left:400px;right:400px;bottom:16px;background:rgba(20,30,40,.82);color:#fff;font-weight:500;
 font-size:17px;line-height:1.3;padding:8px 14px;border-radius:10px;text-align:center}
/* HUD */
.xp{position:absolute;left:20px;top:16px;width:430px;height:104px}
.xpbar{position:absolute;left:78px;top:30px;width:340px;height:46px;border-radius:23px;background:#2A3F6E;border:5px solid #fff;
 box-shadow:0 0 0 4px #5A3410;display:flex;align-items:center;justify-content:center}
.xpfill{position:absolute;left:0;top:0;bottom:0;border-radius:18px;background:linear-gradient(#8ED6FF,#3D8FE0)}
.xpbar span{position:relative}
.star{position:absolute;left:0;top:0;width:104px}.lvl{position:absolute;left:0;width:104px;top:32px;text-align:center;font-size:44px}
.cur{position:absolute;right:20px;height:60px;min-width:230px;border-radius:30px;background:rgba(60,36,10,.82);border:4px solid #fff;
 box-shadow:0 0 0 4px #5A3410;display:flex;align-items:center;justify-content:flex-end;padding:0 64px 0 70px}
.cur img{position:absolute;left:-12px;top:-10px;width:72px}
.plus{position:absolute;right:-8px;top:-8px;width:68px;height:68px;border-radius:50%;background:linear-gradient(#B6F27A,#3FA535);
 border:4px solid #fff;box-shadow:0 0 0 4px #5A3410;color:#fff;font-size:44px;line-height:54px;text-align:center;font-weight:700}
.rb{position:absolute;border-radius:50%;background:linear-gradient(#FFE97A,#F7A91E);border:6px solid #FFF8DC;
 box-shadow:0 0 0 5px #5A3410,0 8px 0 5px rgba(60,36,10,.35);display:flex;align-items:center;justify-content:center}
.rb img{width:66%}.rb.big img{width:70%}
.rb.confirm{background:linear-gradient(#B6F27A,#3FA535)}.rb.off{background:linear-gradient(#E4DAC4,#B8AA8C)}
.badge{position:absolute;right:-10px;top:-12px;min-width:44px;height:44px;border-radius:22px;background:#E8402E;border:4px solid #fff;
 box-shadow:0 0 0 3px #5A3410;text-align:center;line-height:36px;-webkit-text-stroke-width:4px}
.quest{position:absolute;left:124px;top:150px;height:84px;padding:6px 22px 6px 8px;border-radius:20px;background:#FFF6DC;
 border:5px solid #E9B24A;box-shadow:0 0 0 4px #5A3410;display:flex;align-items:center;gap:10px}
.quest img{height:68px}.season{position:absolute;right:26px;top:176px;width:76px}
/* shop */
.shoptitle{position:absolute;left:0;right:0;top:20px;text-align:center}
.tabs{position:absolute;left:0;right:0;top:86px;display:flex;justify-content:center;gap:10px}
.tab{width:116px;height:104px;border-radius:20px;background:linear-gradient(#F7C24A,#E8962A);border:5px solid #FFF8DC;
 box-shadow:0 0 0 4px #5A3410;display:flex;align-items:center;justify-content:center;opacity:.85}
.tab img{width:92px;mix-blend-mode:multiply}.tab.on{background:linear-gradient(#FFF2A0,#FFD23F);transform:translateY(8px) scale(1.08);opacity:1}
.closeb{position:absolute;width:76px;height:76px;border-radius:50%;background:linear-gradient(#FF8A6A,#D92B2B);border:5px solid #fff;
 box-shadow:0 0 0 5px #5A3410;display:flex;align-items:center;justify-content:center}.closeb img{width:60%}
.shopbar{position:absolute;left:0;right:0;bottom:0;height:400px;padding:0 24px}
.cards{display:flex;gap:14px;height:372px}
.card{position:relative;flex:0 0 246px;height:364px;border-radius:22px;background:linear-gradient(#FFE97A,#F7A91E);
 border:5px solid #FFF8DC;box-shadow:0 0 0 4px #5A3410,0 8px 0 4px rgba(60,36,10,.3);text-align:center;padding-top:12px}
.card .pic{height:150px;max-width:210px;object-fit:contain}.card .nm{margin-top:6px}
.card .sub{font-size:19px;color:#7A4A12;height:46px;padding:4px 14px;line-height:1.15}
.card .cnt{position:absolute;right:14px;top:128px}
.price{margin:2px auto 0;width:180px;height:56px;border-radius:28px;background:linear-gradient(#B6F27A,#3FA535);border:4px solid #fff;
 box-shadow:0 0 0 4px #5A3410;display:flex;align-items:center;justify-content:center;gap:8px}.price img{width:40px}
.card.locked{background:linear-gradient(#C9D2DA,#8E9AA6)}.grey{filter:grayscale(1) brightness(.75);opacity:.8}
.card.locked .sub{color:#fff}.lk{width:60px;margin-top:0}
.scroll{height:10px;border-radius:5px;background:rgba(60,36,10,.55);margin-top:6px}.scroll i{display:block;width:34%%;height:100%%;border-radius:5px;background:#FFF8DC}
/* windows */
.win{position:absolute;border-radius:36px;background:#FFF6DC;border:12px solid #E9A23A;box-shadow:0 0 0 5px #5A3410,0 14px 0 5px rgba(40,25,5,.35)}
.ribbon{position:absolute;left:50%%;top:-44px;transform:translateX(-50%%);min-width:360px;height:76px;padding:0 40px;border-radius:22px;
 background:linear-gradient(#F7B24A,#D9822A);border:5px solid #FFE9B0;box-shadow:0 0 0 5px #5A3410;display:flex;align-items:center;justify-content:center;white-space:nowrap}
.ribbon.blue{background:linear-gradient(#7CC4FF,#3D8FE0);border-color:#D6EEFF}.ribbon.green{background:linear-gradient(#B6F27A,#3FA535);border-color:#E4FFC4}
.zone{position:absolute;border-radius:24px;border:5px solid;padding:44px 18px 18px}
.zt{position:absolute;left:22px;top:10px;letter-spacing:2px;opacity:.75}
.zone.cream{background:#FBE9BE;border-color:#E2C078}.zone.orange{background:#FFD9A0;border-color:#F09A2E}.zone.blue{background:#CFE9FF;border-color:#4C9BE0}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.cell{position:relative;height:166px;border-radius:22px;background:#F3D9A2;display:flex;align-items:center;justify-content:center}
.cell.sel{background:linear-gradient(#FFF2A0,#FFD23F);box-shadow:0 0 0 5px #F09A2E}
.cell img{width:120px}.cell .n{position:absolute;right:10px;bottom:6px}
.selrow{display:flex;align-items:center;gap:18px;margin:6px 8px 18px}.selrow img{width:120px}
.pr{display:flex;align-items:center;gap:6px;margin-top:6px}.pr img{width:40px}
.btnrow{display:flex;gap:14px;justify-content:center}
.btn{height:68px;padding:0 26px;border-radius:34px;border:5px solid #fff;box-shadow:0 0 0 4px #5A3410,0 6px 0 4px rgba(60,36,10,.3);
 display:flex;align-items:center;justify-content:center;white-space:nowrap}
.btn.green{background:linear-gradient(#B6F27A,#3FA535)}.btn.yellow{background:linear-gradient(#FFE97A,#F7A91E)}.btn.wide{width:100%%;height:80px;margin-bottom:22px}
.caprow{display:flex;align-items:center;gap:14px;margin:0 8px}.caprow img{width:84px}
.bar{height:30px;border-radius:15px;background:#2A3F6E;border:4px solid #fff;box-shadow:0 0 0 3px #5A3410;margin-top:8px;overflow:hidden}
.bar i{display:block;height:100%%;background:linear-gradient(#8ED6FF,#3D8FE0)}
.capbig{display:flex;align-items:center;justify-content:center;gap:18px;margin:56px 0 12px}.capbig img{width:96px}
.needs{margin:14px 60px 0}.need{display:flex;align-items:center;gap:18px;height:116px;border-bottom:4px dashed #E2C078}
.need:last-child{border:0}.ni{width:100px}.nn{flex:1}.ok{width:64px;height:64px;padding:8px;border-radius:50%%;background:linear-gradient(#B6F27A,#3FA535);box-shadow:0 0 0 4px #5A3410}.miss{-webkit-text-stroke-width:5px;color:#FF8A7A}
.needs.row{display:flex;gap:10px;margin:10px 30px 0}.needs.row .need{flex:1;flex-direction:column;height:auto;border:0;gap:2px;background:#FBE9BE;border-radius:20px;padding:10px}
.needs.row .nn{text-align:center}.needs.row .ok{width:44px;height:44px;padding:6px}
.landpic{margin:56px auto 0;width:660px;height:230px;border-radius:24px;border:5px solid #5A3410;background:url(@BG@) 30%% 20%%/1500px;position:relative}
.landpic:after{content:"";position:absolute;inset:0;border-radius:18px;background:rgba(30,50,20,.45)}
.lockbig{position:absolute;left:50%%;top:50%%;width:120px;transform:translate(-50%%,-50%%);z-index:2}
.npcbig{position:absolute;left:150px;top:250px;height:600px}
.bubble{position:absolute;border-radius:36px;background:#FFFDF4;border:6px solid #5A3410;padding:28px 30px 22px}
.bubble:before{content:"";position:absolute;left:-44px;top:150px;border:24px solid transparent;border-right:40px solid #5A3410}
.bubble:after{content:"";position:absolute;left:-30px;top:156px;border:18px solid transparent;border-right:32px solid #FFFDF4}
.offer{display:flex;align-items:center;justify-content:center;gap:14px;margin:16px 0 8px;background:#FBE9BE;border-radius:22px;padding:8px}
.offer img{width:92px}.arrow{color:#FFD23F}
.answers{position:absolute}
/* loading */
.load{background:linear-gradient(#6EC3FF,#C8ECFF 62%%,#C8ECFF)}
.cloud{position:absolute;width:300px;height:90px;border-radius:50px;background:#fff;opacity:.9}
.cloud:before{content:"";position:absolute;left:50px;top:-50px;width:130px;height:130px;border-radius:50%%;background:#fff}
.cloud:after{content:"";position:absolute;left:150px;top:-30px;width:100px;height:100px;border-radius:50%%;background:#fff}
.logo{position:absolute;left:0;right:0;top:130px;text-align:center;font-size:190px;font-weight:700;color:#8EDB4A;-webkit-text-stroke:22px #2E5A1A;
 paint-order:stroke fill;letter-spacing:2px;line-height:1;transform:rotate(-3deg)}.logo .l2{color:#FFD23F}
.hill{position:absolute;left:-200px;right:-200px;bottom:-560px;height:900px;border-radius:50%%;background:linear-gradient(#A8E05A,#6BBF3A)}
.hill.h2{left:500px;right:-600px;bottom:-640px;background:linear-gradient(#8ED44A,#58A830)}
.lh{position:absolute;left:330px;bottom:190px;height:150px}.ls{position:absolute;left:1090px;bottom:200px;height:170px}.lc{position:absolute;left:560px;bottom:230px;height:190px;transform:scaleX(-1)}
.loadbar{position:absolute;left:450px;right:450px;bottom:104px;height:60px;border-radius:30px;background:#2A3F6E;border:6px solid #fff;
 box-shadow:0 0 0 5px #5A3410;overflow:hidden;display:flex;align-items:center;justify-content:center}
.loadbar i{position:absolute;left:0;top:0;bottom:0;background:linear-gradient(#FFE97A,#F7A91E)}.loadbar span{position:relative}
.tip{position:absolute;left:0;right:0;bottom:44px;text-align:center}
'''.replace('%%', '%').replace('@FONT@', font).replace('@BG@', bg)
    html = f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{"".join(screens)}</body></html>'
    Path(out).write_text(html, encoding="utf-8")
    print(len(html) // 1024, "KB,", len(screens), "screens")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
