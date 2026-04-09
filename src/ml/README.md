# ML scaffold

## Muc tieu

Khung nay duoc tao de:

- train baseline model tu cac bang mart moi
- score du lieu mau de kiem tra flow
- luu artifact va metadata de do tien do

## Bai toan dang scaffold

### Classification

- `late_delivery`
- `low_review`
- `customer_value_tier`
- `seller_risk_band`

### Regression

- `delivery_days_regression`
- `order_value_regression`
- `daily_category_revenue_regression`

## Lenh mau

```bash
python -m src.ml.list_tasks
python -m src.ml.train_model --task late_delivery
python -m src.ml.predict --task late_delivery --limit 50
python -m src.ml.train_model --task order_value_regression
```

## Artifact output

Model va metadata duoc luu trong `src/ml/models/`:

- `<task>.joblib`
- `<task>.json`

## Giai doan tiep theo

- doi query scaffold thanh query toi uu theo bang mart that
- them split theo thoi gian cho backtest
- them logging, experiment tracking, va ghi prediction vao warehouse
- them luu prediction vao prediction facts trong warehouse
- noi semantic output voi lop GenAI / API
