#!/usr/bin/env python2

'''This script preprocesses the data downloaded from the online databases

- Concatenates files split by chromosome into one file 
- Creates tabix indicies for all gff and bed files (.tbi files)
- Splits structural variants by type 

Input: Directory with all the downloaded datasets
Output: Processed data for use with a script to make the trackList.json

Usage: python preproc_data.py /data/jbrowse/data'''

import sys
import os

# Get the directory paths from commandline

data_dir = sys.argv[1]

# Iterate through files in data directory and save paths to list

datafiles = []

for root, dirs, files in os.walk(data_dir):
	for name in files:
		datafiles.append(os.path.join(root, name))


# Concatenate all files split by chromosome #
#############################################

# Determine which files need to be collated

def get_split_files(datafiles):
	'''
	Filters the list of files and returns all the files to be collated 
	in a list of lists. Uses regex to determine if collated file already 
	exists and to collect the split files for one type

	Input: List of all files
	Output: List of lists containing files to be collated
	'''
	
	import re
	
	chr_split_pat = '.+chr.*([0-9]{1,2}|[XY]|MT).*(?<!(tbi))$'
	chr_concat_pat = '.+chr(_all|.gff3).*'

	collated_files = []

	for datafilepath in datafiles:
		filename = os.path.basename(datafilepath)
		if re.search(chr_concat_pat, filename):
			prefix = re.search('.+chr', filename)
			for datafilepath in datafiles:
				if prefix.group(0) in datafilepath:
					collated_files.append(datafilepath)

	split_files = {} 
	for datafilepath in datafiles:
		filename = os.path.basename(datafilepath)
		if re.search(chr_split_pat, filename):
			if datafilepath not in collated_files:
				prefix = re.search('.+chr', filename)
				if prefix.group(0) in datafilepath:
					if prefix.group(0) not in split_files:
						split_files[prefix.group(0)] = [datafilepath]
					else:
						split_files[prefix.group(0)].append(datafilepath)

	return split_files


# Concatenate files based on type

def concat_files(datafiles):
	'''
	Concatenates files depending on type using either vcf-concat or cat (for gff)
	
	Input: Dictionary of filtered files from get_split_files
	Output: Concatented files
	'''

	import subprocess, shlex, re

	for key in split_files_dict:
		split_files = split_files_dict[key]
		
		if split_files[0].endswith('.vcf.gz'):
		# vcf-concat homo_sapiens_incl_consequences-chr* | bgzip -c > homo_sapiens_incl_consequences.vcf.gz	
			filename = os.path.basename(split_files[0])
			prefix = re.search('.+chr', filename)
			split_files_string = ' '.join(split_files)
			args_str_concat = 'vcf-concat {0}'.format(split_files_string)
			args_concat = shlex.split(args_str_concat)
			print 'Running {0}'.format(args_str_concat)
			p1 = subprocess.call(args_concat, stdout=subprocess.PIPE)
			
			args_str_bgzip = 'bgzip -c'
			args_bgzip = shlex.split(args_str_bgzip)
			print 'Running {0}'.format(args_str_bgzip)
			with open('{0}_all.vcf.gz'.format(prefix.group(0)), 'w+') as zipfile:
				p2 = subprocess.check_output(args_bgzip, stdin=p1.stdout, stdout=zipfile)
			



#split_files_dict = get_split_files(datafiles)
#concat_files(split_files_dict)	

# Create tabix indices for all gff and bed files #
##################################################

def bgzip_data(datafile):
	'''
	bgzips datafile for indexing
	'''
	
	import subprocess, shlex

	args_str = 'bgzip {0}'.format(datafile)
	args = shlex.split(args_str)
	print 'Running {0}'.format(args_str)
	p = subprocess.call(args, stdout=subprocess.PIPE)
		
def tabix_data(datafiles):
	'''
	Tabixes all datafiles that have no associated index

	Input: List of all datafiles
	Output: Tbi files for all datafiles without an index
	'''
	
	import subprocess, shlex

	tbi_files = []
	for datafile in datafiles:
		if datafile.endswith('.tbi'):
			tbi_files.append(datafile)

	for datafile in datafiles:
		if not datafile.endswith('.tbi'):
			if not '{0}.tbi'.format(datafile) in tbi_files:
				if datafile.endswith('.gff3') or datafile.endswith('.gff'):
					# Need to first sort the file
					args_str_sort = 'sort -k1,1 -k4,4n -o {0} {0}'.format(datafile)
					args_sort = shlex.split(args_str_sort)
					print 'Running {0}'.format(args_str_sort)
					sort_p = subprocess.call(args_sort, stdout=subprocess.PIPE)
					
					# Then bgzip the file
					bgzip_data(datafile)
					
					# And finally tabix the file
					args_str = 'tabix -p gff {0}.gz'.format(datafile)
					args = shlex.split(args_str)
					print 'Running {0}'.format(args_str)
					p = subprocess.call(args, stdout=subprocess.PIPE)

				elif datafile.endswith('.gff3.gz'):
					args_str = 'tabix -p gff {0}'.format(datafile)
					args = shlex.split(args_str)
					print 'Running {0}'.format(args_str)
					p = subprocess.call(args, stdout=subprocess.PIPE)

				elif datafile.endswith('.bed'):
					# bgzip the file first
					bgzip_data(datafile)

					# Then tabix
					args_str = 'tabix -p bed {0}.gz'.format(datafile)
					args = shlex.split(args_str)
					print 'Running {0}'.format(args_str)
					p = subprocess.call(args, stdout=subprocess.PIPE)

				elif datafile.endswith('.vcf.gz'):
					args_str = 'tabix -p vcf {0}'.format(datafile)
					args = shlex.split(args_str)
					print 'Running {0}'.format(args_str)
					p = subprocess.call(args, stdout=subprocess.PIPE)

				

tabix_data(datafiles)
	
# Split structural variant file by type #
######################################### 

