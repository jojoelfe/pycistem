#!/bin/bash
set -euo pipefail

git -C cisTEM pull || git clone https://github.com/timothygrant80/cisTEM.git

cd cisTEM
./regenerate_project.b

mkdir -p build/gcc && cd build/gcc && CC=gcc CXX=g++ CPPFLAGS=-fPIC CXXFLAGS=-fPIC CFLAGS=-fPIC ../../configure  --enable-staticmode --enable-samples --enable-experimental --enable-openmp --with-wx-config=wx-config

cd src

make -j 2 libcore.a