# ML scaffold

## Muc tieu

Khung ML duoc thu gon de phuc vu 3 bai toan tieu bieu, tranh mo rong mart qua nhieu nhung van bao phu du 3 nhom nghiep vu quan trong:

- demand planning: san pham nao co kha nang ban chay
- order operations: don hang nao co kha nang hoan tat thanh cong
- regional planning: khu vuc nao co nhu cau mua hang cao

## Bai toan dang ho tro

| Task | Source mart | Grain | Target |
| --- | --- | --- | --- |
| `product_bestseller` | `marts.fact_ml_product_demand` | 1 product / ngay co ban | Co thuoc top demand trong 7 ngay toi |
| `order_success` | `marts.fact_ml_order_success` | 1 order | Don co kha nang thanh cong/giao thanh cong |
| `geo_high_demand` | `marts.fact_ml_geo_demand` | 1 city-state / ngay co ban | Khu vuc co nhu cau cao trong 7 ngay toi |

## Cau truc code

- `tasks.py`: catalog 3 bai toan, SQL, target, feature va cau hoi mau.
- `service.py`: doc mart, train model, luu artifact, predict, gan band/action va tao summary cho GenAI/API.
- `list_tasks.py`, `train_model.py`, `predict.py`: CLI entrypoint mong.

## Lenh mau

```bash
python -m src.ml.list_tasks
python -m src.ml.train_model --task product_bestseller
python -m src.ml.predict --task product_bestseller --limit 50
python -m src.ml.train_model --task order_success
python -m src.ml.train_model --task geo_high_demand
```

## Artifact output

Model va metadata duoc luu trong `src/ml/models/`:

- `<task>.joblib`
- `<task>.json`

## Giai doan tiep theo

- them backtest rolling-window cho 2 bai toan next-7-day
- them feature importance/SHAP de giai thich vi sao model goi y san pham/khu vuc
- ghi prediction output vao warehouse neu can lam dashboard theo lich
