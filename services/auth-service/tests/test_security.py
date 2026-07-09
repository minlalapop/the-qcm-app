from app.services.security import hash_password, verify_password


def test_password_hashing_roundtrip() -> None:
    hashed_password = hash_password("strong-password")

    assert hashed_password != "strong-password"
    assert verify_password("strong-password", hashed_password)
    assert not verify_password("wrong-password", hashed_password)
