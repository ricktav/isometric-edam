# Isometrisch Edam

Een zoombare isometrische pixel-art-kaart van Edam (Noord-Holland), 4 × 4 km van de polders van de Zeevang tot het Fort bij Edam, de zeedijk en het strandbad aan het IJsselmeer. Gemaakt met de code van [Isometric Helenaveen](https://github.com/jankeesvw/isometric-helenaveen) van [@jankeesvw](https://x.com/jankeesvw), die een dorp procedureel rendert uit Nederlandse open data: exact, naadloos en in een paar minuten opnieuw te bouwen.

Edam ligt in Nederland, dus de bronnen van het voorbeeld zijn ongewijzigd gebruikt: RD-coördinaten (EPSG:28992), gebouwen uit de 3D BAG (LoD2.2, met dakvormen), de grond uit de BGT, de luchtfoto van PDOK (25 cm) en de hoogtes van bomen en reliëf uit het AHN (50 cm). Wegen, paden, water, wandelroutes en bezienswaardigheden komen uit OpenStreetMap.

## Pijplijn

`./build.sh` doet alles: `scripts/fetch.py` haalt de ruwe data op (de 3D BAG per blok van 500 m, parallel, omdat de API maar 50 gebouwen per pagina geeft), `scripts/landmarks.py` benoemt de plekken en voegt toe wat de 3D BAG gladstrijkt (de Speeltoren van 40 m en de toren van de Grote Kerk, allebei gemeten in het AHN, en het torentje op het Raadhuis), `build_buildings.py`, `build_trees.py` en `build_ground.py` bouwen de scène, `render/run.mjs` rendert die tegel voor tegel in headless Chromium vanuit vier windrichtingen, `vips dzsave` snijdt er Deep Zoom-piramides van en `viewer/index.html` toont ze met OpenSeadragon. Zie de README van Isometric Helenaveen voor de details van elke stap.

Het gebied staat in `scripts/config.py`. De plekken en hun verhalen staan in `scripts/landmarks.py`, de rondleiding "Edam van toen" in `scripts/build_history.py`. De vaste punten van de viewer (beginpunt op het Damplein, de lantaarns binnen 900 m van het centrum, de zwemmers bij het strandbad) staan bovenin `viewer/index.html`.

`./site.sh` bouwt `site/` opnieuw zonder te renderen; `./deploy.sh` publiceert `site/` naar GitHub Pages.

## Data en licenties

- 3D BAG (TU Delft, 3DGI): CC BY 4.0
- BGT, AHN, BAG-adressen (Kadaster, Rijkswaterstaat): CC0 / publiek domein
- Luchtfoto (Beeldmateriaal Nederland, via PDOK): CC BY 4.0
- OpenStreetMap: ODbL
- Teksten: naar Wikipedia (CC BY-SA 4.0) en het Rijksmonumentenregister
- Foto's: Wikimedia Commons, per bestand gecontroleerd (publiek domein, CC BY, CC BY-SA); de credits staan bij elke foto
- Muziek: [My Street](https://opengameart.org/content/my-street) van congusbongus, CC0
