#!/usr/bin/env bash 

# This script will retrieve the top level features for vcf and gff3 files to
# create separate tracks

# Input: A datafile path, a datatype (vcf or gff3)
# Output: A text file with all top level features

datafilepath=$1
datatype=$2

# GFF3 #
########

if [ "${datatype}" == "gff3" ];
then
	less $datafilepath | grep "^[^#]" |  cut -f 3 | sort | uniq > ${datafilepath}_toplvlfeats.txt
	echo Wrote ${datafilepath}_toplvlfeats.txt 
# VCF #
#######
elif [ "${datatype}" == "vcf" ];
then
	less $datafilepath | grep "^[^#]" |  cut -f 5 | sort | uniq > ${datafilepath}_toplvlfeats.txt
	echo Wrote ${datafilepath}_toplvlfeats.txt 
fi

