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
    run("behave ringo/tests/behave/features --tags=-wip --tags=-needs_mail_setup --logging-level=ERROR")

    cmd_coverage = []
    cmd_coverage.append("coverage report")
    cmd_coverage.append("-m")
    cmd_coverage.append("--include='ringo*'")
    # Omit testfiles,
    # Omit scripts,
    # Omit statemachine (is already tests in functional tests),
    cmd_coverage.append("--omit='ringo/test*,ringo/scripts/*,ringo/model/statemachine*'")
    run(" ".join(cmd_coverage))
    run("rm -r test-data")
    run("rm test.sqlite")
