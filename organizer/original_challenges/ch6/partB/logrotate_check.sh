#!/bin/bash
# NovaGrid internal utility - checks log rotation status for a named service.
# Intentionally vulnerable (Section 10.6): passes its argument straight into
# a shell without any sanitisation, so anything the caller passes runs as
# whatever user invokes this script - root, in this challenge, because of
# the overly permissive sudoers rule.
#
# This is the single intentional misconfiguration for CH6 Part B. It is not
# a kernel exploit or an unrelated bug - it is a realistic, well-documented
# class of sudoers misconfiguration (unrestricted argument passthrough).

SERVICE_NAME="$1"
echo "Checking log rotation status for: ${SERVICE_NAME}"
bash -c "${SERVICE_NAME}"
