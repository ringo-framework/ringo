from invoke import run, task

@task
def docs(doctype="html"):
    """Will build the documentation"""
    run("cd docs; make %s" % doctype)

@task
def test():
    """Will run all the tests"""
    run("coverage erase")
    run("alembic -c alembic-test.ini upgrade head")
    run("python setup.py nosetests")
    run("behave ringo/tests/behave/features --logging-level=ERROR")
    run("coverage report -m --include='ringo*' --omit='ringo/test*'")
    run("rm -r test-data")
    run("rm test.sqlite")
