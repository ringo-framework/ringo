APP=$1
BRABBEL=https://github.com/ringo-framework/brabbel
FORMBAR=https://github.com/ringo-framework/formbar
RINGO=https://github.com/ringo-framework/ringo

if ! [ -d $APP ]; then
  mkdir $APP
fi

cd $APP
if ! [ -d env ]; then
  virtualenv env
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