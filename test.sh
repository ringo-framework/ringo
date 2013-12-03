#!/bin/sh
rm test.sqlite
alembic -c alembic-test.ini upgrade head
#initialize_ringo_db test.ini
#nosetests
behave ringo/tests/behave/features --logging-level=ERROR
coverage report -m --include="ringo*" --omit="ringo/test*"
rm -r test-data
rm test.sqlite
