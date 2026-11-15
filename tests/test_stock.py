import pytest
from fastapi.testclient import TestClient

from app.inventory import load_stores
from app.main import app

client = TestClient(app)
FIRST_HILL, CAPITOL_HILL, SLU = 10482, 11307, 9815


def test_loads_three_stores_with_ten_components_each():
    stores = load_stores()
    assert set(stores) == {FIRST_HILL, CAPITOL_HILL, SLU}
    assert all(len(s.items) == 10 for s in stores.values())


def test_first_hill_oat_milk_is_sold_out():
    r = client.get(f"/stores/{FIRST_HILL}/stock/oat_milk")
    assert r.status_code == 200
    body = r.json()
    assert body["available"] == 0
    assert body["in_stock"] is False


def test_capitol_hill_oat_milk_subtracts_reserved():
    body = client.get(f"/stores/{CAPITOL_HILL}/stock/oat_milk").json()
    assert body["quantity_on_hand"] == 2
    assert body["reserved_quantity"] == 1
    assert body["available"] == 1
    assert body["in_stock"] is True


def test_capitol_hill_almond_milk_is_sold_out():
    assert client.get(f"/stores/{CAPITOL_HILL}/stock/almond_milk").json()["in_stock"] is False


def test_closed_store_is_reported_closed():
    body = client.get(f"/stores/{SLU}/stock").json()
    assert body["store_open"] is False
    assert len(body["items"]) == 10


def test_list_stores():
    r = client.get("/stores")
    assert r.status_code == 200
    assert {s["store_id"]: s["store_open"] for s in r.json()} == {
        FIRST_HILL: True, CAPITOL_HILL: True, SLU: False,
    }


@pytest.mark.parametrize("url", ["/stores/1/stock", f"/stores/{FIRST_HILL}/stock/unicorn_milk"])
def test_unknown_store_or_component_is_404(url):
    assert client.get(url).status_code == 404


def test_available_is_never_negative(tmp_path):
    p = tmp_path / "s.csv"
    p.write_text(
        "store_id,store_name,store_open,component_id,component_name,component_type,"
        "quantity_on_hand,reserved_quantity,last_updated_at\n"
        "1,Test,True,oat_milk,Oatmilk,drink_base,1,3,2025-03-07T06:00:00-08:00\n"
    )
    assert load_stores(p)[1].items["oat_milk"].available == 0


def test_first_hill_almond_milk_matches_snapshot_row():
    # Store.csv row: 10482, almond_milk, 38 on hand, 1 reserved
    body = client.get(f"/stores/{FIRST_HILL}/stock/almond_milk").json()
    assert body["quantity_on_hand"] == 38
    assert body["reserved_quantity"] == 1
    assert body["available"] == 37
    assert body["in_stock"] is True


def test_first_hill_two_pct_milk_matches_snapshot_row():
    # Store.csv row: 10482, two_pct_milk, 96 on hand, 3 reserved
    body = client.get(f"/stores/{FIRST_HILL}/stock/two_pct_milk").json()
    assert body["quantity_on_hand"] == 96
    assert body["reserved_quantity"] == 3
    assert body["available"] == 93
    assert body["in_stock"] is True
