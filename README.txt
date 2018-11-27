DATA MODELS: https://app.quickdatabasediagrams.com/#/d/2ZG81I
DOCS: https://docs.google.com/document/d/1d-RCtdjtqnSYYRUpeGUaGbdhHT9O5UNRMva8g_1ABl0/edit



curl http://0.0.0.0:5000/api/users/3/movielist -XPOST -d '{"movie_id": "45346"}' -H 'Content-Type: application/json' -v
curl http://0.0.0.0:5000/api/users/3/movielist -v
