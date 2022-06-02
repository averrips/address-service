import pytest


@pytest.fixture(scope="session")
def django_db_use_migrations():
    """Used for the test_ensure_migrations_are_run test, this fixture temporarily enables migrations.
    By default migrations are not run for performance reasons.
    """
    return False
