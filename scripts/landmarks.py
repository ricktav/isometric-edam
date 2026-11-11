# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy"]
# ///
"""Named places of Edam: style overrides and extra geometry for buildings, plus the viewer's place list.

Sources: the Rijksmonumentenregister, Dutch Wikipedia, photos on Wikimedia Commons, OpenStreetMap, and AHN for
tower positions and heights.

Output: data/build/landmarks.json
"""

import json

import numpy as np

from config import BUILD, RAW
from geo import wgs_to_rd

WP = "https://nl.wikipedia.org/wiki/"  # Dutch Wikipedia, where most of these stories are told at length
RCE = "Rijksdienst voor het Cultureel Erfgoed"

# Buildings found by an address or point; `pand` is resolved to the 3D BAG building under that point.
BUILDINGS = [
    {
        "name": "Grote of Sint-Nicolaaskerk",
        "note": "Laatgotische hallenkerk, begonnen in de 15e eeuw, met de grootste gebrandschilderde ramen van het land",
        "kind": "Rijksmonument · 15e eeuw",
        "stop": "De Grote Kerk",
        "addrs": ["Grote Kerkstraat 59"],
        "address": "Grote Kerkstraat 59",
        "style": "church",
        "wall": (138, 78, 60),
        "roof": (74, 76, 84),
        # The west tower, in AHN about 7 m square and 39.6 m to the top of its low spire.
        "tower": {"x": 131917.2, "y": 503140.5, "w": 7.2, "body": 30.0, "top": 39.6, "cross": True},
        "photo": ("Edam_-_SInt-Nicolaaskeerk_011.jpg", "De Grote Kerk in 2022, P. Hughes, CC BY 4.0"),
        "web": "https://www.grotekerkedam.nl",
    },
    {
        "name": "Speeltoren",
        "note": "Scheve toren van de afgebroken Onze-Lieve-Vrouwekerk, met een carillon dat elk kwartier speelt",
        "kind": "Rijksmonument · 16e eeuw",
        "stop": "De Speeltoren",
        "addrs": ["Lingerzijde 1"],
        "address": "Lingerzijde 1",
        "style": "church",
        "wall": (140, 80, 62),
        "roof": (90, 92, 100),
        # In AHN: a 4.5 m square shaft to about 27 m, the octagonal lantern on top of it reaches 40 m.
        "tower": {"x": 131901.0, "y": 502795.2, "w": 4.6, "body": 27.0, "top": 40.1},
        "photo": ("Edam_023.JPG", "De Speeltoren in 2012, Microtoerisme, CC BY-SA 3.0"),
    },
    {
        "name": "Raadhuis",
        "note": "Stadhuis in Lodewijk XIV-stijl uit 1737, van bouwmeester Jacob Jongh",
        "kind": "Rijksmonument · 1737",
        "stop": "Het Raadhuis",
        "addrs": ["Damplein 1"],
        "address": "Damplein 1",
        "style": "house",
        "wall": (120, 68, 54),
        "roof": (70, 72, 80),
        "frame": (240, 238, 230),
        # The little clock tower on the roof, 24.7 m up in AHN.
        "turret": {"x": 132070.7, "y": 502794.2, "r": 1.3, "base": 12.0, "body": 19.5, "top": 24.7},
        "photo": ("Edam,_Holland_5.jpg", "Het Raadhuis aan het Damplein in 2005, stevekc, CC BY 2.0"),
        "web": "https://www.edamsmuseum.nl",
    },
    {
        "name": "Edams Museum (Steenen Coopmanshuys)",
        "note": "Het oudste stenen huis van Edam, uit ca. 1540, met een drijvende kelder",
        "kind": "Rijksmonument · ca. 1540",
        "stop": "Het Steenen Coopmanshuys",
        "addrs": ["Damplein 8"],
        "address": "Damplein 8",
        "style": "house",
        "wall": (132, 72, 56),
        "roof": (150, 70, 50),
        "frame": (236, 234, 226),
        "photo": ("Edam_-_Damplein_8jpg.jpg", "Het Edams Museum aan het Damplein in 2010, Arch, publiek domein"),
        "web": "https://www.edamsmuseum.nl",
    },
    {
        "name": "Kaaswaag",
        "note": "Waaggebouw uit 1778 aan de Kaasmarkt, waar in de zomer op woensdag de kaasmarkt is",
        "kind": "Rijksmonument · 1778",
        "stop": "De Kaasmarkt",
        "addrs": ["Jan Nieuwenhuizenplein 5"],
        "address": "Jan Nieuwenhuizenplein 5",
        "style": "house",
        "wall": (236, 232, 220),
        "roof": (150, 68, 48),
        "frame": (60, 90, 60),
        "photo": ("Kaaswaag_Edam.JPG", "De Kaaswaag in 2011, Marion Golsteijn, CC BY-SA 3.0 NL"),
        "web": "https://www.kaasmarktedam.nl",
    },
    {
        "name": "Lutherse kerk (De Swaen)",
        "note": "Evangelisch-lutherse kerk uit 1739-1741, met gevels in Lodewijk XIV-stijl, nu de protestantse kerk De Swaen",
        "kind": "Rijksmonument · 1740",
        "stop": "De Lutherse kerk",
        "addrs": ["Voorhaven 135"],
        "address": "Voorhaven 135",
        "style": "church",
        "wall": (134, 76, 58),
        "roof": (72, 74, 82),
        "photo": ("Edam,_Evangelisch_Lutherse_kerk.jpg", "De Lutherse kerk aan de Voorhaven in 2010, Arch, publiek domein"),
    },
    {
        "name": "Proveniershuis",
        "note": "In 1555 gesticht als tehuis voor ouderen die zich inkochten; de gebouwen zijn 17e- en 18e-eeuws",
        "kind": "Rijksmonument · 1555",
        "stop": "Het Proveniershuis",
        "addrs": ["J C Brouwersgracht 30"],
        "address": "J.C. Brouwersgracht 30",
        "style": "house",
        "wall": (138, 78, 60),
        "roof": (150, 70, 50),
        "frame": (240, 238, 230),
        "photo": ("Proveniershuis_JC_Brouwersgracht_30_Edam_Rijksmonument_14292.jpg", "Het Proveniershuis in 2017, Edithnib, CC BY-SA 3.0 NL"),
    },
    {
        "name": "Doopsgezinde vermaning",
        "kind": "Rijksmonument · 1702",
        "addrs": ["Jan Nieuwenhuizenplein 6"],
        "address": "Jan Nieuwenhuizenplein 6",
        "text": "Een schuilkerkje aan de Kaasmarkt uit 1702: de doopsgezinden mochten in de Republiek wel samenkomen, maar hun kerk mocht er van buiten niet als een kerk uitzien.",
    },
    {
        "name": "Voormalig weeshuis",
        "kind": "Rijksmonument · 19e eeuw",
        "addrs": ["Jan Nieuwenhuizenplein 12"],
        "address": "Jan Nieuwenhuizenplein 12",
        "text": "Het weeshuis van Edam aan de Kaasmarkt, in het laatste kwart van de 19e eeuw gebouwd op de plek van zijn voorganger.",
    },
    {
        "name": "Sluiswachterswoning Oorgat",
        "kind": "Rijksmonument",
        "addrs": ["Oorgat 1"],
        "address": "Oorgat 1",
        "stop": "De stormvloed van 1916",
        "text": "Het huis van de sluiswachter bij de zeesluis in het Oorgat. Achter het huis staat een stenen paal die aangeeft hoe hoog het water in januari 1916 stond, toen de Zuiderzee over de dijken kwam.",
    },
    {
        "name": "Hotel De Fortuna",
        "addrs": ["Spuistraat 3"],
        "kind": "Hotel en restaurant",
        "address": "Spuistraat 3",
        "text": "Hotel-restaurant in een rij 17e-eeuwse huisjes aan het water van de Spuistraat, met een tuin aan de gracht.",
        "web": "https://www.fortuna-edam.nl",
    },
]

# Points without a building of their own.
POINTS = [
    # The fort is a bomb-proof barracks under a mound of earth: the 3D BAG has only its sheds, so it is a point on
    # the OpenStreetMap fort polygon; AHN shows the mound.
    {
        "name": "Fort bij Edam",
        "at": (133293, 503416),
        "kind": "Werelderfgoed · 1913",
        "stop": "Het Fort bij Edam",
        "address": "Oorgat 10",
        "text": "Het laatste fort van de Stelling van Amsterdam, gebouwd in 1908-1913 bij het Oorgat om de zeedijk en de sluis te dekken: een bomvrij gebouw onder een aarden wal, met een gracht eromheen. Sinds 2005 houdt een stichting het open voor bezoek.",
        "photo": ("Fort_bij_Edam_004.JPG", "Het Fort bij Edam in 2010, Janericloebe, publiek domein"),
        "web": "https://www.fortbijedam.nl",
        "more": WP + "Fort_bij_Edam",
    },
    {
        "name": "Damplein",
        "at": (132058, 502806),
        "kind": "Plein",
        "stop": "De dam in de IJe",
        "text": "Het hart van Edam: de dam in het riviertje de IJe (of E) waar het stadje rond 1230 naar is genoemd. Aan het plein staan het Raadhuis en het Edams Museum.",
    },
    {
        "name": "Damsluis",
        "at": (132036, 502806),
        "kind": "Rijksmonument · 1795-1798",
        "text": "De schutsluis onder het Damplein, uit 1795-1798, scheidt het water van de Voorhaven van de grachten en de polder erachter.",
        "photo": ("Damsluis_Edam.jpg", "De Damsluis in 2011, Marion Golsteijn, CC BY-SA 3.0"),
    },
    {
        "name": "Kaasmarkt",
        "at": (131950, 502940),
        "kind": "Plein",
        "stop": "De Kaasmarkt",
        "photo": ("Kaasmarkt_Edam.jpg", "Kaasmarkt in Edam, 2006, Lupo, CC BY-SA 3.0"),
    },
    {
        "name": "Kwakelbrug",
        "at": (131919, 502658),
        "kind": "Rijksmonument · 18e eeuw",
        "stop": "De Kwakelbrug",
        "text": "Een smalle houten ophaalbrug over de Schepenmakersdijk-gracht, net breed genoeg voor een voetganger. Het is een van de meest gefotografeerde plekjes van Edam.",
        "photo": ("Kwakelbrug.JPG", "De Kwakelbrug in 2011, Marion Golsteijn, CC BY-SA 3.0 NL"),
    },
    {
        "name": "Stormvloedpaal 1916",
        "at": (133452, 503245),
        "kind": "Rijksmonument · 1916",
        "stop": "De stormvloed van 1916",
        "text": "Een stenen paal achter de sluiswachterswoning in het Oorgat met het peil van de stormvloed van 13 en 14 januari 1916, die het Waterland onder water zette en de aanleiding werd voor de Afsluitdijk.",
    },
    {
        "name": "Oorgatsluis",
        "at": (133434, 503192),
        "kind": "Zeesluis",
        "stop": "Voorhaven en Oorgat",
        "text": "De sluis waarmee de Voorhaven van Edam aan het IJsselmeer ligt. Al in 1357, bij het stadsrecht, mocht Edam hier een haven naar zee maken.",
    },
    {
        "name": "Vestingwal",
        "at": (131800, 503260),
        "kind": "Rijksmonument",
        "stop": "De vesting",
        "text": "De overblijfselen van de stadswallen van Edam, de Wester- en Noordervesting, met de singelgracht ervoor. De vesting omsloot het stadje vanaf de 16e eeuw; de Purmerpoort werd in 1835 afgebroken.",
        "photo": ("Edam,_Omwalling_van_voormalige_Wester-,_Noordervesting.jpg", "De wal van de Noordervesting in 2011, M.arjon, CC BY-SA 3.0 NL"),
    },
    {"name": "Strandbad Edam", "at": (133760, 503150), "kind": "Strand", "text": "Het strandje van Edam aan het IJsselmeer, met een trap in de dijk en uitzicht tot Marken."},
    {"name": "Jachthaven Edam", "at": (133650, 503260), "kind": "Jachthaven", "text": "De jachthaven buiten de dijk, waar de Voorhaven via het Oorgat op het IJsselmeer uitkomt."},
    {
        "name": "Standbeeld Jan Nieuwenhuyzen",
        "at": (131965, 502930),
        "kind": "Monument",
        "text": "Jan Nieuwenhuyzen (1724-1806), doopsgezind predikant in Edam, richtte hier in 1784 de Maatschappij tot Nut van 't Algemeen op, die scholen en bibliotheken stichtte voor gewone mensen. Het plein van de Kaasmarkt draagt zijn naam.",
    },
    {
        "name": "Joodse begraafplaats",
        "at": (132678, 502971),
        "kind": "Begraafplaats",
        "text": "De Joodse begraafplaats van Edam aan de rand van de oude stad, bij de Oosterkade. Ernaast staat het monument De tochtgenoten voor de Joodse Edammers die in de oorlog werden weggevoerd.",
        "more": WP + "Joodse_begraafplaats_(Edam)",
    },
    {
        "name": "Monument De tochtgenoten",
        "at": (132680, 502954),
        "kind": "Oorlogsmonument",
        "text": "Rachel beweent haar kinderen: een gedenkteken bij de Joodse begraafplaats voor de Joodse inwoners van Edam die de oorlog niet overleefden.",
        "more": WP + "De_tochtgenoten",
    },
    {"name": "Egbert Snijder-monument", "at": (131818, 502555), "kind": "Kunstwerk", "more": WP + "Egbert_Snijder_monument"},
    {
        "name": "Trambrug",
        "at": (131740, 502652),
        "kind": "Spoorbrug",
        "text": "Hier reed van 1888 tot 1932 de stoomtram van Amsterdam naar Edam; het tracé is nu een fietspad langs de vesting.",
    },
    {"name": "Camping Strandbad Edam", "at": (133608, 503488), "kind": "Camping", "web": "https://www.campingstrandbad.nl"},
    {"name": "Natuurpark De Broeckgouw", "at": (133341, 502871), "kind": "Natuur"},
    {"name": "Zeedijk", "at": (133900, 503700), "kind": "Dijk", "stop": "De stormvloed van 1916", "text": "De dijk tussen Edam en de polder Zeevang en het IJsselmeer, sinds 1932 geen zee meer maar een meer. Het Zuiderzeepad loopt erover."},
]

# Series in the viewer's panel: a walk past these places, starting with the one nearest the centre.
CATEGORIES = [
    ("binnenstad", "Monumenten in de binnenstad", [
        "Raadhuis", "Edams Museum (Steenen Coopmanshuys)", "Damsluis", "Speeltoren", "Lutherse kerk (De Swaen)", "Kwakelbrug",
        "Kaaswaag", "Doopsgezinde vermaning", "Voormalig weeshuis", "Proveniershuis", "Grote of Sint-Nicolaaskerk", "Vestingwal",
    ]),
    ("water", "Aan het water", ["Damsluis", "Kwakelbrug", "Oorgatsluis", "Sluiswachterswoning Oorgat", "Stormvloedpaal 1916", "Jachthaven Edam", "Strandbad Edam", "Zeedijk", "Fort bij Edam", "Trambrug"]),
    ("herdenken", "Monumenten en herdenking", ["Standbeeld Jan Nieuwenhuyzen", "Joodse begraafplaats", "Monument De tochtgenoten", "Stormvloedpaal 1916", "Egbert Snijder-monument"]),
    ("kaas", "Kaas", ["Kaasmarkt", "Kaaswaag"]),
    ("bedrijven", "Bedrijven", ["Hotel De Fortuna", "Edams Museum (Steenen Coopmanshuys)", "Fort bij Edam", "Jachthaven Edam", "Camping Strandbad Edam"]),
]

# What the viewer shows when a place is clicked; the rest of an entry is for the render.
INFO = ("note", "kind", "text", "address", "web", "more", "photo", "stop")

# No lattice masts in the area yet; see scripts/landmarks.py of Isometric Helenaveen for the format.
MASTS = []


def point_in_ring(x, y, ring):
    inside = False
    for (x1, y1), (x2, y2) in zip(ring, np.roll(ring, -1, axis=0)):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside


ADDRESSES = None


def address_xy(name):
    """RD position of a BAG address such as "Geldersestraat 3" (data/raw/addresses.json, from scripts/fetch.py)."""
    global ADDRESSES
    if ADDRESSES is None:
        ADDRESSES = {label.replace(", Edam", "").split(", ")[0]: (x, y) for x, y, label in json.loads((RAW / "addresses.json").read_text())}
    return ADDRESSES[name]


def building_at(rings, x, y):
    for rid, ring, a in rings:
        if point_in_ring(x, y, ring):
            return rid, a
    return None, None


def main():
    feats = [json.loads(line) for line in open(RAW / "3dbag.jsonl")]
    rings = []
    for f in feats:
        t = f["transform"]
        V = np.array(f["vertices"], dtype=np.float64) * t["scale"] + t["translate"]
        co = f["CityObjects"][f["id"]]
        rings.append((f["id"], V[co["geometry"][0]["boundaries"][0][0]][:, :2], co["attributes"]))

    out = {"buildings": {}, "places": [], "masts": [], "hotspots": [], "categories": []}
    for b in BUILDINGS:
        if "addrs" in b:
            pts = [address_xy(a) for a in b["addrs"]]
            pids = [building_at(rings, *pt)[0] for pt in pts]
            assert all(pids), f"{b['name']}: no building at {b['addrs']}"
            x, y = np.mean(pts, axis=0)
            out["places"].append({"name": b["name"], "note": b.get("note"), "x": x, "y": y, "h": 4.0})
            out["hotspots"].append({"name": b["name"], "pids": pids, "x": x, "y": y, **{k: b[k] for k in INFO if k in b}})
            if "style" in b:
                for pid in pids:
                    out["buildings"][pid] = {k: v for k, v in b.items() if k not in ("at", "latlon", "addrs", *INFO)}
            print(f"{b['name']}: {', '.join(pids)}")
            continue
        x, y = b["at"] if "at" in b else wgs_to_rd(*b["latlon"])
        pid, attrs = None, None
        for rid, ring, a in rings:
            if point_in_ring(x, y, ring):
                pid, attrs = rid, a
                break
        if pid is None:
            d = [(np.hypot(*(ring.mean(0) - (x, y))), rid, a) for rid, ring, a in rings]
            dist, pid, attrs = min(d, key=lambda t: t[0])
            if dist > 20:
                pid = None
        height = ((attrs or {}).get("b3_h_dak_max") or 0) - ((attrs or {}).get("b3_h_maaiveld") or 0)
        if "tower" in b:
            height = b["tower"]["top"]
        elif "turret" in b:
            height = b["turret"]["top"]
        out["places"].append({"name": b["name"], "note": b.get("note"), "x": x, "y": y, "h": round(height, 1)})
        if pid and "style" in b:
            out["buildings"][pid] = {k: v for k, v in b.items() if k not in ("at", "latlon", *INFO)}
        if pid:
            out["hotspots"].append({"name": b["name"], "pid": pid, "x": x, "y": y, **{k: b[k] for k in INFO if k in b}})
        print(f"{b['name']}: {pid or 'no building'}")
    for p in POINTS:
        x, y = p["at"] if "at" in p else address_xy(p["addr"]) if "addr" in p else wgs_to_rd(*p["latlon"])
        out["places"].append({"name": p["name"], "note": p.get("note"), "x": x, "y": y, "h": 2.0})
        out["hotspots"].append({"name": p["name"], "x": x, "y": y, **{k: p[k] for k in INFO if k in p}})
    for m in MASTS:
        x, y = wgs_to_rd(*m["latlon"])
        out["masts"].append({**{k: v for k, v in m.items() if k != "latlon"}, "x": x, "y": y})
    names = {h["name"] for h in out["hotspots"]}
    for key, label, members in CATEGORIES:
        missing = [n for n in members if n not in names]
        assert not missing, f"{label}: no hotspot for {missing}"
        out["categories"].append({"key": key, "label": label, "names": members})
    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / "landmarks.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
