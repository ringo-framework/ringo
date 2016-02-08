from invoke import run, task

@task
def clean():
    """Will remove swp, rej, pyc, orig files"""
    run("find . -name \*.swp -delete")
    run("find . -name \*.swo -delete")
    run("find . -name \*.rej -delete")
    run("find . -name \*.orig -delete")
    run("find . -name \*.pyc -delete")

@task
def docs(doctype="html", zip=False, show=False):
    """Will build the documentation"""
    run("cd docs; make %s" % doctype)
    run("cp -r docs/build/html ringo/static/doc")
    run("cp -r docs/build/html ringo/static/doc")
    if doctype == "html" and zip:
        run("cd docs/build/html/; zip -r ../doc.zip *")
    if show:
        run("cd docs/build/html/; firefox index.html")


@task
def test():
    run("ringo-admin db init --config=test.ini")
    run("python setup.py test")
