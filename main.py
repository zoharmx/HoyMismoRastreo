import os
import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")

# URL de HubSpot para consultar contactos
HUBSPOT_SEARCH_URL = "https://api.hubapi.com/crm/v3/objects/contacts/search"

@app.get("/consultar-envio")
def consultar_envio(email: str):
    """
    Consulta en HubSpot las propiedades del contacto relacionadas al envío/paquete,
    basándose en el email.
    """
    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "filterGroups": [{
            "filters": [{
                "propertyName": "email",
                "operator": "EQ",
                "value": email
            }]
        }],
        "properties": [
            "firstname",
            "estatus",
            "destino",
            "tracking_id",
            "fecha_de_recoleccion",
            "nombre_del_receptor",  # Asegúrate de usar el nombre correcto
            "tamano_de_la_caja",
            "peso_del_paquete",
            "phone",
            "hs_whatsapp_phone_number",
            "address"
        ]
    }
    response = requests.post(HUBSPOT_SEARCH_URL, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if "results" in data and len(data["results"]) > 0:
            contacto = data["results"][0]["properties"]
            return {
                "estatus": contacto.get("estatus", "No disponible"),
                "nombre": contacto.get("firstname", "No disponible"),
                "destino": contacto.get("destino", "No disponible"),
                "numero_guia": contacto.get("tracking_id", "No disponible"),
                "fecha_de_recoleccion": contacto.get("fecha_de_recoleccion", "No disponible"),
                "nombre_del_receptor": contacto.get("nombre_del_receptor", "No disponible"),
                "tamano_de_la_caja": contacto.get("tamano_de_la_caja", "No disponible"),
                "peso_del_paquete": contacto.get("peso_del_paquete", "No disponible"),
                "telefono": contacto.get("phone", "No disponible"),
                "whatsapp": contacto.get("hs_whatsapp_phone_number", "No disponible"),
                "direccion": contacto.get("address", "No disponible")
            }
        else:
            return {"error": "No se encontró el contacto con ese correo."}
    else:
        return {
            "error": f"Error en la consulta a HubSpot: {response.status_code} - {response.text}"
        }

@app.get("/consultar-envio-html", response_class=HTMLResponse)
def consultar_envio_html(email: str):
    """
    Consulta en HubSpot y retorna la información en formato HTML.
    """
    info = consultar_envio(email)
    if "error" in info:
        return f"<html><body><h1>Error: {info['error']}</h1></body></html>"
    html_content = "<html><head><title>Información del Envío</title></head><body>"
    html_content += "<h1>Información del Envío</h1>"
    html_content += "<table border='1'>"
    for key, value in info.items():
        html_content += f"<tr><td>{key}</td><td>{value}</td></tr>"
    html_content += "</table></body></html>"
    return html_content
