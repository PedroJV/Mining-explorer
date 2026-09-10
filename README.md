# Mining Explorer

A geospatial data platform exploring 48,414 mining and mineral sites across Western Australia, built end to end: live API extraction, PostGIS spatial database, a FastAPI service, and a four-page interactive dashboard.

## What it does

Mining Explorer pulls live data from MINEDEX, the Western Australian government's official register of mines and mineral deposits, models it as real spatial data in PostgreSQL with PostGIS, and serves it through an API to an interactive site covering context, mapping, statistics, and raw data exploration.

## Tech stack

- **Data extraction:** Python, requests (live ArcGIS REST API, paginated)
- **Data cleaning:** pandas, Jupyter
- **Database:** PostgreSQL with PostGIS (real spatial geometry, not flat lat/lon columns)
- **API:** FastAPI, with automatic interactive documentation at `/docs`
- **Frontend:** HTML, CSS, vanilla JavaScript, Leaflet.js for mapping

## Why this project is different from a flat CSV pipeline

- **Live extraction, not a static download.** The dataset is pulled directly from WA's ArcGIS REST service, paginated across 5 requests to cover all 48,414 records, the same data the government publishes today.
- **Real spatial geometry.** Coordinates are stored as PostGIS `geometry(Point, 4326)` objects, not plain numbers, enabling genuine spatial queries like finding every site within 100km of a given point using `ST_DWithin`, something flat columns can't do correctly.
- **Investigated, not assumed.** Early coordinate classification flagged sites as anomalies that turned out to be legitimate: places like Torbay and Denmark on WA's south coast, and Christmas Island, an external territory WA administers for mining regulation despite it sitting in the Indian Ocean. The classification was corrected after checking, rather than silently dropping or mislabelling real sites.

## What the data actually shows

Of 48,414 recorded sites, only 4,561 (9.4%) are currently operating. The rest is a historical register: 20,248 shut, 16,689 never developed, and the remainder proposed or under development. It's closer to a complete mining history of the state than a live production dashboard, and the site is built to make that distinction clear rather than imply otherwise.

## Site structure

- `index.html`, historical and dataset context
- `map.html`, interactive map of currently operating sites
- `stats.html`, aggregate statistics across the full register
- `explore.html`, searchable, filterable table covering all 48,414 records

## Running it locally

1. Clone the repo and create a virtual environment.
2. Install dependencies: `pip install fastapi uvicorn sqlalchemy psycopg2-binary geoalchemy2 python-decouple pandas jupyter requests`
3. Create a PostgreSQL database named `mining_explorer` with the PostGIS extension enabled.
4. Run the notebook to extract and load data, or restore from `data/mining_sites_clean.csv`.
5. Create a `.env` file with `DB_PASSWORD`.
6. Run `uvicorn main:app --reload`.
7. Open `frontend/index.html` in a browser.

---

Built by [Pedro Vasconez](https://github.com/PedroJV)
