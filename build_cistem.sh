#!/bin/bash
set -euo pipefail

git -C cisTEM pull || git clone https://github.com/timothygrant80/cisTEM.git

cd cisTEM
./regenerate_project.b

mkdir -p build/icpc && cd build/icpc && CC=icc CXX=icpc CPPFLAGS=-fPIC CXXFLAGS=-fPIC CFLAGS=-fPIC ../../configure  --enable-staticmode --enable-samples --enable-experimental --enable-openmp --with-wx-config=/opt/WX/intel-static/bin/wx-config

make -j 2