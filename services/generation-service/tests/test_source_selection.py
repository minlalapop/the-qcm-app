from app.services.source_selection import distribute_questions


def test_distribute_questions() -> None:
    assert distribute_questions(7, 3) == [3, 2, 2]
