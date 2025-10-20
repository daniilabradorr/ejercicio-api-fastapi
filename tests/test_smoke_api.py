#hago un fluido básico: author -> book -> library_book -> loan -> return -> delete library_book

#los imports
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def _suf():
    return uuid.uuid4().hex[:6]

def test_members_min_crud():
    suf = _suf()
    #creo un miembro
    r = client.post("/members", json={"full_name": f"Socio {suf}", "email": f"socio{suf}@demo.com"})
    assert r.status_code == 201
    member = r.json()

    #conflict por email duplicado
    r = client.post("/members", json={"full_name": "Otro", "email": f"socio{suf}@demo.com"})
    assert r.status_code == 409

    #detalle
    r = client.get(f"/members/{member['id']}")
    assert r.status_code == 200

def test_full_flow_loan_return_delete_copy():
    suf = _suf()

    # 1 autor
    r = client.post("/authors", json={"name": f"Autor-{suf}"})
    assert r.status_code == 201
    author = r.json()

    # 2 libro
    book_payload = {
        "isbn": f"ISBN-{suf}",
        "title": f"Libro {suf}",
        "description": "demo",
        "category": "SciFi",
        "author_id": author["id"],
    }
    r = client.post("/books", json=book_payload)
    assert r.status_code == 201
    book = r.json()

    # 3 miembro
    r = client.post("/members", json={"full_name": f"Socio {suf}", "email": f"socio{suf}@demo.com"})
    assert r.status_code == 201
    member = r.json()

    # 4 ejemplar físico
    r = client.post("/library-books", json={
        "book_id": book["id"],
        "inventory_code": f"INV-{suf}",
        "status": "AVAILABLE",
        "location": "A-1"
    })
    assert r.status_code == 201
    lb = r.json()

    # 5 préstamo (borrow)
    r = client.post("/loans", json={"library_book_id": lb["id"], "member_id": member["id"]})
    assert r.status_code == 201
    loan = r.json()

    # 6 devolver préstamo
    r = client.patch(f"/loans/{loan['id']}", json={"status": "RETURNED"})
    assert r.status_code == 200

    # 7 borrar ejemplar
    r = client.delete(f"/library-books/{lb['id']}")
    assert r.status_code == 204
