#!/bin/sh
#set -x

USAGE="Usage: `basename $0` [-hv] [-s] [-e] [-l logfile.txt] [-c git-url] [-n] app"
VERSION="0.0"

NEWAPP=0
GIT="0"
SYSTEMSITEPACKAGES=0
INSTALLEXT=0
LOGFILE=/dev/null

# URLS
BRABBEL=https://github.com/ringo-framework/brabbel.git
FORMBAR=https://github.com/ringo-framework/formbar.git
RINGO=https://github.com/ringo-framework/ringo.git
PYTESTRINGO=https://github.com/ringo-framework/pytest-ringo.git

# EXTENSIONS
PRINTTEMPLATES=https://github.com/ringo-framework/ringo_printtemplates.git
COMMENT=https://github.com/ringo-framework/ringo_comment.git
EVALUATION=https://github.com/ringo-framework/ringo_evaluation.git
DIAGRAM=https://github.com/ringo-framework/ringo_diagram.git
FILE=https://github.com/ringo-framework/ringo_file.git
NEWS=https://github.com/ringo-framework/ringo_news.git
TAG=https://github.com/ringo-framework/ringo_tag.git
EXTENSIONS="$PRINTTEMPLATES $COMMENT $EVALUATION $DIAGRAM $FILE $NEWS $TAG"


# Parse command line options.
while getopts hvsnec:l: OPT; do
    case "$OPT" in
        h)
            echo $USAGE
            exit 0
            ;;
        v)
            echo "`basename $0` version $VERSION"
            exit 0
            ;;
        s)
            SYSTEMSITEPACKAGES=1
            ;;
        n)
            NEWAPP=1
            ;;
        e)
            INSTALLEXT=1
            ;;
        c)
            GIT=$OPTARG
            ;;
        l)
            LOGFILE=$OPTARG
            ;;
        \?)
            # getopts issues an error message
            echo $USAGE >&2
            exit 1
            ;;
    esac
done

# Remove the switches we parsed above.
shift `expr $OPTIND - 1`

# We want at least one non-option argument. 
# Remove this block if you don't need it.
if [ $# -eq 0 ]; then
    echo $USAGE >&2
    exit 1
fi

# Check if clone and new option is provided
if [ $NEWAPP -eq 1 ] && [ $GIT != "0" ]; then
  echo "Error: -c and -n option are not allowed together"
  echo $USAGE >&2
  exit 1
fi


# Set name of the application
APP=$1

if ! [ -d $APP ]; then
  mkdir $APP
fi

cd $APP
if ! [ -d "env" ]; then
  printf "Installing virtualenv... "
  if [ $SYSTEMSITEPACKAGES -eq 1 ]; then
    virtualenv --system-site-packages env > $LOGFILE  2>&1
  else
    virtualenv env > $LOGFILE  2>&1
  fi
  printf "OK\n"
fi

. env/bin/activate
pip install setuptools --upgrade > $LOGFILE  2>&1

Deploy() {
  DIR=`echo $1 | awk -F \/ '{split($NF, P, "."); print P[1]}'`
  if ! [ -d $DIR ]; then
    printf "Installing $DIR... "
    git clone $path $DIR > $LOGFILE  2>&1
    cd $DIR
    python setup.py develop > $LOGFILE  2>&1
    printf "OK\n"
    cd ..
  fi
}

if ! [ -d lib ]; then
  mkdir lib
fi
cd lib
# Install base libs
for path in $BRABBEL $FORMBAR $RINGO; do
  Deploy $path
done
# Install extensions
if [ $INSTALLEXT -eq 1 ]; then
  for path in $EXTENSIONS; do
    Deploy $path
  done
fi

cd ..

if [ $NEWAPP -eq 1 ]; then
  printf "Creating new app $APP... "
  pcreate -t ringo $APP
  mv $APP src
  cd src
  python setup.py develop > $LOGFILE  2>&1
  printf "OK\n"
  cd ..
fi

if [ $GIT != "0"  ]; then
  printf "Cloning app $APP... "
  git clone $GIT $APP
  mv $APP src
  cd src
  if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > $LOGFILE  2>&1
  else
    python setup.py develop > $LOGFILE  2>&1
  fi
  printf "OK\n"
  cd ..
fi

echo "Ringo Setup Ready. Next steps:"
echo ""
echo "cd $APP"
echo "source env/bin/activate"
exit 0
