#!/bin/sh
# produce ptex2tex documentation

ptex2tex doc
latex -shell-escape doc
latex -shell-escape doc
dvipdf doc
