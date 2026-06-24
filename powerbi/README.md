# Power BI Project (`.pbip`)

This folder is a **Power BI Project (PBIP)** — Microsoft's documented, file-based project format. Power BI Desktop opens it directly; you then save it as a `.pbix` from inside the app.

> A `.pbix` is a proprietary binary that can only be authored inside Power BI Desktop. PBIP is the supported way to version-control and share a buildable project as plain files — which is exactly why it belongs in a Git repo.

## Contents

```
Mainland_Procurement.pbip            <- open this in Power BI Desktop
Mainland_Procurement.SemanticModel/  <- data model: tables, relationships, DAX measures, KPI (TMDL)
Mainland_Procurement.Report/         <- the 4-page report (PBIR)
```

The model reads its data from the repo's `../data/processed/` CSVs via a parameter.

## Build the `.pbix`

1. **Enable PBIP** (one time): Power BI Desktop -> File -> Options and settings -> Options -> **Preview features** -> tick **"Power BI Project (.pbip) save option"** -> OK -> restart.
2. Open **`Mainland_Procurement.pbip`**.
3. **Transform data -> Edit parameters** and set **DataFolder** to the absolute path of the repo's `data/processed/` folder, *with a trailing slash* — e.g. `C:\Users\you\city-of-mainland\data\processed\`.
4. **Home -> Refresh** (loads 26,357 transactions + dimensions).
5. **File -> Save As -> Power BI report (.pbix)**.

## What's already modelled

**Star schema** — `PurchaseTrans` (fact) -> `DimProduct` -> `DimCategory`, single-direction relationships.

**Measures** — Purchased Amount, Discount Amount, Net Purchase Amount, Total Order Qty, Distinct Products, Distinct Suppliers, and the **Net Purchase KPI** (`SWITCH`: Low < 10K, Medium 10-20K, HIGH > 20K). Source: [`../dax/measures.dax`](../dax/measures.dax).

**Report pages** — Executive Overview, Top 10 by Country, Supplier Discounts, Geographic & Class.

## Note on visuals

The PBIR visual definitions are intentionally minimal so the project opens cleanly across Power BI Desktop versions. The data model and all measures are complete; you may want to fine-tune individual visual formatting after first open, then save.
