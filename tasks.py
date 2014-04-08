from invoke import run, task


@task
def docs(doctype="html"):
    """Will build the documentation"""
    run("cd docs; make %s" % doctype)
    run("cp -r docs/build/html ringo/static/doc")


@task
def test(exclude="None"):
    """Will run all the tests"""
    if not exclude:
        exclude = []
    if exclude:
        exclude = exclude.split(",")
    if "init" not in exclude:
        run("rm test.sqlite")
        run("alembic -c alembic-test.ini upgrade head")
    run("python setup.py nosetests")
    if "behave" not in exclude:
        #run("coverage erase")
        #cmd_coverage = []
        #cmd_coverage.append("coverage report")
        #cmd_coverage.append("-m")
        #cmd_coverage.append("--include='ringo*'")
        ## Omit testfiles,
        ## Omit scripts,
        ## Omit statemachine (is already tests in functional tests),
        #cmd_coverage.append("--omit='ringo/test*,ringo/scripts/*,ringo/model/statemachine*'")
        #run(" ".join(cmd_coverage))
        run("behave ringo/tests/behave/features --tags=-wip --tags=-needs_mail_setup --logging-level=ERROR")
        run("rm -r test-data")
    else:
        print "Ignoring Functional-Tests (Behave)"
