#!/usr/bin/env python2

'''This script updates the trackList.json file with the data in its data directory

usage: python make_tracklist.py [jbrowse data directory] [path to trackList.json]
e.g: python make_tracklist.py /data/jbrowse/data /data/jbrowse/data/trackList.json'''

import json
import sys
import os

# Get the directory paths from commandline

data_dir = sys.argv[1]
trackList_file = sys.argv[2]

# Iterate through files in data directory and save paths to list

datafiles = []

for root, dirs, files in os.walk(data_dir):
	for name in files:
		datafiles.append(os.path.join(root, name))

# Load the trackList.json file into python

# Process each type of file individually and create a JSON object(?) for each
# one and append this to a dictionary of dictionaries (?)

# VCF Template
# {
#         "label"         : "mysnps",
#         "key"           : "SNPs from VCF",
#         "storeClass"    : "JBrowse/Store/SeqFeature/VCFTabix",
#         "urlTemplate"   : "../vcf_files/SL2.40_all_rna_seq.v1.vcf.gz",
#         "type"          : "JBrowse/View/Track/HTMLVariants"
#      }


def get_category(datafilepath, source):
	import re

	category = ''
	
	if source == 'gatk':	
		category = 'Variations/GATK'

	elif source == 'ensembl':
		germline_pat = 'homo_sapiens-chr.+\.vcf\.gz'
		cons_pat = 'homo_sapiens_incl_consequences-chr.+\.vcf\.gz'
		hapmap_pat = 'HAPMAP'
		esp_pat = 'ESP6500'
		
		if re.search(germline_pat, datafilepath):
			category = 'Variations/ENSEMBL/Germline Variations'
		elif re.search(cons_pat, datafilepath):
			category = 'Variations/ENSEMBL/Consequence'
		elif re.search(hapmap_pat, datafilepath):
			category = 'Variations/ENSEMBL/Allele Frequency'
		elif re.search(esp_pat, datafilepath):
			category = 'Variations/ENSEMBL/Allele Frequency'
		else:
			category = 'Variations/ENSEMBL/General'

	return category

	
def make_vcf_track(datafilepath):
	vcf_keys = ['label', 'key', 'storeClass', 'urlTemplate', 'type']
	datafile_track = {key:'' for key in vcf_keys}
	
	if 'gatk' in datafilepath:
		datafile_track['category'] = get_category(datafilepath, 'gatk')
		datafile_track['label'] = 'gatk vcf {}'.format(os.path.basename(datafilepath))
	elif 'ensembl' in datafilepath: 
		datafile_track['category'] = get_category(datafilepath, 'ensembl')
		datafile_track['label'] = 'ensembl vcf {}'.format(os.path.basename(datafilepath))
		


	datafile_track['key'] = os.path.basename(datafilepath)[:-3]
	datafile_track['storeClass'] ='JBrowse/Store/SeqFeature/VCFTabix' 
	datafile_track['urlTemplate'] = os.path.relpath(datafilepath, data_dir)
	datafile_track['type'] = 'JBrowse/View/Track/HTMLVariants'
	
	return datafile_track

def make_gff3_track(datafilepath):
	'''Handle all the gff3 tracks using the flatfile-to-json.pl script'''
	import subprocess, shlex

	flatfile_to_json_path = '/data/jbrowse/bin/flatfile-to-json.pl'
	
	if 'ensembl' in datafilepath:
		if 'regulation' in datafilepath:
			# Run the flatfile-to-json.pl
			# 			args_str = '{0} --gff {1} --tracklabel {2} --key {2} --trackType CanvasFeatures --className Regulation/ENSEMBL --out /data/jbrowse/data'.format(flatfile_to_json_path, datafilepath, os.path.basename(datafilepath))
	
			args_str = '{0} --gff {1} --tracklabel {2} --key {2} --className Regulation/ENSEMBL --config \'{{\"category\":\"Regulation\"}}\' --out /data/jbrowse/data'.format(flatfile_to_json_path, datafilepath, os.path.basename(datafilepath))
			args = shlex.split(args_str)
			print 'Running {0}'.format(args_str)
			p = subprocess.call(args, stdout=subprocess.PIPE)
		elif 'gff3' in datafilepath:
			# Run the flatfile-to-json.pl
			# args_str = '{0} --gff {1} --tracklabel {2} --key {2} --trackType CanvasFeatures --className Genes/ENSEMBL --out /data/jbrowse/data'.format(flatfile_to_json_path, datafilepath, os.path.basename(datafilepath))

			args_str = '{0} --gff {1} --tracklabel {2} --key {2} --className Genes/ENSEMBL --config \'{{\"category\":\"Genes\"}}\' --out /data/jbrowse/data'.format(flatfile_to_json_path, datafilepath, os.path.basename(datafilepath))
			args = shlex.split(args_str)
			print 'Running {0}'.format(args_str)
			p = subprocess.call(args, stdout=subprocess.PIPE)

		# Add clause for datasets other than ensembl

def make_bed_track(datafilepath):
	'''Handle all the bed tracks using the flatfile-to-json.pl script'''

	import subprocess, shlex

	flatfile_to_json_path = '/data/jbrowse/bin/flatfile-to-json.pl'
	

	if 'ensembl' in datafilepath:
		if 'regulation' in datafilepath:
			# Run the flatfile-to-json.pl
			args_str = '{0} --bed {1} --tracklabel {2} --key {2} --trackType CanvasFeatures --className Regulation/ENSEMBL --config \'{{\"category\":\"Regulation\"}}\' --out /data/jbrowse/data'.format(flatfile_to_json_path, datafilepath, os.path.basename(datafilepath))
			args = shlex.split(args_str)
			p = subprocess.call(args, stdout=subprocess.PIPE)

		elif 'gff3' in datafilepath:
			# Run the flatfile-to-json.pl
			args_str = '{0} --bed {1} --tracklabel {2} --key {2} --trackType CanvasFeatures --className Genes/ENSEMBL --config \'{{\"category\":\"Genes\"}}\' --out /data/jbrowse/data'.format(flatfile_to_json_path, datafilepath, os.path.basename(datafilepath))
			args = shlex.split(args_str)
			p = subprocess.call(args, stdout=subprocess.PIPE)



		# Add clause for datasets other than ensembl


vcf_datafile_tracks = []
for datafile in datafiles:
	if datafile.endswith('vcf.gz'):
		datafile_track = make_vcf_track(datafile)				
		vcf_datafile_tracks.append(datafile_track)
# 	elif datafile.endswith('.gff3'):
# 		make_gff3_track(datafile)
# 	elif datafile.endswith('bed.gz'):
# 		make_bed_track(datafile)
# 
# Convert dictionary to JSON and append vcf to trackList.json

decoded_json = {}
with open(trackList_file, 'r') as tLjson:
	decoded_json = json.load(tLjson)
	json_urls = [json_track['urlTemplate'] for json_track in decoded_json['tracks']]
	for track in vcf_datafile_tracks:
		if track['urlTemplate'] not in json_urls:
			print 'Adding {0} to track list'.format(track['key'])
			decoded_json['tracks'].append(track)

with open(trackList_file, 'w') as tLjson:
	json.dump(decoded_json, tLjson, indent=4)



