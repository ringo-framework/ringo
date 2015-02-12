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
def test(exclude="None"):
    """Will run all the tests"""
    if not exclude:
        exclude = []
    if exclude:
        exclude = exclude.split(",")
    if "init" not in exclude:
        run("rm -f test.sqlite")
        run("ringo-admin db init --config=test.ini")
        run("ringo-admin fixtures load --config=test.ini")
    if "unit" not in exclude:
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
