"""Backend API tests for e-commerce app"""
import os
import uuid
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://ecommerce-hub-1993.preview.emergentagent.com').rstrip('/')
API = f"{BASE_URL}/api"

ADMIN_EMAIL = "admin@eshop.com"
ADMIN_PASSWORD = "admin123"


@pytest.fixture(scope="session")
def admin_token():
    r = requests.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert r.status_code == 200, f"Admin login failed: {r.text}"
    return r.json()["token"]


@pytest.fixture(scope="session")
def customer():
    email = f"TEST_user_{uuid.uuid4().hex[:8]}@example.com"
    r = requests.post(f"{API}/auth/register", json={"email": email, "password": "pass1234", "name": "TEST User"})
    assert r.status_code == 200, f"Register failed: {r.text}"
    data = r.json()
    return {"token": data["token"], "id": data["user"]["id"], "email": email}


@pytest.fixture(scope="session")
def admin_h(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="session")
def cust_h(customer):
    return {"Authorization": f"Bearer {customer['token']}"}


# ---------- Auth ----------
class TestAuth:
    def test_login_invalid(self):
        r = requests.post(f"{API}/auth/login", json={"email": "no@x.com", "password": "x"})
        assert r.status_code == 401

    def test_admin_login(self, admin_token):
        assert isinstance(admin_token, str) and len(admin_token) > 10

    def test_me(self, cust_h):
        r = requests.get(f"{API}/auth/me", headers=cust_h)
        assert r.status_code == 200
        assert r.json()["role"] == "customer"


# ---------- Categories CRUD ----------
class TestCategories:
    cat_id = None

    def test_list_categories(self):
        r = requests.get(f"{API}/categories")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_create_category(self, admin_h):
        payload = {"name": "TEST_Cat", "slug": f"test-cat-{uuid.uuid4().hex[:6]}", "description": "d", "active": True}
        r = requests.post(f"{API}/categories", json=payload, headers=admin_h)
        assert r.status_code == 200, r.text
        TestCategories.cat_id = r.json()["id"]
        assert r.json()["name"] == "TEST_Cat"

    def test_get_category(self):
        r = requests.get(f"{API}/categories/{TestCategories.cat_id}")
        assert r.status_code == 200

    def test_update_category(self, admin_h):
        payload = {"name": "TEST_Cat_Up", "slug": f"test-cat-up-{uuid.uuid4().hex[:6]}", "active": True}
        r = requests.put(f"{API}/categories/{TestCategories.cat_id}", json=payload, headers=admin_h)
        assert r.status_code == 200
        assert r.json()["name"] == "TEST_Cat_Up"

    def test_create_without_admin(self, cust_h):
        r = requests.post(f"{API}/categories", json={"name": "x", "slug": "x"}, headers=cust_h)
        assert r.status_code == 403


# ---------- Products CRUD ----------
class TestProducts:
    pid = None

    def test_list(self):
        r = requests.get(f"{API}/products")
        assert r.status_code == 200

    def test_create(self, admin_h):
        payload = {"name": "TEST_P", "slug": f"test-p-{uuid.uuid4().hex[:6]}", "description": "d",
                   "price": 99.0, "images": [], "category_id": TestCategories.cat_id or "x", "stock": 5}
        r = requests.post(f"{API}/products", json=payload, headers=admin_h)
        assert r.status_code == 200, r.text
        TestProducts.pid = r.json()["id"]

    def test_get(self):
        r = requests.get(f"{API}/products/{TestProducts.pid}")
        assert r.status_code == 200
        assert r.json()["price"] == 99.0

    def test_search(self):
        r = requests.get(f"{API}/products", params={"search": "TEST_P"})
        assert r.status_code == 200
        assert any(p["id"] == TestProducts.pid for p in r.json())

    def test_update(self, admin_h):
        payload = {"name": "TEST_P_Up", "slug": f"test-p-up-{uuid.uuid4().hex[:6]}", "description": "d",
                   "price": 50.0, "images": [], "category_id": TestCategories.cat_id or "x", "stock": 3}
        r = requests.put(f"{API}/products/{TestProducts.pid}", json=payload, headers=admin_h)
        assert r.status_code == 200
        assert r.json()["price"] == 50.0


# ---------- Wishlist ----------
class TestWishlist:
    def test_add(self, cust_h):
        r = requests.post(f"{API}/wishlist/{TestProducts.pid}", headers=cust_h)
        assert r.status_code == 200

    def test_get(self, cust_h):
        r = requests.get(f"{API}/wishlist", headers=cust_h)
        assert r.status_code == 200
        assert any(p["id"] == TestProducts.pid for p in r.json())

    def test_remove(self, cust_h):
        r = requests.delete(f"{API}/wishlist/{TestProducts.pid}", headers=cust_h)
        assert r.status_code == 200


# ---------- Orders ----------
class TestOrders:
    oid = None

    def test_create(self, cust_h):
        payload = {"items": [{"product_id": TestProducts.pid, "qty": 2, "price": 50.0}],
                   "total": 100.0,
                   "shipping_address": {"name": "T", "address": "1 St", "city": "C", "zip": "1", "country": "US"}}
        r = requests.post(f"{API}/orders", json=payload, headers=cust_h)
        assert r.status_code == 200, r.text
        TestOrders.oid = r.json()["id"]
        assert r.json()["status"] == "pending"

    def test_list_customer(self, cust_h):
        r = requests.get(f"{API}/orders", headers=cust_h)
        assert r.status_code == 200
        assert any(o["id"] == TestOrders.oid for o in r.json())

    def test_admin_update_status(self, admin_h):
        r = requests.put(f"{API}/orders/{TestOrders.oid}/status", params={"status": "shipped"}, headers=admin_h)
        assert r.status_code == 200
        g = requests.get(f"{API}/orders/{TestOrders.oid}", headers=admin_h)
        assert g.json()["status"] == "shipped"


# ---------- Reviews ----------
class TestReviews:
    rid = None

    def test_create(self, cust_h):
        r = requests.post(f"{API}/reviews", json={"product_id": TestProducts.pid, "rating": 5, "comment": "good"}, headers=cust_h)
        assert r.status_code == 200
        TestReviews.rid = r.json()["id"]
        assert r.json()["approved"] is False

    def test_approve(self, admin_h):
        r = requests.put(f"{API}/reviews/{TestReviews.rid}/approve", headers=admin_h)
        assert r.status_code == 200

    def test_get_approved(self):
        r = requests.get(f"{API}/reviews", params={"product_id": TestProducts.pid})
        assert r.status_code == 200
        assert any(rv["id"] == TestReviews.rid for rv in r.json())


# ---------- Coupons ----------
class TestCoupons:
    code = f"TEST{uuid.uuid4().hex[:6].upper()}"

    def test_create(self, admin_h):
        r = requests.post(f"{API}/coupons",
                          json={"code": self.code, "discount_type": "percentage",
                                "discount_value": 10, "min_purchase": 10, "max_uses": 100},
                          headers=admin_h)
        assert r.status_code == 200

    def test_validate(self):
        r = requests.get(f"{API}/coupons/validate/{self.code}", params={"total": 100})
        assert r.status_code == 200
        assert r.json()["discount"] == 10

    def test_list(self, admin_h):
        r = requests.get(f"{API}/coupons", headers=admin_h)
        assert r.status_code == 200


# ---------- Banners & Settings ----------
class TestBannersSettings:
    bid = None

    def test_create_banner(self, admin_h):
        r = requests.post(f"{API}/banners", json={"title": "TEST_B", "image": "data:image/png;base64,xx", "position": 1, "active": True}, headers=admin_h)
        assert r.status_code == 200
        TestBannersSettings.bid = r.json()["id"]

    def test_list_banner(self):
        r = requests.get(f"{API}/banners")
        assert r.status_code == 200

    def test_settings_get(self):
        r = requests.get(f"{API}/settings")
        assert r.status_code == 200
        assert "footer_text" in r.json()

    def test_settings_update(self, admin_h):
        r = requests.put(f"{API}/settings", json={"footer_text": "TEST_FOOTER"}, headers=admin_h)
        assert r.status_code == 200
        assert r.json()["footer_text"] == "TEST_FOOTER"


# ---------- Admin stats ----------
class TestAdminStats:
    def test_stats(self, admin_h):
        r = requests.get(f"{API}/admin/stats", headers=admin_h)
        assert r.status_code == 200
        d = r.json()
        for k in ["total_products", "total_orders", "total_customers", "total_revenue"]:
            assert k in d


# ---------- Cleanup ----------
def test_zz_cleanup(admin_h):
    if TestProducts.pid:
        requests.delete(f"{API}/products/{TestProducts.pid}", headers=admin_h)
    if TestCategories.cat_id:
        requests.delete(f"{API}/categories/{TestCategories.cat_id}", headers=admin_h)
    if TestReviews.rid:
        requests.delete(f"{API}/reviews/{TestReviews.rid}", headers=admin_h)
    if TestBannersSettings.bid:
        requests.delete(f"{API}/banners/{TestBannersSettings.bid}", headers=admin_h)
