"""Test fixtures. Tests run against a throw-away SQLite file built by the real Alembic migration,
so the development database is never touched and migrations are exercised on every run."""
import pytest
from uuid import uuid4
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from app.core.config import BACKEND_DIR
from app.db.session import build_engine
from app.dependencies import get_db
from app.main import app
from app.core.config import settings
from app.services import payment_service


@pytest.fixture(scope="session")
def test_engine(tmp_path_factory):
    db_file = tmp_path_factory.mktemp("db") / "test.db"
    url = f"sqlite:///{db_file.as_posix()}"
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", url)
    command.upgrade(cfg, "head")
    engine = build_engine(url)
    yield engine
    engine.dispose()


@pytest.fixture(autouse=True)
def clean_tables(test_engine):
    """Every test starts from empty tables, so tests are independent of execution order."""
    with test_engine.begin() as conn:
        conn.execute(text("DELETE FROM payments"))
        conn.execute(text("DELETE FROM appointments"))
        conn.execute(text("DELETE FROM doctors"))
        conn.execute(text("DELETE FROM users"))
    yield


@pytest.fixture
def session_factory(test_engine):
    return sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)


@pytest.fixture
def client(session_factory, monkeypatch):
    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr(settings, "razorpay_key_id", "rzp_test_key")
    monkeypatch.setattr(settings, "razorpay_key_secret", "rzp_test_secret")

    class FakeRazorpayClient:
        class Orders:
            @staticmethod
            def create(_payload):
                return {"id": f"order_test_{uuid4().hex}"}

        order = Orders()

    monkeypatch.setattr(payment_service, "_razorpay_client", lambda: FakeRazorpayClient())
    # raise_server_exceptions=False so we can assert on the 500 envelope for unexpected errors
    with TestClient(app, raise_server_exceptions=False) as c:
        session = c.post(
            "/auth/register",
            json={"username": "test-patient", "password": "secret-password", "name": "Jane Doe", "role": "patient"},
        )
        assert session.status_code == 201, session.text
        c.headers["Authorization"] = f"Bearer {session.json()['access_token']}"
        yield c
    app.dependency_overrides.clear()


DOCTOR = {"name": "Dr. Test", "specialization": "General", "start_hour": 9, "end_hour": 17}
DAY = "2030-10-20"


@pytest.fixture
def make_doctor(client):
    def _make(**overrides):
        doctor = {
            "username": f"doctor-{uuid4().hex[:10]}",
            "password": "secret-password",
            "name": DOCTOR["name"],
            "role": "doctor",
            "specialization": DOCTOR["specialization"],
            "start_hour": DOCTOR["start_hour"],
            "end_hour": DOCTOR["end_hour"],
            "fee_paise": 50000,
        }
        doctor.update(overrides)
        response = client.post("/auth/register", json=doctor)
        assert response.status_code == 201, response.text
        result = client.get(f"/doctors/{response.json()['user']['doctor_id']}")
        assert result.status_code == 200, result.text
        return {**result.json(), "token": response.json()["access_token"]}

    return _make


@pytest.fixture
def book(client):
    def _book(doctor_id, time="10:00:00", patient="Jane Doe", day=DAY):
        order = client.post(
            "/payments/orders", json={"doctor_id": doctor_id, "slot": f"{day}T{time}"}
        )
        if order.status_code != 201:
            return order
        order_data = order.json()
        payment_id = f"pay_test_{uuid4().hex}"
        import hashlib
        import hmac

        signature = hmac.new(
            settings.razorpay_key_secret.encode(),
            f"{order_data['order_id']}|{payment_id}".encode(),
            hashlib.sha256,
        ).hexdigest()
        return client.post("/payments/verify", json={
            "appointment_id": order_data["appointment_id"],
            "razorpay_order_id": order_data["order_id"],
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        })

    return _book
