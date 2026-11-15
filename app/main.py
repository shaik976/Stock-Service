from fastapi import FastAPI, HTTPException

from .inventory import Store, StockItem, load_stores

app = FastAPI(title="Store Stock Service")
STORES = load_stores()


def _item_json(i: StockItem) -> dict:
    return {
        "component_id": i.component_id,
        "component_name": i.component_name,
        "component_type": i.component_type,
        "quantity_on_hand": i.quantity_on_hand,
        "reserved_quantity": i.reserved_quantity,
        "available": i.available,
        "in_stock": i.available > 0,
        "last_updated_at": i.last_updated_at,
    }


def _get_store(store_id: int) -> Store:
    store = STORES.get(store_id)
    if store is None:
        raise HTTPException(404, f"Unknown store {store_id}")
    return store


@app.get("/stores")
def list_stores():
    return [
        {"store_id": s.store_id, "store_name": s.store_name, "store_open": s.store_open}
        for s in STORES.values()
    ]


@app.get("/stores/{store_id}/stock")
def store_stock(store_id: int):
    s = _get_store(store_id)
    return {
        "store_id": s.store_id,
        "store_name": s.store_name,
        "store_open": s.store_open,
        "items": [_item_json(i) for i in s.items.values()],
    }


@app.get("/stores/{store_id}/stock/{component_id}")
def component_stock(store_id: int, component_id: str):
    s = _get_store(store_id)
    item = s.items.get(component_id)
    if item is None:
        raise HTTPException(404, f"Store {store_id} has no component '{component_id}'")
    return {"store_id": s.store_id, "store_open": s.store_open, **_item_json(item)}
