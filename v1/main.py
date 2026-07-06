"""Global Server (Central Registry). Port 9000. DB: global_registry_db.

Holds the federation registry (entities, applications, security gateways,
hosted applications), the GLOBAL SERVICE CATALOG, central subscriptions and
the approved trust services (CA, TSA). Generates the SIGNED global
configuration consumed by every security gateway.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from global_server import database, registry

app = FastAPI(title="IM Global Server", version="2.0")


class EntityReq(BaseModel):
    entity_class: str
    entity_code: str
    name: str = ""


class ApplicationReq(BaseModel):
    entity_class: str
    entity_code: str
    application_code: str


class GatewayReq(BaseModel):
    gateway_code: str
    owner_class: str
    owner_code: str
    address: str
    auth_cert_pem: str


class GatewayAppReq(BaseModel):
    gateway_code: str
    entity_class: str
    entity_code: str
    application_code: str


class ServiceReq(BaseModel):
    service_id: str
    gateway_code: str
    description: str = ""


class SubscriptionReq(BaseModel):
    subscriber: str
    service_id: str
    status: str = "approved"


class TrustReq(BaseModel):
    name: str
    url: str = ""
    cert_pem: str


@app.on_event("startup")
def _startup():
    database.init()
    try:
        registry.get_or_create_key()
    except Exception as e:
        print(f"[global] signing key provisioning deferred: {e}")


# ---- registration / management API ----
@app.post("/api/entities")
def add_entity(r: EntityReq):
    return registry.add_entity(r.entity_class, r.entity_code, r.name)


@app.post("/api/applications")
def add_application(r: ApplicationReq):
    return registry.add_application(r.entity_class, r.entity_code, r.application_code)


@app.post("/api/gateways")
def register_gateway(r: GatewayReq):
    return registry.register_gateway(r.gateway_code, r.owner_class, r.owner_code,
                                     r.address, r.auth_cert_pem)


@app.post("/api/gateways/{gateway_code}/approve")
def approve_gateway(gateway_code: str):
    return registry.approve_gateway(gateway_code)


@app.post("/api/gateway-applications")
def register_gateway_application(r: GatewayAppReq):
    return registry.register_gateway_application(
        r.gateway_code, r.entity_class, r.entity_code, r.application_code)


@app.post("/api/services")
def register_service(r: ServiceReq):
    return registry.register_service(r.service_id, r.gateway_code, r.description)


@app.post("/api/subscriptions")
def add_subscription(r: SubscriptionReq):
    return registry.add_subscription(r.subscriber, r.service_id, r.status)


@app.post("/api/trusted-ca")
def trusted_ca(r: TrustReq):
    return registry.add_trusted_ca(r.name, r.url, r.cert_pem)


@app.post("/api/trusted-tsa")
def trusted_tsa(r: TrustReq):
    return registry.add_trusted_tsa(r.name, r.url, r.cert_pem)


@app.post("/api/setup-trust")
def setup_trust():
    """Convenience: fetch the CA + TSA certs (server-side) and register them."""
    import httpx
    from common.topology import CA_URL, TSA_URL
    ca = httpx.get(f"{CA_URL}/api/ca-cert", timeout=15).text
    tsa = httpx.get(f"{TSA_URL}/api/tsa-cert", timeout=15).text
    registry.add_trusted_ca("GovStack IM Root CA", CA_URL, ca)
    registry.add_trusted_tsa("GovStack IM TSA", TSA_URL, tsa)
    return {"ok": True, "ca": "registered", "tsa": "registered"}


# ---- update (PUT) API ----
class EntityUpdate(BaseModel):
    name: str = ""


class GatewayUpdate(BaseModel):
    address: str | None = None
    status: str | None = None
    owner_class: str | None = None
    owner_code: str | None = None


class ServiceUpdate(BaseModel):
    description: str | None = None
    gateway_code: str | None = None


@app.put("/api/entities/{entity_class}/{entity_code}")
def update_entity(entity_class: str, entity_code: str, r: EntityUpdate):
    return registry.update_entity(entity_class, entity_code, r.name)


@app.put("/api/gateways/{gateway_code}")
def update_gateway(gateway_code: str, r: GatewayUpdate):
    return registry.update_gateway(gateway_code, r.address, r.status,
                                   r.owner_class, r.owner_code)


@app.put("/api/services")
def update_service(service_id: str, r: ServiceUpdate):
    return registry.update_service(service_id, r.description, r.gateway_code)


# ---- delete API (cascade=true removes dependent records) ----
@app.delete("/api/entities/{entity_class}/{entity_code}")
def delete_entity(entity_class: str, entity_code: str, cascade: bool = False):
    return registry.delete_entity(entity_class, entity_code, cascade)


@app.delete("/api/applications/{entity_class}/{entity_code}/{application_code}")
def delete_application(entity_class: str, entity_code: str, application_code: str,
                       cascade: bool = False):
    return registry.delete_application(entity_class, entity_code, application_code, cascade)


@app.delete("/api/gateways/{gateway_code}")
def delete_gateway(gateway_code: str, cascade: bool = False):
    return registry.delete_gateway(gateway_code, cascade)


@app.delete("/api/gateway-applications/{gateway_code}/{entity_class}/{entity_code}/{application_code}")
def delete_gateway_application(gateway_code: str, entity_class: str, entity_code: str,
                              application_code: str):
    return registry.delete_gateway_application(gateway_code, entity_class, entity_code,
                                               application_code)


@app.delete("/api/services")
def delete_service(service_id: str):
    return registry.delete_service(service_id)


@app.delete("/api/subscriptions")
def delete_subscription(subscriber: str, service_id: str):
    return registry.delete_subscription(subscriber, service_id)


@app.delete("/api/trusted-ca/{name}")
def delete_trusted_ca(name: str):
    return registry.delete_trusted_ca(name)


@app.delete("/api/trusted-tsa/{name}")
def delete_trusted_tsa(name: str):
    return registry.delete_trusted_tsa(name)


# ---- distribution / discovery API ----
@app.get("/api/services")
def services():
    return registry.list_services()


@app.get("/api/globalconf")
def globalconf():
    return registry.signed_globalconf()


@app.get("/api/anchor")
def anchor():
    return registry.anchor()


@app.get("/api/registry")
def registry_view():
    return registry.list_all()


app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static"),
                           html=True), name="static")
