#!/usr/bin/env python2

'''
Generates the trackList.json for the facted track selector using the data directory

(Update description)

e.g: 
python make_faceted_tracks.py /data/jbrowse/data /data/jbrowse/data/trackList.json
'''

import json
import sys
import os

# Below should be in a function
# Get the directory paths from commandline 

data_dir = sys.argv[1]
trackList_file = sys.argv[2]

# Iterate through files in data directory and save paths to list

datafiles = []

for root, dirs, files in os.walk(data_dir):
	for name in files:
		datafiles.append(os.path.join(root, name))

def get_toplvlfeats(datafilepath):
	'''Retrieves all top level features for splitting a datafile into separate tracks'''

	import re

	features = []
	existing_feats = {}
	feature_file_pat = '.+_toplvlfeats.txt'

	for datafile in datafiles:
		if re.search(feature_file_pat, datafile):
			with open(datafile, 'r') as handle:
				exist_features = set(handle.readlines())
				existing_feats[datafile] = [exist_feature.strip()[1:-1] for exist_feature in exist_features]
		
	if datafilepath.endswith('vcf.gz'):
		# Need to fix this to make it more efficient
		feature_file = '{0}_toplvlfeats.txt'.format(datafilepath) 

		if feature_file in datafiles:
			with open(feature_file, 'r') as handle:
				features = set(handle.readlines())
				features = [feature.strip() for feature in features]

		else:
			get_features = True
			for bulk_file in existing_feats:
				for feat in existing_feats[bulk_file]:
					if feat in datafilepath:
						get_features = False
					
			if get_features:
				# Run the bash script to generate the feature file
				print 'Feature file not found for, ' + datafilepath

				import subprocess, shlex

				args_str = './get_toplvlfeats.sh {0} {1}'.format(datafilepath, 'vcf')
				args = shlex.split(args_str)
				print 'Running {0}'.format(args_str)
				# p1 = subprocess.call(args, stdout=subprocess.PIPE)	

				with open(feature_file, 'r') as handle:
					features = set(handle.readlines())
					features = [feature.strip() for feature in features]


	elif datafilepath.endswith('gff3.gz'):
		feature_file = '{0}_toplvlfeats.txt'.format(datafilepath) 
		if feature_file in datafiles:
			with open(feature_file, 'r') as handle:
				features = set(handle.readlines())
				features = [feature.strip() for feature in features]

		else:
			get_features = True
			for bulk_file in existing_feats:
				for feat in existing_feats[bulk_file]:
					if feat in datafilepath:
						get_features = False
					
			if get_features:
				# Run the bash script to generate the feature file
				print 'Feature file not found for, ' + datafilepath

				import subprocess, shlex

				args_str = './get_toplvlfeats.sh {0} {1}'.format(datafilepath, 'gff3')
				args = shlex.split(args_str)
				print 'Running {0}'.format(args_str)
				# p1 = subprocess.call(args, stdout=subprocess.PIPE)	

				with open(feature_file, 'r') as handle:
					features = set(handle.readlines())
					features = [feature.strip() for feature in features]

			
	return features

def make_vcf_track(datafilepath):
	vcf_keys = ['label', 'key', 'storeClass', 'urlTemplate', 'type']
	datafile_track = {key:'' for key in vcf_keys}

	datafile_track['label'] = os.path.basename(datafilepath)
	datafile_track['key'] = os.path.basename(datafilepath)[:-3]
	datafile_track['storeClass'] ='JBrowse/Store/SeqFeature/VCFTabix' 
	datafile_track['urlTemplate'] = os.path.relpath(datafilepath, data_dir)
	datafile_track['type'] = 'JBrowse/View/Track/CanvasFeatures'
	datafile_track['maxFeatureScreenDensity'] = 0.01

	return datafile_track

def make_gff_track(datafilepath, feature=None):
	gff_keys = ['label', 'key', 'storeClass', 'urlTemplate', 'type']
	datafile_track = {key:'' for key in gff_keys}
	
	if feature:
		datafile_track['label'] = '{0}_{1}.gff3.gz'.format(os.path.basename(datafilepath)[:-8], feature)
		datafile_track['key'] = '{0}_{1}.gff3.gz'.format(os.path.basename(datafilepath)[:-8], feature)
		datafile_track['storeClass'] ='JBrowse/Store/SeqFeature/GFF3Tabix' 
		datafile_track['urlTemplate'] = os.path.relpath(datafilepath, data_dir)
		datafile_track['type'] = 'JBrowse/View/Track/CanvasFeatures'
		datafile_track['chunkSizeLimit'] = 2000000
		datafile_track['dontRedispatch'] = 'chromosome'
		datafile_track['topLevelFeatures'] = feature
		datafile_track['maxFeatureScreenDensity'] = 0.01

	else:
		datafile_track['label'] = os.path.basename(datafilepath)
		datafile_track['key'] = os.path.basename(datafilepath)[:-3]
		datafile_track['storeClass'] ='JBrowse/Store/SeqFeature/GFF3Tabix' 
		datafile_track['urlTemplate'] = os.path.relpath(datafilepath, data_dir)
		datafile_track['type'] = 'JBrowse/View/Track/CanvasFeatures'
		datafile_track['chunkSizeLimit'] = 2000000
		datafile_track['dontRedispatch'] = 'chromosome'
		datafile_track['maxFeatureScreenDensity'] = 0.01

	return datafile_track

def make_bed_track(datafilepath):
	bed_keys = ['label', 'key', 'storeClass', 'urlTemplate', 'type']
	datafile_track = {key:'' for key in bed_keys}
	
	datafile_track['label'] = os.path.basename(datafilepath)
	datafile_track['key'] = os.path.basename(datafilepath)[:-3]
	datafile_track['storeClass'] ='JBrowse/Store/SeqFeature/BEDTabix' 
	datafile_track['urlTemplate'] = os.path.relpath(datafilepath, data_dir)
	datafile_track['type'] = 'JBrowse/View/Track/CanvasFeatures'
	datafile_track['maxFeatureScreenDensity'] = 0.01
	
	return datafile_track



def make_track_dicts(datafiles):
	'''Makes a list of all the track dictionaries'''
	import re
	import subprocess, shlex

	chr_split_pat = '.+chr.*([0-9]{1,2}|[XY]|MT).*(?<!(tbi))$'
	chr_joined_pat = '.+chr(_all|.gff3).*'

	track_dicts = []
	for datafile in datafiles:
		if re.search(chr_joined_pat, datafile):
			if datafile.endswith('.vcf.gz'):
				if datafile.endswith('variations.vcf.gz'): 
					features = get_toplvlfeats(datafile)
					for feature in features:
						# Split vcf file by variant type
						# bcftools filter -i'SVTYPE="indel"' homo_sapiens_structural_variations.vcf.gz -o homo_sapiens_structural_variations_indel.vcf.gz -O z
						
						output_file = '{0}_{1}.vcf.gz'.format(datafile[:-7], feature[1:-1])
						
						if output_file not in datafiles:

							args_str = 'bcftools filter -i\'SVTYPE="{0}"\' {1} -o {2} -O z '.format(feature[1:-1], datafile, output_file)
							args = shlex.split(args_str)
							print 'Running {0}'.format(args_str)
							p1 = subprocess.call(args, stdout=subprocess.PIPE)	

							args_str_tabix = 'tabix -p vcf {0}'.format(output_file)
							args_tabix = shlex.split(args_str)
							print 'Running {0}'.format(args_str_tabix)
							p1 = subprocess.call(args_tabix, stdout=subprocess.PIPE)	
						

						vcf_datafile_track = make_vcf_track(output_file)
						track_dicts.append(vcf_datafile_track)
				else:
					vcf_datafile_track = make_vcf_track(datafile)
					track_dicts.append(vcf_datafile_track)

			elif datafile.endswith('.gff3.gz') or datafile.endswith('.gff.gz'):
				if '/gff3/' in datafile:
					features = get_toplvlfeats(datafile)
					for feature in features:
						gff_datafile_track = make_gff_track(datafile, feature)
						track_dicts.append(gff_datafile_track)
				else:	
					gff_datafile_track = make_gff_track(datafile)
					track_dicts.append(gff_datafile_track)
			elif datafile.endswith('.bed.gz'):
				# Add clause for removing repeats of gff files in regulation
				pass
				#bed_datafile_track = make_bed_track(datafile)
				#track_dicts.append(bed_datafile_track)
				
		if not re.search(chr_split_pat, datafile):
			if datafile.endswith('.vcf.gz'):
				if 'structural' in datafile:
					features = get_toplvlfeats(datafile)
					for feature in features:
						# Split vcf file by variant type
						# bcftools filter -i'SVTYPE="indel"' homo_sapiens_structural_variations.vcf.gz -o homo_sapiens_structural_variations_indel.vcf.gz -O z
						
						output_file = '{0}_{1}.vcf.gz'.format(datafile[:-7], feature[1:-1])
						
						if output_file not in datafiles:

							args_str = 'bcftools filter -i\'SVTYPE="{0}"\' {1} -o {2} -O z '.format(feature[1:-1], datafile, output_file)
							args = shlex.split(args_str)
							print 'Running {0}'.format(args_str)
							p1 = subprocess.call(args, stdout=subprocess.PIPE)	

							args_str_tabix = 'tabix -p vcf {0}'.format(output_file)
							args_tabix = shlex.split(args_str)
							print 'Running {0}'.format(args_str_tabix)
							p1 = subprocess.call(args_tabix, stdout=subprocess.PIPE)	
						

						vcf_datafile_track = make_vcf_track(output_file)
						track_dicts.append(vcf_datafile_track)
				else:
					vcf_datafile_track = make_vcf_track(datafile)
					track_dicts.append(vcf_datafile_track)

			elif datafile.endswith('.gff3.gz') or datafile.endswith('.gff.gz'):
				if '/gff3/' in datafile:
					features = get_toplvlfeats(datafile)
					for feature in features:
						gff_datafile_track = make_gff_track(datafile, feature)
						track_dicts.append(gff_datafile_track)
				else:	
					gff_datafile_track = make_gff_track(datafile)
					track_dicts.append(gff_datafile_track)

			elif datafile.endswith('.bed.gz'):
				# Add clause for removing repeats of gff files in regulation
				datafile_tbi = '{0}.tbi'.format(datafile)
				if 'ensembl' not in datafile and datafile_tbi in datafiles:
					bed_datafile_track = make_bed_track(datafile)
					track_dicts.append(bed_datafile_track)
				
	return track_dicts

track_dicts = make_track_dicts(datafiles)

# Convert dictionary to JSON and append vcf to trackList.json

decoded_json = {}
with open(trackList_file, 'r') as tLjson:
	decoded_json = json.load(tLjson)
	json_urls = [json_track['urlTemplate'] for json_track in decoded_json['tracks']]

	for track in track_dicts:
		if track['urlTemplate'] not in json_urls:
			print 'Adding {0} to track list'.format(track['key'])
			decoded_json['tracks'].append(track)

with open(trackList_file, 'w') as tLjson:
	json.dump(decoded_json, tLjson, indent=4)



