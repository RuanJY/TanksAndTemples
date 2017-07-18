# ----------------------------------------------------------------------------
# -                        Open3D: www.open3d.org                            -
# ----------------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2017 Arno Knapitsch <arno.knapitsch@gmail.com >
#                    Jaesik Park <syncle@gmail.com>
#                    Qian-Yi Zhou <Qianyi.Zhou@gmail.com>
#                    Vladlen Koltun <vkoltun@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# ----------------------------------------------------------------------------
#
# This script is for downloading reconstruction result from
# www.tanksandtemples.org
# If you are using this software, please refer following paper.
#
# @article{Knapitsch2017,
#    author    = {Arno Knapitsch and Jaesik Park and Qian-Yi Zhou and Vladlen Koltun},
#    title     = {Tanks and Temples: Benchmarking Large-Scale Scene Reconstruction},
#    journal   = {ACM Transactions on Graphics},
#    volume    = {36},
#    number    = {4},
#    year      = {2017},
#}
#

import sys
import os
import argparse
import zipfile
import hashlib

if (sys.version_info > (3, 0)):
	pversion = 3
	from urllib.request import Request, urlopen
else:
	pversion = 2
	from urllib2 import Request, urlopen


sep = os.sep
parser = argparse.ArgumentParser(description='Tanks and Temples file downloader')
parser.add_argument('--modality', type=str, help='(image|video|both) choose if you want to download video sequences (very big) or pre sampled image sets', default='image')
parser.add_argument('--group', type=str, help='(intermediate|advanced|both) choose if you want to download intermediate or advanced dataset', default='both')
parser.add_argument('--pathname', type=str, help='chose destination path name, default = local path', default='')
parser.add_argument('-s', action='store_true', default=False, dest='status', help='show data status')
parser.add_argument('--unpack_off', action='store_false', default=True, dest='unpack', help='do not un-zip the folders after download')
parser.add_argument('--calc_md5_off', action='store_false', default=True, dest='calc_md5', help='do not calculate md5sum after download')


def generate_file_md5(filename, blocksize=2**20):
    m = hashlib.md5()
    with open(filename, "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update( buf )
    return m.hexdigest()


# download file into folder "scene_out_dir" without progress bar
def download_file_url(url, scene_out_dir):
	q = Request(url)
	chunk_size=4024
	if not os.path.exists(scene_out_dir):
		os.makedirs(scene_out_dir)
	local_filename = scene_out_dir + sep + url.split('/')[-1]
	if os.path.exists(local_filename):
		write_str = "ab"
		#If the file exists, then only download the remainder
		existSize = os.path.getsize(local_filename)
	else:
		write_str = "wb"
		existSize = 0

	response = urlopen(q)
	total_length = int(response.headers.get('content-length'))
	q.add_header('Range',"bytes=%s-" % (existSize ))

	dl = existSize

	if(total_length>existSize):
		response = urlopen(q)
		try:
			with open(local_filename, write_str) as f:
				while True:
					chunk = response.read(chunk_size)
					if not chunk:
						break
					if chunk:
						dl += len(chunk)
						f.write(chunk)
						done = int(50 * dl / total_length)
						sys.stdout.write("\r[%s%s] %2.1f%% of %5.0f MB" % ('=' * done, ' ' * (50-done), 100*float(dl) / total_length, float(dl)/1000000) )
						sys.stdout.flush()
		except KeyboardInterrupt:
			pass
	else:
		dl = existSize
		done = int(50 * dl / total_length)
		sys.stdout.write("\r[%s%s] %2.1f%% of %5.0f MB" % ('=' * done, ' ' * (50-done), 100*float(dl) / total_length, float(dl)/1000000) )
		sys.stdout.flush()
	return local_filename


# download file into folder "scene_out_dir" without progress bar
def download_file_url2(url, scene_out_dir):
	q = Request(url)
	chunk_size=4024
	if not os.path.exists(scene_out_dir):
		os.makedirs(scene_out_dir)
	local_filename = scene_out_dir + sep + url.split('/')[-1]
	write_str = "wb"
	existSize = 0

	dl = existSize
	response = urlopen(q)
	try:
		with open(local_filename, write_str) as f:
			while True:
				chunk = response.read(chunk_size)
				if not chunk:
					break
				if chunk:
					dl += len(chunk)
					f.write(chunk)

	except KeyboardInterrupt:
		pass
	return local_filename


def download_video(pathname, link_gc, scene, image_md5_dict, calc_md5):
	scene_out_dir = pathname + 'videos'
	download_file = link_gc + scene + '.mp4'
	print('\ndownloading video ' + download_file.split('/')[-1])
	local_fn = download_file_url(download_file, scene_out_dir)
	download_file_local = scene_out_dir + sep + scene + '.mp4'

	if(calc_md5):
		h_md5 = generate_file_md5(download_file_local)
		print('\nmd5 downloaded: ' + h_md5)
		print('md5 original:   ' + video_md5_dict[scene])
		md5_check = h_md5 == video_md5_dict[scene]

		if(md5_check):
			if(unpack):
				extr_dir = scene_out_dir

				zip_file = scene_out_dir + sep + scene + '.zip'
				if(zipfile.is_zipfile(zip_file)):
					if not os.path.exists(extr_dir):
						os.makedirs(extr_dir)
					zip = zipfile.ZipFile(zip_file,'r')
					zip.extractall(extr_dir)
		else:
			print('\nWarning: MD5 does not match, delete file and restart download\n')
	else:
		if(unpack):
			extr_dir = scene_out_dir
			zip_file = scene_out_dir + sep + scene + '.zip'
			if(zipfile.is_zipfile(zip_file)):
				if not os.path.exists(extr_dir):
					os.makedirs(extr_dir)
				zip = zipfile.ZipFile(zip_file,'r')
				zip.extractall(extr_dir)

def check_video(pathname, scene, image_md5_dict):
	scene_out_dir = pathname + 'videos'
	download_file = link_gc + scene + '.mp4'
	ret_str = ' '
	download_file_local = scene_out_dir + sep + scene + '.mp4'

	if os.path.exists(download_file_local):
		h_md5 = generate_file_md5(download_file_local)
		md5_check = h_md5 == video_md5_dict[scene]

		if(md5_check):
			ret_str = 'X'
		else:
			ret_str = '?'
	else:
		ret_str = ' '
	return ret_str


def download_image_sets(pathname, link_gc_is, scene, image_md5_dict, calc_md5):
	scene_out_dir = pathname + 'image_sets'
	download_file = link_gc_is + scene + '.zip'
	download_file_local = scene_out_dir + sep + scene + '.zip'
	print('\ndownloading image set ' + download_file.split('/')[-1])
	local_fn = download_file_url(download_file, scene_out_dir)

	if(calc_md5):
		#h_md5 = hashlib.md5(open(download_file_local,'rb').read()).hexdigest()
		h_md5 = generate_file_md5(download_file_local)
		print('\nmd5 downloaded: ' + h_md5)
		print('md5 original:   ' + image_md5_dict[scene])
		md5_check = h_md5 == image_md5_dict[scene]

		if(md5_check):
			if(unpack):
				extr_dir = scene_out_dir

				zip_file = scene_out_dir + sep + scene + '.zip'
				if(zipfile.is_zipfile(zip_file)):
					if not os.path.exists(extr_dir):
						os.makedirs(extr_dir)
					zip = zipfile.ZipFile(zip_file,'r')
					zip.extractall(extr_dir)
					#Archive(zip_file).extractall()
		else:
			print('\nWarning: MD5 does not match, delete file and restart download\n')


def check_image_sets(pathname, scene, image_md5_dict):
	scene_out_dir = pathname + 'image_sets'
	ret_str = ''
	download_file_local = scene_out_dir + sep + scene + '.zip'

	if os.path.exists(download_file_local):
		h_md5 = generate_file_md5(download_file_local)
		md5_check = h_md5 == image_md5_dict[scene]
		if(md5_check):
			ret_str = 'X'
		else:
			ret_str = '?'
	else:
		ret_str = ' '
	return ret_str


def print_status(sequences, modality, pathname, intermediate_list, advanced_list, image_md5_dict, video_md5_dict):
	#print('intermediate Dataset \t\t\t Video \t\t\t image set')
	print('\n\n data status: \n\n')
	print('[X] - downloaded    [ ] - missing    [?] - being downloaded or corrupted    [n] - not checked')

	if (sequences == 'intermediate' or sequences == 'both' or sequences == ''):
		print('\n\n-----------------------------------------------------------------')
		line_new = '%12s  %12s  %12s' % (' intermediate Dataset', 'Video', 'image set')
		print(line_new)
		print('-----------------------------------------------------------------')
		for scene in intermediate_list:
			#print(scene + '\t\t\t X \t\t\t X')
			line_new = '%12s  %19s  %10s' % (scene, check_video(pathname, scene, video_md5_dict) if (modality == 'video' or modality == 'both' or modality == '') else 'n', check_image_sets(pathname, scene, image_md5_dict) if (modality == 'image' or modality == 'both' or modality == '') else 'n')
			print(line_new)

	if (sequences == 'advanced' or sequences == 'both' or sequences == ''):
		print('\n\n-----------------------------------------------------------------')
		line_new = '%12s  %16s  %12s' % (' advanced Dataset', 'Video', 'image set')
		print(line_new)
		print('-----------------------------------------------------------------')
		for scene in advanced_list:
			#print(scene + '\t\t\t X \t\t\t X')
			line_new = '%12s  %19s  %10s' % (scene, check_video(pathname, scene, video_md5_dict) if (modality == 'video' or modality == 'both' or modality == '') else 'n', check_image_sets(pathname, scene, image_md5_dict) if (modality == 'image' or modality == 'both' or modality == '') else 'n')
			print(line_new)


if __name__ == "__main__":
	link_gc ='https://storage.googleapis.com/t2-data/videos/'
	link_gc_is = 'https://storage.googleapis.com/t2-data/image_sets/'
	intermediate_list = ['Family','Francis','Horse','Lighthouse','M60','Panther','Playground','Train']
	advanced_list = ['Auditorium','Ballroom','Courtroom','Museum','Palace','Temple']

	args = parser.parse_args()
	sequences = args.group
	calc_md5 = args.calc_md5

	if sequences == 'intermediate':
		scene_list = intermediate_list
	elif sequences == 'advanced':
		scene_list = advanced_list
	elif sequences == 'both':
		scene_list = intermediate_list + advanced_list
	elif sequences == '':
		scene_list = intermediate_list + advanced_list
	else:
		sys.exit('Error! Unknown group parameter, see help [-h]')
	scene_list.sort()

	modality = args.modality
	unpack = args.unpack
	status_print = args.status
	pathname = args.pathname

	if pathname:
		pathname = pathname + sep

	# download md5 checksum file and create md5 dict for image sets zip files:
	image_md5_dict = {}
	scene_out_dir = pathname + 'image_sets'
	md5_file = link_gc_is + 'image_sets_md5.chk'
	local_fn = download_file_url2(md5_file, scene_out_dir)
	fname = scene_out_dir + sep + 'image_sets_md5.chk'
	with open(fname) as f:
		content = f.readlines()
		content = [x.strip() for x in content]

	for line in content:
		md5 = line.split(' ')[0]
		scene_name = line.split(' ')[-1][0:-4]
		image_md5_dict.update({scene_name:md5})

	# download md5 checksum file and create md5 dict for videos:
	video_md5_dict = {}
	scene_out_dir = pathname + 'videos'
	md5_file = link_gc + 'video_set_md5.chk'
	local_fn = download_file_url2(md5_file, scene_out_dir)
	fname = scene_out_dir + sep + 'video_set_md5.chk'
	with open(fname) as f:
		content = f.readlines()
		content = [x.strip() for x in content]

	for line in content:
		md5 = line.split(' ')[0]
		scene_name = line.split(' ')[-1][0:-4]
		video_md5_dict.update({scene_name:md5})

	if (len(sys.argv)==1):
		print_status('both', 'both', pathname, intermediate_list, advanced_list, image_md5_dict, video_md5_dict)

	elif status_print and (len(sys.argv)==2):
		print_status('both', 'both', pathname, intermediate_list, advanced_list, image_md5_dict, video_md5_dict)

	elif status_print:
		print_status(sequences, modality, pathname, intermediate_list, advanced_list, image_md5_dict, video_md5_dict)

	elif sequences or modality:
		for scene in scene_list:

			if modality == 'video':
				download_video(pathname, link_gc, scene, video_md5_dict, calc_md5)
			elif modality == 'image':
				download_image_sets(pathname, link_gc_is, scene, image_md5_dict, calc_md5)
			elif modality == 'both':
				download_image_sets(pathname, link_gc_is, scene, image_md5_dict, calc_md5)
				download_video(pathname, link_gc, scene, video_md5_dict, calc_md5)
			else:
				sys.exit('Error! Unknown modality parameter, see help [-h]')