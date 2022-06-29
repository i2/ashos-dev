#!/bin/sh

# Detect OS/distro name
name=""
if grep -q '^DISTRIB_ID=' $1/etc/lsb-release 2>/dev/null; then
    name="$(awk -F= '$1 == "DISTRIB_ID" {print tolower($2)}' /etc/lsb-release)"
elif grep -q '^ID=' $1/etc/os-release 2>/dev/null; then
    name="$(. /etc/os-release && echo "${ID}")"
else
    for file in $1/etc/*; do
        if [ "${file}" = "os-release" ]; then
            continue
        elif [ "${file}" = "lsb-release" ]; then
            continue
        elif echo "${file}" | grep -q -- "-release$" 2>/dev/null; then
            name="$(awk '{print tolower($1);exit}' "${file}")"
            break
        fi
    done
fi
if [ -z "${name}" ]; then
    echo "Your operating system/distro could not be detected" >/dev/null 2>&1
    break
fi

echo $name

