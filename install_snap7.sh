#!/bin/sh

# Download Snap7 library
wget https://sourceforge.net/projects/snap7/files/1.4.2/snap7-full-1.4.2.7z/download -O snap7-full-1.4.2.7z

# Install required tools
apk add --no-cache p7zip sudo

# Extract Snap7 library
7z x snap7-full-1.4.2.7z

# Install Snap7 library
cd snap7-full-1.4.2/build/unix
make -f arm_v6_linux.mk all
make -f arm_v6_linux.mk install
