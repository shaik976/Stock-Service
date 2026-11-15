"""Step 1: know what each store has left."""
import csv
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CSV = Path(__file__).resolve().parent.parent / "data" / "Store.csv"


@dataclass(frozen=True)
class StockItem:
    component_id: str
    component_name: str
    component_type: str  # "drink_base" or "add_in"
    quantity_on_hand: int
    reserved_quantity: int
    last_updated_at: str

    @property
    def available(self) -> int:
        # Reserved stock is already promised to other orders.
        return max(0, self.quantity_on_hand - self.reserved_quantity)


@dataclass
class Store:
    store_id: int
    store_name: str
    store_open: bool
    items: dict  # component_id -> StockItem


def load_stores(path: Path = DEFAULT_CSV) -> dict:
    """Read the stock CSV into {store_id: Store}."""
    stores: dict = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            sid = int(row["store_id"])
            store = stores.setdefault(
                sid,
                Store(
                    store_id=sid,
                    store_name=row["store_name"],
                    store_open=row["store_open"].strip().lower() == "true",
                    items={},
                ),
            )
            store.items[row["component_id"]] = StockItem(
                component_id=row["component_id"],
                component_name=row["component_name"],
                component_type=row["component_type"],
                quantity_on_hand=int(row["quantity_on_hand"]),
                reserved_quantity=int(row["reserved_quantity"]),
                last_updated_at=row["last_updated_at"],
            )
    return stores
