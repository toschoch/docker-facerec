import pytest

from facerec_service import create_app
from facerec import facedb

@pytest.fixture
def app(tmpdir):
    facedb.set_db_path(tmpdir)
    app = create_app()
    app.debug = True
    return app

