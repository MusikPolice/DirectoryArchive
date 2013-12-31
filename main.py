#!/usr/bin/env python
import os
import sys
import zipfile
import argparse

# An argparse class that validates that an input string is a path to a readable directory
class readable_writable_dir(argparse.Action):
	def __call__(self,parser, namespace, values, option_string=None):
		prospective_dir=values
		if not os.path.isdir(prospective_dir):
			raise argparse.ArgumentTypeError("readable_dir:{0} is not a valid path".format(prospective_dir))
		if not os.access(prospective_dir, os.R_OK):
			raise argparse.ArgumentTypeError("readable_dir:{0} cannot read directory".format(prospective_dir))
		if not os.access(prospective_dir, os.W_OK):
			raise argparse.ArgumentTypeError("readable_dir:{0} cannot write to directory".format(prospective_dir))
		setattr(namespace,self.dest,prospective_dir)

# Prints a pretty little progress message to the terminal 
def update_progress(current, total):
	progress = int(current / float(total) * 100)
	sys.stdout.write('\r\tAdding file {0} of {1} ({2}%)'.format(current, total, progress))
	if current == total:
		sys.stdout.write('\n')
	sys.stdout.flush()

# Adds all files at the specified path to the specified zip file, relative to path
# zip must be a ZipFile type that is open for writing
def zipdir(path, zip):
	for root, dirs, files in os.walk(path):
		count = 0
		for file in files:
			count += 1
			update_progress(count, len(files))
			abspath = os.path.join(root, file)
			relpath = os.path.relpath(abspath, os.path.dirname(path))
			zip.write(abspath, relpath)

# Application entry
if __name__ == '__main__':
	# get args
	parser = argparse.ArgumentParser(description='Replaces each sub-directory of the specified directory with a *.zip archive that contains a compressed copy of the sub-directory\'s contents')
	parser.add_argument('directory', action=readable_writable_dir, help='The top-level directory. All sub-directories of this directory will be archived.')
	parser.add_argument('-d', '--delete-subdirs', dest='delete', action='store_true', help='Delete subdirectories after they are archived')
	args = parser.parse_args()
	directory = os.path.abspath(args.directory)

	# iterate over sub directories
	for d in os.listdir(directory):
		subdir = os.path.join(directory, d)
		if os.path.isdir(subdir):

			# create a zip file for each subdir and add its contents to the archive
			print 'Archiving ' + subdir
			with zipfile.ZipFile(subdir + '.zip', mode='w', compression=zipfile.ZIP_DEFLATED, allowZip64=True) as zipf:
				zipdir(subdir, zipf)

			if (args.delete):
				# finally, delete the subdir
				print '\tDeleting ' + subdir
				for root, dirs, files in os.walk(subdir, topdown=False):
					for name in files:
						os.remove(os.path.join(root, name))
					for name in dirs:
						os.rmdir(os.path.join(root, name))
				os.rmdir(subdir)
	print 'Done'
