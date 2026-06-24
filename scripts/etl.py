"""
ETL pipeline for the City of Mainland procurement dataset.

Reads the raw multi-sheet workbook, cleans it, derives the calculation
fields defined in the project brief, builds a star-schema model, and writes
the processed CSVs + a clean Excel model used by the Power BI project.

Run:
    python scripts/etl.py
"""
from pathlib import Path
import pandas as pd

RAW = Path("data/raw/Purchase_Transaction.xls")
OUT = Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)


def load_raw():
    sheets = pd.read_excel(RAW, sheet_name=["Category", "Product", "ProductCategory", "PurchaseTrans"])
    return sheets["Category"], sheets["Product"], sheets["ProductCategory"], sheets["PurchaseTrans"]


def clean_transactions(pt: pd.DataFrame) -> pd.DataFrame:
    pt = pt.copy()
    # Missing categorical values -> explicit labels (keeps rows analysable)
    pt["Color"] = pt["Color"].fillna("Not Specified")

    def _postal(v):
        if pd.isna(v):
            return "Unknown"
        if isinstance(v, float):
            return str(int(v))
        return str(v).strip()

    pt["PostalCode"] = pt["PostalCode"].map(_postal)
    # Normalise dates
    for d in ["DueDate", "ShipDate", "OrderDate"]:
        pt[d] = pd.to_datetime(pt[d])
    # Trim text dimensions
    for c in ["Supplier", "City", "StateProvince", "Country", "Employee"]:
        pt[c] = pt[c].astype(str).str.strip()
    # Calculation fields (per brief):
    #   Purchased Amount   = UnitPrice * OrderQty
    #   Discount Amount    = UnitPriceDiscount * Purchased Amount
    #   Net Purchase Amount= Purchased Amount - Discount Amount
    pt["PurchasedAmount"] = (pt["UnitPrice"] * pt["OrderQty"]).round(2)
    pt["DiscountAmount"] = (pt["UnitPriceDiscount"] * pt["PurchasedAmount"]).round(2)
    pt["NetPurchaseAmount"] = (pt["PurchasedAmount"] - pt["DiscountAmount"]).round(2)
    pt["OrderYear"] = pt["OrderDate"].dt.year
    pt["OrderMonth"] = pt["OrderDate"].dt.to_period("M").astype(str)
    return pt


def quality_checks(pt: pd.DataFrame, prod: pd.DataFrame):
    assert pt["TransID"].is_unique, "Duplicate TransID found"
    assert (pt["OrderQty"] > 0).all(), "Non-positive OrderQty"
    assert (pt["UnitPrice"] > 0).all(), "Non-positive UnitPrice"
    assert pt["ProductID"].isin(prod["ProductID"]).all(), "Orphan ProductID"
    assert pt.isnull().sum().sum() == 0, "Residual nulls remain"


def build_model(cat, prod, pc, pt):
    dim_product = (
        prod.merge(pc[["ProductID", "CategoryID"]], on="ProductID", how="left")
            .merge(cat, on="CategoryID", how="left")
    )
    return dim_product, cat


def main():
    cat, prod, pc, pt = load_raw()
    pt = clean_transactions(pt)
    quality_checks(pt, prod)
    dim_product, dim_category = build_model(cat, prod, pc, pt)

    # Processed CSVs (consumed by the Power BI project)
    pt.to_csv(OUT / "PurchaseTrans.csv", index=False)
    dim_product.to_csv(OUT / "DimProduct.csv", index=False)
    dim_category.to_csv(OUT / "DimCategory.csv", index=False)

    # Combined Excel model (convenient single-file import)
    with pd.ExcelWriter(OUT / "Mainland_Clean_Model.xlsx", engine="openpyxl") as w:
        pt.to_excel(w, sheet_name="PurchaseTrans", index=False)
        dim_product.to_excel(w, sheet_name="DimProduct", index=False)
        dim_category.to_excel(w, sheet_name="DimCategory", index=False)

    print(f"Rows: {len(pt):,}")
    print(f"Total Net Purchase Amount: CAD {pt['NetPurchaseAmount'].sum():,.2f}")
    print("ETL complete. Processed files written to data/processed/")


if __name__ == "__main__":
    main()
