#Uso este script para probar la API en local con requests. Como nos dijiste profe
#Recorro autores, miembros, libros, ejemplares y préstamos.

import os, uuid, sys, time
import requests

BASE = os.getenv("API_URL", "http://127.0.0.1:8000")

def expect(resp, code):
    """si la respuesta no es la esperada, paro y muestro el cuerpo"""
    if resp.status_code != code:
        print(f"\nERROR {resp.request.method} {resp.request.url} "
              f"-> {resp.status_code} (esperado {code})\n{resp.text}\n")
        sys.exit(1)

def main():
    suf = uuid.uuid4().hex[:6]  # sufijo para evitar colisiones únicas
    print(f"BASE={BASE}  sufijo={suf}")

    # 0) health
    r = requests.get(f"{BASE}/health")
    expect(r, 200)
    print("OK /health")

    #autores
    #creo un autor principal (lo usaré para el libro)
    r = requests.post(f"{BASE}/authors", json={"name": f"Autor-{suf}"})
    expect(r, 201)
    author = r.json()
    print("OK POST /authors")

    #creo un segundo autor para probar conflictos y delete
    r = requests.post(f"{BASE}/authors", json={"name": f"Autor2-{suf}"})
    expect(r, 201)
    author2 = r.json()

    #listado + detalle
    expect(requests.get(f"{BASE}/authors"), 200)
    expect(requests.get(f"{BASE}/authors/{author['id']}"), 200)

    #PATCH autor1 (cambio nombre)
    r = requests.patch(f"{BASE}/authors/{author['id']}", json={"name": f"Autor-{suf}-patch"})
    expect(r, 200)
    print("OK PATCH /authors/{id}")

    #Intento poner nombre duplicado -> 409
    r = requests.patch(f"{BASE}/authors/{author['id']}", json={"name": author2["name"]})
    expect(r, 409)
    print("OK conflicto nombre autor 409")

    #PUT autor1 (reemplazo)
    r = requests.put(f"{BASE}/authors/{author['id']}", json={"name": f"Autor-{suf}-put"})
    expect(r, 200)
    print("OK PUT /authors/{id}")

    #DELETE autor2 (está “libre”, debería dejarme)
    r = requests.delete(f"{BASE}/authors/{author2['id']}")
    expect(r, 204)
    print("OK DELETE /authors/{id}")

    # miembros
    r = requests.post(f"{BASE}/members",
                      json={"full_name": f"Socio {suf}", "email": f"socio{suf}@demo.com"})
    expect(r, 201)
    member = r.json()
    print("OK POST /members")

    #duplique email -> 409
    r = requests.post(f"{BASE}/members",
                      json={"full_name": "Socio Duplicado", "email": f"socio{suf}@demo.com"})
    expect(r, 409)
    print("OK conflicto email miembro 409")

    #PATCH bloqueo
    r = requests.patch(f"{BASE}/members/{member['id']}", json={"blocked": False})
    expect(r, 200)

    #libros
    #creo libro con el autor principal
    book_payload = {
        "isbn": f"ISBN-{suf}",
        "title": f"Libro {suf}",
        "description": "demo",
        "category": "SciFi",
        "author_id": author["id"]
    }
    r = requests.post(f"{BASE}/books", json=book_payload)
    expect(r, 201)
    book = r.json()
    print("OK POST /books")

    #duplique ISBN -> 409
    r = requests.post(f"{BASE}/books", json=book_payload)
    expect(r, 409)
    print("OK conflicto ISBN 409")

    #PATCH título
    r = requests.patch(f"{BASE}/books/{book['id']}", json={"title": f"Libro {suf} PATCH"})
    expect(r, 200)
    print("OK PATCH /books/{id}")

    #libreria-lirbos relacion
    r = requests.post(f"{BASE}/library-books",
                      json={"book_id": book["id"],
                            "inventory_code": f"INV-{suf}",
                            "status": "AVAILABLE",
                            "location": "A-1"})
    expect(r, 201)
    lb = r.json()
    print("OK POST /library-books")

    #listado filtrando por AVAILABLE
    expect(requests.get(f"{BASE}/library-books", params={"status_": "AVAILABLE"}), 200)

    # prestamos
    # borrow
    r = requests.post(f"{BASE}/loans",
                      json={"library_book_id": lb["id"], "member_id": member["id"]})
    expect(r, 201)
    loan = r.json()
    print("OK POST /loans (borrow)")

    #intentar borrar el ejemplar con préstamo activo -> 409
    r = requests.delete(f"{BASE}/library-books/{lb['id']}")
    expect(r, 409)
    print("OK bloqueo delete ejemplar con préstamo 409")

    #return
    r = requests.patch(f"{BASE}/loans/{loan['id']}", json={"status": "RETURNED"})
    expect(r, 200)
    print("OK PATCH /loans/{id} RETURNED")

    #ahora sí, borrar el ejemplar -> 204
    r = requests.delete(f"{BASE}/library-books/{lb['id']}")
    expect(r, 204)
    print("OK DELETE /library-books/{id}")

    #listados finales
    expect(requests.get(f"{BASE}/authors"), 200)
    expect(requests.get(f"{BASE}/books"), 200)
    expect(requests.get(f"{BASE}/members"), 200)
    expect(requests.get(f"{BASE}/loans"), 200)

    print("\n✅ Todo OK. test obligatorio para la finalizacon del ejercicio completado.")

if __name__ == "__main__":
    main()