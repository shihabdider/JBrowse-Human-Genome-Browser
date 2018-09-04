#!/usr/bin/env bash 

# This script updates all the genomic data in the /data directory

# The following databases are used:
# GATK Resource Bundle
# ENSEMBL Variations Dataset

# GATK #
########

GATK_DIR="/data/jbrowse/data/gatk/"

mkdir -p $GATK_DIR
wget -m -P $GATK_DIR ftp://gsapubftp-anonymous@ftp.broadinstitute.org/bundle/hg38

# ENSEMBL #
###########

ENSEMBL_DIR="/data/jbrowse/data/ensembl"

wget --no-remove-listing ftp://ftp.ensembl.org/pub/
RELEASE="$(grep -Eo release-[0-9]+ .listing| sort -nrt M -k2,2 | head -n 1)"
echo "${RELEASE}"

mkdir -p $ENSEMBL_DIR
wget -np -nH --cut-dirs 5 -m -P $ENSEMBL_DIR/vcf ftp://ftp.ensembl.org/pub/$RELEASE/variation/vcf/homo_sapiens/
wget -np -nH --cut-dirs 5 -m -P $ENSEMBL_DIR/gff3 ftp://ftp.ensembl.org/pub/$RELEASE/gff3/homo_sapiens/
wget -np -nH --cut-dirs 5 -m -P $ENSEMBL_DIR/regulation ftp://ftp.ensembl.org/pub/$RELEASE/regulation/homo_sapiens/

# Update JBrowse trackList

# python make_tracklist.py /data/jbrowse/data /data/jbrowse/data/trackList.json
