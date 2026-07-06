import datetime as dt

from sqlalchemy import (Column, DateTime, Integer, String, Text,
                        UniqueConstraint)

from global_server.database import Base


class Entity(Base):
    """A registered organisation (X-Road 'member')."""
    __tablename__ = "entity"
    id = Column(Integer, primary_key=True)
    entity_class = Column(String(32), nullable=False)
    entity_code = Column(String(64), nullable=False)
    name = Column(String(255))
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    __table_args__ = (UniqueConstraint("entity_class", "entity_code"),)


class Application(Base):
    """An information system of an entity (X-Road 'subsystem')."""
    __tablename__ = "application"
    id = Column(Integer, primary_key=True)
    entity_class = Column(String(32), nullable=False)
    entity_code = Column(String(64), nullable=False)
    application_code = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    __table_args__ = (UniqueConstraint("entity_class", "entity_code", "application_code"),)


class SecurityGateway(Base):
    """A registered security gateway (X-Road 'security server')."""
    __tablename__ = "security_gateway"
    id = Column(Integer, primary_key=True)
    gateway_code = Column(String(64), nullable=False, unique=True)
    owner_class = Column(String(32), nullable=False)
    owner_code = Column(String(64), nullable=False)
    address = Column(String(255), nullable=False)
    auth_cert_pem = Column(Text, nullable=False)
    status = Column(String(16), default="approved")  # pending | approved
    created_at = Column(DateTime, default=dt.datetime.utcnow)


class GatewayApplication(Base):
    """An application registered (hosted) on a security gateway."""
    __tablename__ = "gateway_application"
    id = Column(Integer, primary_key=True)
    gateway_code = Column(String(64), nullable=False)
    instance = Column(String(32), nullable=False)
    entity_class = Column(String(32), nullable=False)
    entity_code = Column(String(64), nullable=False)
    application_code = Column(String(64), nullable=False)
    status = Column(String(16), default="approved")
    created_at = Column(DateTime, default=dt.datetime.utcnow)


class Service(Base):
    """Global service catalog entry (a published provider service)."""
    __tablename__ = "service"
    id = Column(Integer, primary_key=True)
    service_id = Column(String(255), nullable=False, unique=True)  # full id
    instance = Column(String(32))
    entity_class = Column(String(32))
    entity_code = Column(String(64))
    application_code = Column(String(64))
    service_code = Column(String(64))
    gateway_code = Column(String(64))
    description = Column(String(255))
    created_at = Column(DateTime, default=dt.datetime.utcnow)


class Subscription(Base):
    """Central record of a consumer application subscribing to a service."""
    __tablename__ = "subscription"
    id = Column(Integer, primary_key=True)
    subscriber = Column(String(255), nullable=False)   # consumer application id
    service_id = Column(String(255), nullable=False)
    status = Column(String(16), default="approved")    # pending | approved | rejected
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    __table_args__ = (UniqueConstraint("subscriber", "service_id"),)


class TrustedCA(Base):
    __tablename__ = "trusted_ca"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    url = Column(String(255))
    cert_pem = Column(Text, nullable=False)


class TrustedTSA(Base):
    __tablename__ = "trusted_tsa"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    url = Column(String(255))
    cert_pem = Column(Text, nullable=False)


class GlobalKey(Base):
    __tablename__ = "global_key"
    id = Column(Integer, primary_key=True)
    cert_pem = Column(Text, nullable=False)
    key_pem = Column(Text, nullable=False)
    serial = Column(String(64))
    created_at = Column(DateTime, default=dt.datetime.utcnow)
