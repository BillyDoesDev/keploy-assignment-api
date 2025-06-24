#!/bin/bash

export PYTHONPATH=$(pwd)
pytest --cov=scripts --cov-report=term-missing --html=report.html --self-contained-html --cov-fail-under=70
