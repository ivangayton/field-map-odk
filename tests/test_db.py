import sqlite3

import pytest

from odk_fieldmap.db import get_db
from odk_fieldmap.models import User

# def test_get_close_db(app):
#    with app.app_context():
#        db = get_db()
#        assert db is get_db()
#    with pytest.raises(sqlite3.ProgrammingError) as e: db.session.query(User).first()
#    assert 'closed' in str(e.value)
#
# def test_init_db_command(runner, monkeypatch):
#    class Recorder(object):
#        called = False
#
#    def fake_init_db():
#        Recorder.called = True
#
#    monkeypatch.setattr('odk_fieldmap.db.init_db', fake_init_db)
#    result = runner.invoke(args=['init-db'])
#    assert 'Initialized' in result.output
#    assert Recorder.called
