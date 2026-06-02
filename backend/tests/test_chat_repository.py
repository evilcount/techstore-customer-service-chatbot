from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.db.models import Base
from backend.app.db.repository import ChatRepository


def make_repository():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    return ChatRepository(session_factory())


def test_create_session_for_unknown_email():
    repo = make_repository()

    session = repo.create_session("new.customer@example.com")

    assert session.customer_email == "new.customer@example.com"
    assert session.id


def test_add_and_list_messages():
    repo = make_repository()
    session = repo.create_session("john.doe@company.com")

    repo.add_message(session.id, "user", "Hello")
    repo.add_message(session.id, "assistant", "Hi there")
    messages = repo.list_messages(session.id)

    assert [message.role for message in messages] == ["user", "assistant"]
    assert [message.content for message in messages] == ["Hello", "Hi there"]
