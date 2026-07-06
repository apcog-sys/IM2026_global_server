"""Global registry + signed global-configuration generation.

The Global Server is the federation's source of truth: entities,
applications, security gateways and their hosted applications, the global
service catalog, central subscriptions, and the trusted CA(s)/TSA(s). It
packages trust + topology into a *signed global configuration* that every
security gateway downloads and verifies.
"""
import datetime as dt

import httpx

from common import crypto
from common.topology import CA_URL, INSTANCE
from common.util import canonical_json
from global_server import models
from global_server.database import SessionLocal


# --------------------------------------------------------------------------
# Config-signing key (issued by the CA -> acts as the configuration anchor)
# --------------------------------------------------------------------------

def get_or_create_key():
    db = SessionLocal()
    try:
        rec = db.query(models.GlobalKey).first()
        if rec:
            return rec
        key = crypto.generate_rsa_key()
        csr = crypto.create_csr(key, "Information Mediator Global Server",
                                org="GovStack IM", org_unit="GlobalConf")
        resp = httpx.post(f"{CA_URL}/api/sign",
                          json={"csr_pem": csr, "profile": crypto.PROFILE_SIGN,
                                "requested_by": "global_server"}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        rec = models.GlobalKey(cert_pem=data["cert_pem"],
                               key_pem=crypto.key_to_pem(key), serial=data["serial"])
        db.add(rec)
        db.commit()
        db.refresh(rec)
        return rec
    finally:
        db.close()


# --------------------------------------------------------------------------
# Registration / management operations
# --------------------------------------------------------------------------

def add_entity(entity_class, entity_code, name):
    db = SessionLocal()
    try:
        if not db.query(models.Entity).filter_by(
                entity_class=entity_class, entity_code=entity_code).first():
            db.add(models.Entity(entity_class=entity_class, entity_code=entity_code,
                                 name=name))
            db.commit()
        return {"ok": True}
    finally:
        db.close()


def add_application(entity_class, entity_code, application_code):
    db = SessionLocal()
    try:
        if not db.query(models.Application).filter_by(
                entity_class=entity_class, entity_code=entity_code,
                application_code=application_code).first():
            db.add(models.Application(entity_class=entity_class, entity_code=entity_code,
                                      application_code=application_code))
            db.commit()
        return {"ok": True}
    finally:
        db.close()


def register_gateway(gateway_code, owner_class, owner_code, address,
                     auth_cert_pem, auto_approve=True):
    db = SessionLocal()
    try:
        rec = db.query(models.SecurityGateway).filter_by(gateway_code=gateway_code).first()
        status = "approved" if auto_approve else "pending"
        if rec:
            rec.address = address
            rec.auth_cert_pem = auth_cert_pem
            rec.owner_class = owner_class
            rec.owner_code = owner_code
            rec.status = status
        else:
            rec = models.SecurityGateway(
                gateway_code=gateway_code, owner_class=owner_class, owner_code=owner_code,
                address=address, auth_cert_pem=auth_cert_pem, status=status)
            db.add(rec)
        db.commit()
        return {"ok": True, "status": status}
    finally:
        db.close()


def approve_gateway(gateway_code):
    db = SessionLocal()
    try:
        rec = db.query(models.SecurityGateway).filter_by(gateway_code=gateway_code).first()
        if not rec:
            return {"ok": False}
        rec.status = "approved"
        db.commit()
        return {"ok": True}
    finally:
        db.close()


def register_gateway_application(gateway_code, entity_class, entity_code,
                                 application_code, instance=INSTANCE, auto_approve=True):
    db = SessionLocal()
    try:
        existing = db.query(models.GatewayApplication).filter_by(
            gateway_code=gateway_code, entity_class=entity_class,
            entity_code=entity_code, application_code=application_code).first()
        status = "approved" if auto_approve else "pending"
        if existing:
            existing.status = status
        else:
            db.add(models.GatewayApplication(
                gateway_code=gateway_code, instance=instance, entity_class=entity_class,
                entity_code=entity_code, application_code=application_code, status=status))
        db.commit()
        return {"ok": True, "status": status}
    finally:
        db.close()


def register_service(service_id, gateway_code, description="", instance=INSTANCE):
    parts = service_id.strip("/").split("/")
    db = SessionLocal()
    try:
        rec = db.query(models.Service).filter_by(service_id=service_id).first()
        if rec:
            rec.gateway_code = gateway_code
            rec.description = description
        else:
            db.add(models.Service(
                service_id=service_id, instance=parts[0], entity_class=parts[1],
                entity_code=parts[2], application_code=parts[3], service_code=parts[4],
                gateway_code=gateway_code, description=description))
        db.commit()
        return {"ok": True}
    finally:
        db.close()


def add_subscription(subscriber, service_id, status="approved"):
    db = SessionLocal()
    try:
        rec = db.query(models.Subscription).filter_by(
            subscriber=subscriber, service_id=service_id).first()
        if rec:
            rec.status = status
        else:
            db.add(models.Subscription(subscriber=subscriber, service_id=service_id,
                                       status=status))
        db.commit()
        return {"ok": True, "status": status}
    finally:
        db.close()


def add_trusted_ca(name, url, cert_pem):
    db = SessionLocal()
    try:
        rec = db.query(models.TrustedCA).filter_by(name=name).first()
        if rec:
            rec.url, rec.cert_pem = url, cert_pem
        else:
            db.add(models.TrustedCA(name=name, url=url, cert_pem=cert_pem))
        db.commit()
        return {"ok": True}
    finally:
        db.close()


def add_trusted_tsa(name, url, cert_pem):
    db = SessionLocal()
    try:
        rec = db.query(models.TrustedTSA).filter_by(name=name).first()
        if rec:
            rec.url, rec.cert_pem = url, cert_pem
        else:
            db.add(models.TrustedTSA(name=name, url=url, cert_pem=cert_pem))
        db.commit()
        return {"ok": True}
    finally:
        db.close()


# --------------------------------------------------------------------------
# Delete operations
# --------------------------------------------------------------------------

def _delete(model, **filters) -> int:
    db = SessionLocal()
    try:
        n = db.query(model).filter_by(**filters).delete()
        db.commit()
        return n
    finally:
        db.close()


def delete_entity(entity_class, entity_code, cascade=False):
    if not cascade:
        return {"deleted": _delete(models.Entity, entity_class=entity_class,
                                   entity_code=entity_code)}
    db = SessionLocal()
    try:
        tok = f"/{entity_class}/{entity_code}/"
        removed = 0
        for s in db.query(models.Subscription).all():
            if tok in s.subscriber or tok in s.service_id:
                db.delete(s)
                removed += 1
        removed += db.query(models.Service).filter_by(
            entity_class=entity_class, entity_code=entity_code).delete()
        removed += db.query(models.GatewayApplication).filter_by(
            entity_class=entity_class, entity_code=entity_code).delete()
        removed += db.query(models.Application).filter_by(
            entity_class=entity_class, entity_code=entity_code).delete()
        removed += db.query(models.Entity).filter_by(
            entity_class=entity_class, entity_code=entity_code).delete()
        db.commit()
        return {"deleted": removed, "cascade": True}
    finally:
        db.close()


def delete_application(entity_class, entity_code, application_code, cascade=False):
    if not cascade:
        return {"deleted": _delete(models.Application, entity_class=entity_class,
                                   entity_code=entity_code, application_code=application_code)}
    db = SessionLocal()
    try:
        prov = f"/{entity_class}/{entity_code}/{application_code}/"
        cons = f"/{entity_class}/{entity_code}/{application_code}"
        removed = 0
        for s in db.query(models.Subscription).all():
            if prov in s.service_id or s.subscriber.endswith(cons):
                db.delete(s)
                removed += 1
        removed += db.query(models.Service).filter_by(
            entity_class=entity_class, entity_code=entity_code,
            application_code=application_code).delete()
        removed += db.query(models.GatewayApplication).filter_by(
            entity_class=entity_class, entity_code=entity_code,
            application_code=application_code).delete()
        removed += db.query(models.Application).filter_by(
            entity_class=entity_class, entity_code=entity_code,
            application_code=application_code).delete()
        db.commit()
        return {"deleted": removed, "cascade": True}
    finally:
        db.close()


def delete_gateway(gateway_code, cascade=False):
    if not cascade:
        return {"deleted": _delete(models.SecurityGateway, gateway_code=gateway_code)}
    db = SessionLocal()
    try:
        service_ids = [s.service_id for s in db.query(models.Service).filter_by(
            gateway_code=gateway_code).all()]
        removed = 0
        for s in db.query(models.Subscription).all():
            if s.service_id in service_ids:
                db.delete(s)
                removed += 1
        removed += db.query(models.Service).filter_by(gateway_code=gateway_code).delete()
        removed += db.query(models.GatewayApplication).filter_by(
            gateway_code=gateway_code).delete()
        removed += db.query(models.SecurityGateway).filter_by(
            gateway_code=gateway_code).delete()
        db.commit()
        return {"deleted": removed, "cascade": True}
    finally:
        db.close()


# --------------------------------------------------------------------------
# Update (PUT) operations
# --------------------------------------------------------------------------

def update_entity(entity_class, entity_code, name):
    db = SessionLocal()
    try:
        rec = db.query(models.Entity).filter_by(
            entity_class=entity_class, entity_code=entity_code).first()
        if not rec:
            return {"updated": 0}
        rec.name = name
        db.commit()
        return {"updated": 1}
    finally:
        db.close()


def update_gateway(gateway_code, address=None, status=None,
                   owner_class=None, owner_code=None):
    db = SessionLocal()
    try:
        rec = db.query(models.SecurityGateway).filter_by(gateway_code=gateway_code).first()
        if not rec:
            return {"updated": 0}
        if address is not None:
            rec.address = address
        if status is not None:
            rec.status = status
        if owner_class is not None:
            rec.owner_class = owner_class
        if owner_code is not None:
            rec.owner_code = owner_code
        db.commit()
        return {"updated": 1}
    finally:
        db.close()


def update_service(service_id, description=None, gateway_code=None):
    db = SessionLocal()
    try:
        rec = db.query(models.Service).filter_by(service_id=service_id).first()
        if not rec:
            return {"updated": 0}
        if description is not None:
            rec.description = description
        if gateway_code is not None:
            rec.gateway_code = gateway_code
        db.commit()
        return {"updated": 1}
    finally:
        db.close()


def delete_gateway_application(gateway_code, entity_class, entity_code, application_code):
    return {"deleted": _delete(models.GatewayApplication, gateway_code=gateway_code,
                               entity_class=entity_class, entity_code=entity_code,
                               application_code=application_code)}


def delete_service(service_id):
    return {"deleted": _delete(models.Service, service_id=service_id)}


def delete_subscription(subscriber, service_id):
    return {"deleted": _delete(models.Subscription, subscriber=subscriber,
                               service_id=service_id)}


def delete_trusted_ca(name):
    return {"deleted": _delete(models.TrustedCA, name=name)}


def delete_trusted_tsa(name):
    return {"deleted": _delete(models.TrustedTSA, name=name)}


# --------------------------------------------------------------------------
# Service catalog (consumed by gateways for catalog sync)
# --------------------------------------------------------------------------

def list_services():
    db = SessionLocal()
    try:
        return [{"service_id": s.service_id, "gateway_code": s.gateway_code,
                 "provider": f"{s.instance}/{s.entity_class}/{s.entity_code}/{s.application_code}",
                 "service_code": s.service_code, "description": s.description}
                for s in db.query(models.Service).order_by(models.Service.service_id).all()]
    finally:
        db.close()


# --------------------------------------------------------------------------
# Global configuration document
# --------------------------------------------------------------------------

def build_globalconf() -> dict:
    db = SessionLocal()
    try:
        entities = []
        for e in db.query(models.Entity).all():
            apps = [a.application_code for a in db.query(models.Application).filter_by(
                entity_class=e.entity_class, entity_code=e.entity_code).all()]
            entities.append({"entity_class": e.entity_class, "entity_code": e.entity_code,
                             "name": e.name, "applications": apps})

        gateways = []
        for gw in db.query(models.SecurityGateway).filter_by(status="approved").all():
            hosted = [f"{a.instance}/{a.entity_class}/{a.entity_code}/{a.application_code}"
                      for a in db.query(models.GatewayApplication).filter_by(
                          gateway_code=gw.gateway_code, status="approved").all()]
            gateways.append({"gateway_code": gw.gateway_code,
                             "owner": f"{gw.owner_class}/{gw.owner_code}",
                             "address": gw.address, "auth_cert_pem": gw.auth_cert_pem,
                             "applications": hosted})

        cas = [c.cert_pem for c in db.query(models.TrustedCA).all()]
        tsas = [{"url": t.url, "cert_pem": t.cert_pem}
                for t in db.query(models.TrustedTSA).all()]
        services = [{"service_id": s.service_id, "gateway_code": s.gateway_code,
                     "description": s.description} for s in db.query(models.Service).all()]

        return {
            "instance": INSTANCE,
            "generated_at": dt.datetime.utcnow().isoformat() + "Z",
            "entities": entities,
            "security_gateways": gateways,
            "services": services,
            "trusted_cas": cas,
            "trusted_tsas": tsas,
            "global_settings": {"ocsp_fresh_seconds": 3600,
                                "time_stamping_required": True},
        }
    finally:
        db.close()


def signed_globalconf() -> dict:
    rec = get_or_create_key()
    conf = build_globalconf()
    signature = crypto.sign_bytes(canonical_json(conf), crypto.load_key(rec.key_pem))
    return {"conf": conf, "signature": signature, "signer_cert_pem": rec.cert_pem}


def anchor() -> dict:
    rec = get_or_create_key()
    ca_pem = httpx.get(f"{CA_URL}/api/ca-cert", timeout=15).text
    return {"instance": INSTANCE, "global_signer_cert_pem": rec.cert_pem,
            "ca_cert_pem": ca_pem}


# --------------------------------------------------------------------------
# Read helpers for the UI
# --------------------------------------------------------------------------

def list_all() -> dict:
    db = SessionLocal()
    try:
        return {
            "entities": [{"entity": f"{e.entity_class}/{e.entity_code}", "name": e.name}
                         for e in db.query(models.Entity).all()],
            "applications": [{"entity": f"{a.entity_class}/{a.entity_code}",
                              "application": a.application_code}
                             for a in db.query(models.Application).all()],
            "security_gateways": [{"gateway_code": g.gateway_code,
                                   "owner": f"{g.owner_class}/{g.owner_code}",
                                   "address": g.address, "status": g.status}
                                  for g in db.query(models.SecurityGateway).all()],
            "gateway_applications": [{"gateway_code": a.gateway_code,
                                      "application": f"{a.instance}/{a.entity_class}/{a.entity_code}/{a.application_code}",
                                      "status": a.status}
                                     for a in db.query(models.GatewayApplication).all()],
            "services": list_services(),
            "subscriptions": [{"subscriber": s.subscriber, "service_id": s.service_id,
                               "status": s.status} for s in db.query(models.Subscription).all()],
            "trusted_cas": [{"name": c.name, "url": c.url} for c in db.query(models.TrustedCA).all()],
            "trusted_tsas": [{"name": t.name, "url": t.url} for t in db.query(models.TrustedTSA).all()],
        }
    finally:
        db.close()
