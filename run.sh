#!/bin/bash

case "$1" in
one)
  PUB=true E2E=true coverage run -m unittest tests.$2
  ;;
test)
  coverage run -m unittest && coverage report && coverage html
  if [ "$2" = "-v" ]; then
    open htmlcov/index.html
  fi
  ;;
all)
  PUB=true E2E=true coverage run -m unittest && coverage report && coverage html
  if [ "$2" = "-v" ]; then
    open htmlcov/index.html
  fi
  ;;
e2e)
  E2E=true coverage run -m unittest tests.test_e2e && coverage report && coverage html
  if [ "$2" = "-v" ]; then
    open htmlcov/index.html
  fi
  ;;
pub)
  PUB=true coverage run -m unittest tests.test_publish && coverage report && coverage html
  if [ "$2" = "-v" ]; then
    open htmlcov/index.html
  fi
  ;;
docs)
  pydoc-markdown --bootstrap mkdocs
  pydoc-markdown --bootstrap readthedocs
  pydoc-markdown --server --open
  ;;
*)
  echo ""
  echo "usage: sh run.sh <command> [-v]"
  echo ""
  echo "where <command> is one of the following:"
  echo ""
  echo "  test -- to run only unit tests"
  echo "  e2e -- to run only end-to-end tests"
  echo "  pub -- to run only publishing tests"
  echo "  all -- to run unit, end-to-end, and publishing tests"
  echo "  docs -- to generate documentation"
  echo ""
  echo "When running tests, use -v to open the coverage report in your browser."
  echo ""
  ;;
esac
