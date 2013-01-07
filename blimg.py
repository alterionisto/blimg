import os
import re
import urllib.request
import urllib.parse
from argparse import ArgumentParser
import pprint


def size_filter(_dir, _size):
	for (path, dirs, files) in os.walk(_dir):
		for f in files:
			fullpath = os.path.join(path, f)
			if os.path.getsize(fullpath) / 1024 < _size:
				os.remove(fullpath)
				print("removed", fullpath)


def download(_url):
	url = _url[:]
	global uid
	blogname = re_blogname.search(url)
	if blogname:
		blogname = blogname.group(1)
	else:
		print("invalid url:", url)
		return
	if args.organize and not os.path.exists(os.path.join(args.destination, blogname)):
		os.makedirs(os.path.join(args.destination, blogname))
	while True:
		print("requesting:", url)
		try:
			page = urllib.request.urlopen(url)
			page = page.read().decode("utf-8").split("\n")
		except Exception as e:
			print("request failed:", e)
			break
		link = None
		images = []
		for line in page:
			if not link and direction in line:
				link = line
			if not args.wget:
				if re_rel.search(line):
					continue
				img = re_image.search(line)
				if img:
					images.append(img.group(1))
		if not link:
			print("link not found")
			break
		if args.organize:
			outdir = os.path.join(args.destination, blogname)
		else:
			outdir = args.destination
		if args.wget:
			code = os.system("wget -P {} -A jpeg,bmp,gif,png,jpg {}".format(outdir, url))
			if code:
				print("wget return code:", code)
		else:
			print("images found:", len(images))
			for href in images:
				end = re_filename.search(href)
				if end:
					try:
						imagefile = str(end.group(0))
						name, ext = os.path.splitext(imagefile)
						if not args.rewrite:
							newname = name
							while os.path.exists(os.path.join(outdir, newname + ext)):
								newname = name + str(uid)
								uid += 1
							name = newname
						filename = os.path.join(outdir, name + ext)
						urllib.request.urlretrieve(href, filename)
					except Exception as e:
						print("failed to download {}: {}".format(href, e))
		if args.size:
			size_filter(outdir, args.size)
		newurl = re_link.search(link)
		if newurl:
			url = newurl.group(1)
		else:
			print("next post url not found")
			break
		if not url:
			print("url is empty")
			break

uid = 1
re_image = re.compile("(http://[0-9]\.bp\.blogspot\.com\S*[jpg|png|bmp|gif|jpeg])\"")
re_link = re.compile("href=\'(.*?)\'")
re_filename = re.compile("[0-9a-zA-Z-+]*\.jpg")
re_rel = re.compile("rel=\"image_src\"")
re_blogname = re.compile("([a-z0-9A-Z]*)\.blogspot.com")
uid = 1

parser = ArgumentParser(description="Blogspot image downloader")
parser.add_argument("-u", "--url", default=None, dest="url",
	help="starting blog post address")
parser.add_argument("-i", "--direction",
	choices=["newer", "older"], default="older", dest="direction",
	help="direction of download")
parser.add_argument("-d", "--destination", default=r"C:\test", dest="destination",
	help="destination directory")
parser.add_argument("-w", "--wget", action="store_true", dest="wget",
	help="use wget for image downloading")
parser.add_argument("-r", "--rewrite", action="store_true", dest="rewrite",
	help="allow rewriting of existing files")
parser.add_argument("-f", "--file", dest="file",
	help="download images from all blogs specified in file")
parser.add_argument("-o", "--organize", action="store_true", dest="organize",
	help="if --file specified, store images from each one in separate folders")
parser.add_argument("-s", "--size", dest="size",
	help="delete everything smaller than -s KiB")
args = parser.parse_args()
pprint.pprint(args.__dict__)

if not args.url and not args.file:
	raise SystemExit("no input specified")
if args.url and args.file:
	raise SystemExit("choose only one input method, either -u or -f")
if not os.path.isdir(args.destination):
	os.makedirs(args.destination)
if args.direction == "older":
	direction = "Blog1_blog-pager-older-link"
else:
	direction = "Blog1_blog-pager-newer-link"
if args.wget and os.system("wget --help"):
	raise SystemExit("wget not found")
try:
	if args.file:
		for line in open(args.file).read().split("\n"):
			download(line)
	else:
		download(args.url)
except KeyboardInterrupt:
	raise SystemExit("interrupted by user")
