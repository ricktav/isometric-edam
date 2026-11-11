"""Edam van toen: a guided tour along the town's history, as an overlay for the viewer.

Texts are written for this map from Dutch Wikipedia (Edam, Speeltoren, Grote of Sint-Nicolaaskerk, Raadhuis van Edam,
Edams Museum, Kaasmarkt, Fort bij Edam, Trijntje Keever) and the Rijksmonumentenregister; every stop links to its
story there. Photos are Wikimedia Commons files with an open license (checked file by file); they are downloaded once
and published with the site, with credits.

Output: data/build/history.json and data/build/history/*.jpg
"""

import hashlib
import json
import re
import subprocess
import time
import urllib.parse
import urllib.request

from config import BUILD, CX, CY
from geo import wgs_to_rd

WP = "https://nl.wikipedia.org/wiki/"
WIKI = lambda page: ("Wikipedia: " + page.replace("_", " ").split(" (")[0], WP + page)
RM = lambda n: ("Rijksmonumentenregister", f"https://monumentenregister.cultureelerfgoed.nl/monumenten/{n}")

STOPS = [
    {
        "year": "ca. 1230",
        "title": "Een dam in de IJe",
        "at": (132058, 502806),
        "zoom": 0.3,
        "text": "Edam begint als een dam in het veenriviertje de IJe, ook wel de E, dat hier in de Zuiderzee uitmondde. Rond 1230 worden de zeegaten in Waterland afgedamd, en bij de dam groeit een nederzetting van vissers en handelaars: IJedam, later Edam.",
        "source": WIKI("Edam"),
        "more": WP + "Edam",
    },
    {
        "year": "1310",
        "title": "De Speeltoren",
        "at": (131901, 502795),
        "h": 20,
        "text": "De oudste kern van het stadje ligt rond de Onze-Lieve-Vrouwekerk, de Kleine Kerk, gesticht in 1310. De kerk werd in 1883 afgebroken; alleen de toren met zijn 16e-eeuwse achtkante lantaarn bleef staan. Bij werk in 1972 dreigde hij om te vallen en werd hij gestut, maar sindsdien staat hij scheef. Het carillon speelt elk kwartier.",
        "photos": [
            ("Edam_023.JPG", "De Speeltoren in 2012, Microtoerisme, CC BY-SA 3.0"),
            ("Speeltoren_Edam_door_Hendrik_Tavenier.jpg", "De Speeltoren en de Kleine Kerk rond 1790, Hendrik Tavenier (publiek domein)"),
        ],
        "source": WIKI("Speeltoren_(Edam)"),
        "more": WP + "Speeltoren_(Edam)",
    },
    {
        "year": "1357",
        "title": "Voorhaven en Oorgat",
        "at": (133434, 503192),
        "zoom": 0.6,
        "text": "In 1357 krijgt Edam stadsrechten van graaf Willem V, met het recht om twee nieuwe havens naar zee te graven: de Voorhaven en het Oorgat. Scheepsbouw, haringvisserij en kaashandel brengen het stadje in de eeuwen daarna tot bloei. In 1544 beveelt Karel V de open verbinding met de Zuiderzee te sluiten; in 1570 slaan de Edammers de sluisdeuren weer kapot.",
        "source": WIKI("Edam"),
        "more": WP + "Edam",
    },
    {
        "year": "15e eeuw",
        "title": "De Grote Kerk",
        "at": (131956, 503137),
        "h": 15,
        "text": "In de nieuwe stadsuitbreiding aan de noordkant verrijst in de 15e eeuw de Grote of Sint-Nicolaaskerk, een van de grootste hallenkerken van het land. Na een brand in 1602 komen er de beroemde gebrandschilderde ramen, geschonken door steden en rijke families. In 1699 slaat de bliksem in de torenspits; de toren bleef daarna laag.",
        "photos": [
            ("Edam_-_SInt-Nicolaaskeerk_011.jpg", "De Grote Kerk in 2022, P. Hughes, CC BY 4.0"),
            ("Edam_Grote_of_Sint-Nicolaaskerk.jpg", "De Grote Kerk in 2010, Arch (publiek domein)"),
        ],
        "source": WIKI("Grote_of_Sint-Nicolaaskerk_(Edam)"),
        "more": WP + "Grote_of_Sint-Nicolaaskerk_(Edam)",
    },
    {
        "year": "1526",
        "title": "De Kaasmarkt",
        "at": (131950, 502940),
        "text": "Op 16 april 1526 geeft Karel V Edam het recht op een vrije weekmarkt en een waag. In 1574 maakt Willem van Oranje dat waagrecht eeuwigdurend, als dank voor de hulp bij het ontzet van Alkmaar. Eeuwenlang wordt hier Edammer kaas verhandeld, tot 1922. Sinds 1989 is er in juli en augustus elke woensdagochtend weer een kaasmarkt, met kaasdragers en kaasmeisjes.",
        "photos": [
            ("Kaasmarkt_Edam.jpg", "Kaasmarkt in Edam, 2006, Lupo, CC BY-SA 3.0"),
            ("Kaaswaag_Edam.JPG", "De Kaaswaag uit 1778, Marion Golsteijn, CC BY-SA 3.0 NL"),
        ],
        "source": WIKI("Kaasmarkt_(Edam)"),
        "more": WP + "Kaasmarkt_(Edam)",
    },
    {
        "year": "ca. 1540",
        "title": "Het Steenen Coopmanshuys",
        "at": (132046, 502828),
        "h": 8,
        "text": "Het oudste stenen huis van Edam, gebouwd rond 1540 voor een koopman, heeft een kelder die los van het huis op het grondwater drijft en meebeweegt met het peil. De gemeente kocht het huis in 1893 op een veiling, liet het door Pierre Cuypers restaureren en opende er in 1895 het Edams Museum. In 1962 stond het model voor het Delfts blauwe huisje van de KLM.",
        "photos": [
            ("Edam_-_Damplein_8jpg.jpg", "Het Steenen Coopmanshuys in 2010, Arch (publiek domein)"),
            ("Edams_Museum_(1530)_-_Interior_view_of_the_unique_floating_cellar.jpg", "De drijvende kelder in 2020, Txllxt TxllxT, CC BY-SA 4.0"),
        ],
        "source": WIKI("Edams_Museum"),
        "more": WP + "Edams_Museum",
    },
    {
        "year": "1555",
        "title": "Het Proveniershuis",
        "at": (131888, 503076),
        "h": 6,
        "text": "In 1555 gesticht als tehuis voor ouderen die zich met geld of goed inkochten, de proveniers. De huidige gebouwen aan de J.C. Brouwersgracht zijn 17e- en 18e-eeuws en staan rond een stille binnentuin.",
        "photos": [("Proveniershuis_JC_Brouwersgracht_30_Edam_Rijksmonument_14292.jpg", "Het Proveniershuis in 2017, Edithnib, CC BY-SA 3.0 NL")],
        "source": RM(14292),
        "more": "https://monumentenregister.cultureelerfgoed.nl/monumenten/14292",
    },
    {
        "year": "1616",
        "title": "Trijntje Keever, het Groote Meisje",
        "at": (131956, 503137),
        "h": 15,
        "text": "Trijntje Cornelisdochter Keever wordt in april 1616 in Edam geboren en groeit uit tot mogelijk de langste vrouw die ooit heeft geleefd: 2,54 meter. Haar ouders laten haar op kermissen zien. Ze sterft in 1633, zeventien jaar oud, en wordt in de Grote Kerk begraven. Haar levensgrote portret hangt in het Edams Museum.",
        "photos": [("Trijntje_Keever.jpg", "Trijntje Keever, portret uit 1633 (publiek domein)")],
        "source": WIKI("Trijntje_Keever"),
        "more": WP + "Trijntje_Keever",
    },
    {
        "year": "1737",
        "title": "Het Raadhuis",
        "at": (132076, 502789),
        "h": 8,
        "text": "Op 18 mei 1737 legt Roelof Boot de eerste steen van het nieuwe stadhuis aan het Damplein, ontworpen door Jacob Jongh in Lodewijk XIV-stijl, met een zandstenen ingang onder het stadswapen. Binnen hangt nog het beschilderde behang van Willem Rave uit 1738. Nu zit de VVV beneden en trouwt Edam er nog steeds.",
        "photos": [("Edam,_Holland_5.jpg", "Het Raadhuis in 2005, stevekc, CC BY 2.0")],
        "source": WIKI("Raadhuis_van_Edam"),
        "more": WP + "Raadhuis_van_Edam",
    },
    {
        "year": "1740",
        "title": "De Lutherse kerk",
        "at": (132105, 502808),
        "h": 8,
        "text": "Aan de Voorhaven bouwen de lutheranen in 1739-1741 hun eigen kerk, met gevels in Lodewijk XIV-stijl. Het is een van de 176 rijksmonumenten van Edam.",
        "photos": [("Edam,_Evangelisch_Lutherse_kerk.jpg", "De Lutherse kerk in 2010, Arch (publiek domein)")],
        "source": RM(14421),
        "more": "https://monumentenregister.cultureelerfgoed.nl/monumenten/14421",
    },
    {
        "year": "18e eeuw",
        "title": "De Kwakelbrug",
        "at": (131930, 502590),
        "text": "Een smal houten ophaalbruggetje, een kwakel, over het water bij het Doelland. De brug is een rijksmonument en een van de meest gefotografeerde plekjes van het stadje.",
        "photos": [("Kwakelbrug.JPG", "De Kwakelbrug in 2011, Marion Golsteijn, CC BY-SA 3.0 NL")],
        "source": RM(14379),
        "more": "https://monumentenregister.cultureelerfgoed.nl/monumenten/14379",
    },
    {
        "year": "1795",
        "title": "De Damsluis",
        "at": (132066, 502811),
        "text": "Onder het Damplein ligt de Damsluis uit 1795-1798, die het water van de Voorhaven scheidt van de grachten en de polders. Tot ver in de 19e eeuw kon de Zuiderzee bij hoog water tot hier het grondwater opstuwen.",
        "photos": [("Damsluis_Edam.jpg", "De Damsluis in 2011, Marion Golsteijn, CC BY-SA 3.0")],
        "source": RM(14401),
        "more": "https://monumentenregister.cultureelerfgoed.nl/monumenten/14401",
    },
    {
        "year": "1835",
        "title": "De vesting",
        "at": (131800, 503260),
        "zoom": 0.6,
        "text": "Edam was een vestingstadje: de Wester- en Noordervesting met hun wallen en de singelgracht zijn er nog. De Purmerpoort, de stadspoort aan de westkant, werd in 1835 afgebroken. De meermin van Edam, het beeld dat de poort sierde, is nu te zien in het Edams Museum.",
        "photos": [("Edam,_Omwalling_van_voormalige_Wester-,_Noordervesting.jpg", "De wal van de Noordervesting in 2011, M.arjon, CC BY-SA 3.0 NL")],
        "source": WIKI("Edams_Museum"),
        "more": WP + "Edams_Museum",
    },
    {
        "year": "1913",
        "title": "Het Fort bij Edam",
        "at": (133293, 503416),
        "h": 4,
        "zoom": 0.6,
        "text": "Het laatste fort van de Stelling van Amsterdam, gebouwd in 1908-1913 bij het Oorgat om de zeedijk en de sluis te dekken. In de Eerste Wereldoorlog was het bemand, in de Tweede gebruikte de Wehrmacht het, en tot 1980 lagen er wapens en munitie. Sinds 2005 houdt een stichting het open; de Stelling is werelderfgoed.",
        "photos": [
            ("Fort_bij_Edam_004.JPG", "Het Fort bij Edam in 2010, Janericloebe (publiek domein)"),
            ("NIMH_-_2011_-_2918_-_Aerial_photograph_of_Fort_bij_Edam,_The_Netherlands.jpg", "Het fort vanuit de lucht in 1927, Nederlands Instituut voor Militaire Historie, CC BY-SA 4.0"),
        ],
        "source": WIKI("Fort_bij_Edam"),
        "more": WP + "Fort_bij_Edam",
    },
    {
        "year": "1916",
        "title": "De stormvloed",
        "at": (133452, 503245),
        "text": "In de nacht van 13 op 14 januari 1916 jaagt een noordwesterstorm de Zuiderzee over de dijken van Waterland. Achter de sluiswachterswoning in het Oorgat staat een stenen paal met het peil van die nacht. De ramp werd de aanleiding voor de Afsluitdijk; sinds 1932 ligt Edam aan een meer.",
        "source": WIKI("Edam"),
        "more": WP + "Zuiderzeevloed_van_1916",
    },
    {
        "year": "nu",
        "title": "Edam nu",
        "at": (132058, 502806),
        "zoom": 0.3,
        "text": "De binnenstad binnen de oude vesting is een beschermd stadsgezicht, met 176 rijksmonumenten. Edam vierde in 2007 zijn 650 jaar stadsrecht. Einde van de rondleiding.",
        "source": WIKI("Edam"),
        "more": WP + "Edam",
    },
]


def commons_thumb(name, width=960):  # Wikimedia only serves a fixed set of thumbnail widths
    h = hashlib.md5(name.encode()).hexdigest()
    q = urllib.parse.quote(name)
    return f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/{width}px-{q}"


def download(url, tries=6):
    """Wikimedia rate-limits bursts of thumbnail requests; wait politely and retry."""
    req = urllib.request.Request(url, headers={"User-Agent": "isometric-edam/0.1 (personal map)"})
    for attempt in range(tries):
        try:
            data = urllib.request.urlopen(req, timeout=60).read()
            time.sleep(3)
            return data
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == tries - 1:
                raise
            time.sleep(15 * (attempt + 1))


def route_order(stops):
    """Visit the stops as a route over the map instead of by date: the first and last stay put, the rest is a
    nearest-neighbour path tidied with 2-opt, so dots that lie together come one after another. Stops on the same
    spot (the old and the new church) keep their chronological order."""
    first, last, middle = stops[0], stops[-1], stops[1:-1]
    dist = lambda a, b: ((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2) ** 0.5
    path, todo = [first], middle[:]
    while todo:
        nxt = min(todo, key=lambda s: (dist(path[-1], s), stops.index(s)))
        path.append(nxt)
        todo.remove(nxt)
    path.append(last)
    improved = True
    while improved:
        improved = False
        for i in range(1, len(path) - 2):
            for j in range(i + 1, len(path) - 1):
                before = dist(path[i - 1], path[i]) + dist(path[j], path[j + 1])
                after = dist(path[i - 1], path[j]) + dist(path[i], path[j + 1])
                if after < before - 0.01:
                    path[i : j + 1] = path[i : j + 1][::-1]
                    improved = True
    # Places within 40 m of each other (church, parsonage, Sunday school) in chronological order.
    i = 0
    while i < len(path):
        j = i
        while j + 1 < len(path) - 1 and i > 0 and dist(path[j + 1], path[i]) < 40:
            j += 1
        year = lambda st: int(m.group()) if (m := re.search(r"\d{4}", st["year"])) else 9999
        path[i : j + 1] = sorted(path[i : j + 1], key=lambda st: (year(st), stops.index(st)))
        i = j + 1
    return path


def main():
    out_dir = BUILD / "history"
    out_dir.mkdir(parents=True, exist_ok=True)
    stops = []
    for i, s in enumerate(STOPS, start=1):
        x, y = s["at"] if "at" in s else wgs_to_rd(*s["latlon"])
        stop = {"n": i, "year": s["year"], "title": s["title"], "text": s["text"], "x": round(x, 1), "y": round(y, 1),
                "h": s.get("h", 0), "zoom": s.get("zoom", 1.2),
                "source": {"label": s["source"][0], "url": s["source"][1]}, "more": s.get("more")}
        stop["photos"] = []
        for k, (name, credit) in enumerate(s.get("photos", [])):
            dst = out_dir / f"{i:02d}_{k}.jpg"
            if not dst.exists():
                dst.write_bytes(download(commons_thumb(name)))
                subprocess.run(["magick", str(dst), "-resize", "640x640>", "-quality", "82", str(dst)], check=True)
            stop["photos"].append({"src": f"history/{dst.name}", "credit": credit,
                                   "url": f"https://commons.wikimedia.org/wiki/File:{urllib.parse.quote(name)}"})
        stops.append(stop)
    stops = route_order(stops)
    for n, stop in enumerate(stops, start=1):
        stop["n"] = n
    # A version in every photo URL, so browsers never show a cached photo that has since been replaced.
    version = hashlib.md5(b"".join(f.read_bytes() for f in sorted(out_dir.glob("*.jpg")))).hexdigest()[:8]
    for stop in stops:
        for ph in stop["photos"]:
            ph["src"] += f"?v={version}"
    (BUILD / "history.json").write_text(json.dumps({"stops": stops}, ensure_ascii=False, indent=1))
    print(f"{len(stops)} stops, {sum(len(s['photos']) for s in stops)} photos on {sum(bool(s['photos']) for s in stops)} stops")


if __name__ == "__main__":
    main()
