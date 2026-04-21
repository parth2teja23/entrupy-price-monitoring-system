from __future__ import annotations
from __future__ import annotations

import json
from pathlib import Path
from fastapi import APIRouter, Query

router = APIRouter(prefix="/marketplaces", tags=["Marketplaces"], include_in_schema=False)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_PRODUCTS_DIR = PROJECT_ROOT / "sample_products"
SAMPLE_PRICE_CHANGES_DIR = PROJECT_ROOT / "sample_products_price_changes"


def _load_source_payload(prefix: str, simulate: bool = False) -> list[dict]:
    items: list[dict] = []
    data_dir = SAMPLE_PRICE_CHANGES_DIR if simulate and SAMPLE_PRICE_CHANGES_DIR.exists() else SAMPLE_PRODUCTS_DIR

    if not data_dir.exists():
        return items

    for file_path in sorted(data_dir.glob(f"{prefix}_*.json")):
        try:
            with file_path.open("r", encoding="utf-8") as handle:
                items.append(json.load(handle))
        except Exception:
            continue
    return items


@router.get("/1stdibs")
async def get_1stdibs_products(simulate: bool = Query(False)) -> list[dict]:
    return _load_source_payload("1stdibs", simulate=simulate)


@router.get("/fashionphile")
async def get_fashionphile_products(simulate: bool = Query(False)) -> list[dict]:
    return _load_source_payload("fashionphile", simulate=simulate)


@router.get("/grailed")
async def get_grailed_products(simulate: bool = Query(False)) -> list[dict]:
    return _load_source_payload("grailed", simulate=simulate)
