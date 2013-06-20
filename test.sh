#!/bin/sh
rm test.sqlite
initialize_ringo_db test.ini
nosetests
