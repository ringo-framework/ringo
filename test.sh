#!/bin/sh
rm test.sqlite
initialize_ringo_db test.ini
nosetests
behave ringo/tests/behave/features --logging-level=ERROR
rm -r test-data
rm test.sqlite
