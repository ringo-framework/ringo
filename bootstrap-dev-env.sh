#!/bin/sh
#set -x

USAGE="Usage: `basename $0` [-hv] [-s] [-c git-url] [-n] app"
VERSION="0.0"

NEWAPP=0
GIT="0"
SYSTEMSITEPACKAGES=0

# URLS
BRABBEL=https://github.com/ringo-framework/brabbel
FORMBAR=https://github.com/ringo-framework/formbar
RINGO=https://github.com/ringo-framework/ringo


# Parse command line options.
while getopts hvsnc: OPT; do
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
        c)
            GIT=$OPTARG
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
  if [ $SYSTEMSITEPACKAGES -eq 1 ]; then
    virtualenv --system-site-packages env
  else
    virtualenv env
  fi
fi

. env/bin/activate
pip install setuptools --upgrade

if ! [ -d lib ]; then
  mkdir lib
fi

cd lib
if ! [ -d brabbel ]; then
  git clone $BRABBEL
  cd brabbel
  python setup.py develop
  cd ..
fi

if ! [ -d formbar ]; then
  git clone $FORMBAR
  cd formbar
  python setup.py develop
  cd ..
fi

if ! [ -d ringo ]; then
  git clone $RINGO
  cd ringo
  python setup.py develop
  cd ..
fi
cd ..

if [ $NEWAPP -eq 1 ]; then
  pcreate -t ringo $APP
  mv $APP src
  cd src
  python setup.py develop
  cd ..
fi

if [ $GIT != "0"  ]; then
  git clone $GIT $APP
  mv $APP src
  cd src
  if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
  else
    python setup.py develop
  fi
  cd ..
fi
exit 0
