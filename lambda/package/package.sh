#!/bin/bash
cp ../../standalone/requirements.txt .
cp ../../standalone/*.py .
cp ../*.py .
pip install -r requirements.txt -t ./
rm -f lambdas.zip && zip -r lambdas.zip ./ -x '*.zip'
cp lambdas.zip ../
find . \! -name 'package.sh' -delete