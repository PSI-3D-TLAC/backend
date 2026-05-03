# 3D PrintHub — Mock Backend

A minimal Flask backend that returns mock data so the frontend can be exercised
end-to-end without any real database, payment gateway, supplier API, etc.

## Layout

Each domain package under `src/classes/<Package>/` ships a tiny `mock.py`
module with hardcoded data and a few helper functions. `src/server/routes.py`
exposes thin HTTP endpoints that delegate to those mocks.

```
src/
├── classes/
│   ├── Catalog/mock.py
│   ├── Delivery/mock.py
│   ├── Inventory/mock.py
│   ├── OrderManagment/mock.py
│   ├── Payment/mock.py
│   ├── SupplierIntegration/mock.py
│   ├── Support/mock.py
│   └── UserManagment/mock.py
├── server/
│   ├── app.py        # Flask factory + permissive CORS
│   └── routes.py     # All blueprints
main.py               # Entry point (python main.py)
```

## Install

From the project root:

```
pip install -r requirements.txt
```

## Run

```
python main.py
```

The server listens on `http://127.0.0.1:5000` and accepts requests from any
origin (CORS `*`).

## Demo credentials

All sample users use password `test`:

| Role            | Email                  |
| --------------- | ---------------------- |
| Customer        | anna@example.com       |
| Admin           | admin@example.com      |
| WarehouseWorker | ware@example.com       |
| Manager         | manager@example.com    |
| Carrier         | carrier@example.com    |
| Support         | support@example.com    |
| Employee        | emp@example.com        |

## Endpoints

| Method | Path                                | Purpose                                |
| ------ | ----------------------------------- | -------------------------------------- |
| GET    | `/health`                           | Health check                           |
| POST   | `/auth/login`                       | Mock login, returns token + user       |
| POST   | `/auth/logout`                      | Mock logout                            |
| GET    | `/users`                            | List users + roles                     |
| GET    | `/catalog/products`                 | List products (`?active=1`)            |
| POST   | `/catalog/products`                 | Create product                         |
| GET    | `/catalog/products/{id}`            | Get product                            |
| PUT    | `/catalog/products/{id}`            | Update product                         |
| DELETE | `/catalog/products/{id}`            | Delete product                         |
| GET    | `/inventory/materials`              | List materials (`?q=...`)              |
| GET    | `/orders`                           | List orders + valid statuses           |
| POST   | `/orders`                           | Create order (returns mock estimates)  |
| GET    | `/orders/{id}`                      | Get order detail                       |
| PUT    | `/orders/{id}/status`               | Update order status                    |
| POST   | `/payments/pay`                     | Simulate payment (use `forceFail`)     |
| GET    | `/delivery/options`                 | Carriers + delivery options            |
| POST   | `/delivery/shipments`               | Create shipment                        |
| PUT    | `/delivery/shipments/{id}/status`   | Update shipment status                 |
| GET    | `/support/requests`                 | List support requests                  |
| POST   | `/support/requests`                 | Create support request                 |
| GET    | `/support/complaints`               | List complaints + valid reasons        |
| POST   | `/support/complaints`               | Create complaint                       |
| GET    | `/suppliers`                        | List suppliers                         |
| POST   | `/suppliers`                        | Register supplier                      |
| POST   | `/suppliers/{id}/import-products`   | Import products from external link     |

## Example requests

```bash
# Login
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"anna@example.com","password":"test"}'

# Logout
curl -X POST http://127.0.0.1:5000/auth/logout \
  -H "Content-Type: application/json" \
  -d '{"token":"PASTE_TOKEN_HERE"}'

# Users + roles
curl http://127.0.0.1:5000/users

# Catalog
curl http://127.0.0.1:5000/catalog/products
curl -X POST http://127.0.0.1:5000/catalog/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Robot","description":"Toy","price":29.0,"category":"Toys","isActive":true}'
curl -X PUT http://127.0.0.1:5000/catalog/products/1 \
  -H "Content-Type: application/json" -d '{"price": 12.50}'
curl -X DELETE http://127.0.0.1:5000/catalog/products/3

# Inventory
curl "http://127.0.0.1:5000/inventory/materials?q=PLA"

# Orders
curl -X POST http://127.0.0.1:5000/orders \
  -H "Content-Type: application/json" \
  -d '{"customerId":1,"items":[{"productId":1,"materialId":1,"precision":"high","split":false,"quantity":2}]}'
curl http://127.0.0.1:5000/orders/1
curl -X PUT http://127.0.0.1:5000/orders/1/status \
  -H "Content-Type: application/json" -d '{"status":"Confirmed"}'

# Payment (success)
curl -X POST http://127.0.0.1:5000/payments/pay \
  -H "Content-Type: application/json" \
  -d '{"orderId":1,"amount":29.80,"method":"card"}'
# Payment (forced failure)
curl -X POST http://127.0.0.1:5000/payments/pay \
  -H "Content-Type: application/json" \
  -d '{"orderId":1,"amount":29.80,"method":"card","forceFail":true}'

# Delivery
curl http://127.0.0.1:5000/delivery/options
curl -X POST http://127.0.0.1:5000/delivery/shipments \
  -H "Content-Type: application/json" \
  -d '{"orderId":1,"deliveryOptionId":2,"orderTotal":29.80}'
curl -X PUT http://127.0.0.1:5000/delivery/shipments/1/status \
  -H "Content-Type: application/json" -d '{"status":"Sent"}'

# Support
curl -X POST http://127.0.0.1:5000/support/requests \
  -H "Content-Type: application/json" \
  -d '{"orderId":1,"type":"change","description":"Add another item"}'
curl -X POST http://127.0.0.1:5000/support/complaints \
  -H "Content-Type: application/json" \
  -d '{"orderId":1,"reason":"damaged","description":"Cracked vase"}'

# Suppliers
curl http://127.0.0.1:5000/suppliers
curl -X POST http://127.0.0.1:5000/suppliers \
  -H "Content-Type: application/json" \
  -d '{"name":"NewSupplier","address":"Praha","contact":"hi@new.cz"}'
# OK import
curl -X POST http://127.0.0.1:5000/suppliers/1/import-products \
  -H "Content-Type: application/json" -d '{"link":"https://example.com/catalog"}'
# Failure cases (invalid_link / access_denied / import_failed)
curl -X POST http://127.0.0.1:5000/suppliers/1/import-products \
  -H "Content-Type: application/json" -d '{"link":"not-a-url"}'
curl -X POST http://127.0.0.1:5000/suppliers/1/import-products \
  -H "Content-Type: application/json" -d '{"link":"https://example.com/denied"}'
curl -X POST http://127.0.0.1:5000/suppliers/1/import-products \
  -H "Content-Type: application/json" -d '{"link":"https://example.com/fail"}'
```

## Notes

- Data lives only in memory: restarting the server resets all state.
- Authentication is mock-only — endpoints are not actually protected.
- The `wannabe-dbms` folder is kept as-is; the mock backend uses plain Python
  dictionaries which mirror its idea but do not depend on it.
