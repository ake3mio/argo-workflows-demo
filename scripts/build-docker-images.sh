#!/bin/zsh

SCRIPT_DIR=$(dirname $0)

pushd $SCRIPT_DIR/..
  docker build -t tickerconfig -f docker/tickerconfig.dockerfile .
  docker build -t marketdata -f docker/marketdata.dockerfile .
  docker build -t strategy -f docker/strategy.dockerfile .
popd