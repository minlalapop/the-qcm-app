from app.services.metrics import average


def test_average_ignores_none() -> None:
    assert average([1, None, 3]) == 2.0
