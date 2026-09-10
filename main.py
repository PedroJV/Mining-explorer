from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from decouple import config

app = FastAPI(title="Mining Explorer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PASSWORD = config('DB_PASSWORD')
engine = create_engine(f'postgresql://postgres:{DB_PASSWORD}@localhost:5432/mining_explorer')


@app.get("/")
def read_root():
    return {"message": "Mining Explorer API is running"}


@app.get("/sites/count")
def count_sites():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM mining_sites"))
        count = result.scalar()
    return {"total_sites": count}


@app.get("/sites/geojson")
def get_sites_geojson(limit: int = 500):
    query = text("""
        SELECT
            site_id,
            site_title,
            site_stage,
            commodity,
            site_type,
            ST_X(location::geometry) AS longitude,
            ST_Y(location::geometry) AS latitude
        FROM mining_sites
        WHERE site_stage = 'Operating'
        LIMIT :limit
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"limit": limit})
        rows = result.fetchall()

    features = []
    for row in rows:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row.longitude, row.latitude]
            },
            "properties": {
                "site_id": row.site_id,
                "site_title": row.site_title,
                "site_stage": row.site_stage,
                "commodity": row.commodity,
                "site_type": row.site_type
            }
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }


@app.get("/stats/by-stage")
def stats_by_stage():
    query = text("""
        SELECT site_stage, COUNT(*) as count
        FROM mining_sites
        GROUP BY site_stage
        ORDER BY count DESC
    """)
    with engine.connect() as conn:
        rows = conn.execute(query).fetchall()
    return [{"label": row.site_stage, "count": row.count} for row in rows]


@app.get("/stats/by-type")
def stats_by_type():
    query = text("""
        SELECT site_type, COUNT(*) as count
        FROM mining_sites
        GROUP BY site_type
        ORDER BY count DESC
    """)
    with engine.connect() as conn:
        rows = conn.execute(query).fetchall()
    return [{"label": row.site_type, "count": row.count} for row in rows]


@app.get("/stats/by-region")
def stats_by_region():
    query = text("""
        SELECT location_region, COUNT(*) as count
        FROM mining_sites
        GROUP BY location_region
        ORDER BY count DESC
    """)
    with engine.connect() as conn:
        rows = conn.execute(query).fetchall()
    return [{"label": row.location_region, "count": row.count} for row in rows]


@app.get("/stats/top-commodities")
def top_commodities(limit: int = 12):
    query = text("""
        SELECT commodity, COUNT(*) as count
        FROM mining_sites
        WHERE commodity IS NOT NULL AND commodity != ''
        GROUP BY commodity
        ORDER BY count DESC
        LIMIT :limit
    """)
    with engine.connect() as conn:
        rows = conn.execute(query, {"limit": limit}).fetchall()
    return [{"label": row.commodity, "count": row.count} for row in rows]


@app.get("/sites/list")
def list_sites(
    page: int = 1,
    page_size: int = 50,
    search: str = "",
    stage: str = "",
    site_type: str = ""
):
    offset = (page - 1) * page_size

    conditions = []
    params = {"limit": page_size, "offset": offset}

    if search:
        conditions.append("site_title ILIKE :search")
        params["search"] = f"%{search}%"
    if stage:
        conditions.append("site_stage = :stage")
        params["stage"] = stage
    if site_type:
        conditions.append("site_type = :site_type")
        params["site_type"] = site_type

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    count_query = text(f"SELECT COUNT(*) FROM mining_sites {where_clause}")
    data_query = text(f"""
        SELECT site_id, site_title, site_type, site_stage, commodity, location_region
        FROM mining_sites
        {where_clause}
        ORDER BY site_id
        LIMIT :limit OFFSET :offset
    """)

    with engine.connect() as conn:
        total = conn.execute(count_query, params).scalar()
        rows = conn.execute(data_query, params).fetchall()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": [
            {
                "site_id": row.site_id,
                "site_title": row.site_title,
                "site_type": row.site_type,
                "site_stage": row.site_stage,
                "commodity": row.commodity,
                "location_region": row.location_region
            }
            for row in rows
        ]
    }