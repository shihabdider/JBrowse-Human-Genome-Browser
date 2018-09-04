#!/usr/bin/env python2

'''
This script handles all the metadata for the datasets and creates a csv file
for use with the facted track selector

Input: directory with all the datasets
Ouput: metadata.csv 

Usage: 
python extract_metadata.py /data/jbrowse/data/trackList.json
Current metadata tags:

label - Corresponds to the label in the track configuration (which is the filename)
source - Dataset source (ENSEMBL or GATK)
type - Filetype (VCF, GFF3, BED)
category - type of data (Variation, Regulation, Gene, Allele Frequency, Consequence, Germline Variations)
'''

import sys
import os
import json

# Get the trackList path from commandline

trackList = sys.argv[1]

data_dirs = []

with open(trackList, 'r') as handle:
	for track in json.load(handle)['tracks']:
		data_dir = track['urlTemplate'].split('/')[:-1]
		data_path = '/'.join(data_dir+[track['label']])
		data_dirs.append(data_path)

def get_category(datafilepath, source):
	import re
	from glob import glob

	category = ''
	epigenome = ''

	if source == 'gatk':	
		category = 'Variations'

	elif source == 'ensembl':
		germline_pat = 'homo_sapiens-chr.+\.vcf\.gz'
		cons_pat = 'homo_sapiens_incl_consequences-chr.+\.vcf\.gz'
		hapmap_pat = 'HAPMAP'
		esp_pat = 'ESP6500'
		
		if re.search(germline_pat, datafilepath):
			category = 'Germline Variations'
		elif re.search(cons_pat, datafilepath):
			category = 'Consequence Variations'
		elif re.search(hapmap_pat, datafilepath):
			category = 'Allele Frequency'
		elif re.search(esp_pat, datafilepath):
			category = 'Allele Frequency'
		elif 'regulation' in datafilepath:
			category = 'Regulation'
			# Needs more specificity with regards to experiment/location
			regulation_folder = re.search('.*\/regulation\/', datafilepath)

			epigenome_list = []
			if regulation_folder:
				epigenome_list = glob("{0}*/".format(regulation_folder.group(0)))
			#print epigenome_list
			
			for elem in epigenome_list:
				if elem in datafilepath:
					epigenome = elem.split('/')[:-1][-1]
					print epigenome
			
		elif 'gff3' in datafilepath:
			category = 'Gene'
		else:
			category = 'Variations'

	return category, epigenome # Need to make a separate function for epigenome


def gen_metadata(datafiles):
	'''
	Generate metadata tags and load them into a dictionary
		
	Input: List of datafile paths
	Output: List of dictionaries with all metadata tags 
	'''
	metadata_dicts = []
	metadata_cols = ['label', 'source', 'type', 'category', 'epigenome']

	for datafile in datafiles:	
		if datafile.endswith('.gz'):
			metadata_dict = {metadata_cols[i]:None for i in range(len(metadata_cols))}
			
			metadata_dict['label'] = datafile.split('/')[-1]
			
			if 'ensembl' in datafile:
				metadata_dict['source'] = 'ENSEMBL'
				metadata_dict['category'], metadata_dict['epigenome'] = get_category(datafile, 'ensembl')
			elif 'gatk' in datafile:
				metadata_dict['source'] = 'GATK'
				metadata_dict['category'], metadata_dict['epigenome'] = get_category(datafile, 'gatk')
			if datafile.endswith('.gff3.gz') or datafile.endswith('.gff.gz'):
				metadata_dict['type'] = 'GFF3'
			elif datafile.endswith('.vcf.gz'):
				metadata_dict['type'] = 'VCF'
			elif datafile.endswith('.bed.gz'):
				metadata_dict['type'] = 'BED'

		
			metadata_dicts.append(metadata_dict)
		
	return metadata_dicts


def make_csv(metadata_dicts, metadatafile):
	'''Makes the metadata.csv using the list of dictionaries with the metadata tags'''

	import csv
	
	try:
   		with open(metadatafile, 'w+') as csvfile:
			writer = csv.DictWriter(csvfile, fieldnames=metadata_dicts[0].keys())
			writer.writeheader()
			for data in metadata_dicts:
			    writer.writerow(data)
	except IOError:
    		print("I/O error") 	

metadata_dicts = gen_metadata(data_dirs)
make_csv(metadata_dicts, '/data/jbrowse/data/metadata.csv')	
