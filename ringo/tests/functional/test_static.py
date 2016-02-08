def test_about(app):
    app.get("/about")


def test_version(app):
    app.get("/version")


def test_contact(app):
    app.get("/contact")


def test_index(app):
    app.get("/contact")
