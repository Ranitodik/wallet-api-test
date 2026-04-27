# tests/test_wallet.py
import httpx

def test_wallet_flow():
    base_url = "http://app:8000"  # внутри Docker сети имя сервиса — 'app'
    wallet_id = "123e4567-e89b-12d3-a456-426614174000"

    # Пополнение кошелька
    response = httpx.post(
        f"{base_url}/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": 100}
    )
    assert response.status_code == 200
    assert response.json()["balance"] == 100.0

    # Получение баланса
    response = httpx.get(f"{base_url}/api/v1/wallets/{wallet_id}")
    assert response.status_code == 200
    assert response.json()["balance"] == 100.0

    # Снятие средств
    response = httpx.post(
        f"{base_url}/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": 30}
    )
    assert response.status_code == 200
    assert response.json()["balance"] == 70.0

    # Недостаточно средств
    response = httpx.post(
        f"{base_url}/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": 200}
    )
    assert response.status_code == 400