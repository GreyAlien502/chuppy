#!/bin/bash

file="$1"
resolution=${2:-8}
measure=${3:-1}

vim \
	'+%!python ~/chuck/py/scripts/midi2txt.py'" $resolution 1" \
	'+set syntax=bash nowrap colorcolumn='"$(seq 9 $(( $measure * $resolution )) 1000 |tr \\n ,)9" \
	'+autocmd BufReadPost  * :%!python ~/chuck/py/scripts/midi2txt.py'" $resolution 1" \
	'+autocmd BufWritePost * :%!python ~/chuck/py/scripts/midi2txt.py'" $resolution 1" \
	'+autocmd BufWritePre  * :%!python ~/chuck/py/scripts/midi2txt.py'" -d $resolution" \
	"$file"
