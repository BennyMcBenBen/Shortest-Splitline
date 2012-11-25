'''
prepare.py provides utilities for downloading and processing state census files.

@author: Ben
'''
import csv
import os
import urllib2
import zipfile

def download(url, download_dir):
  if not os.path.exists(download_dir):
	    os.makedirs(download_dir)

  file_name = url.split('/')[-1]
  u = urllib2.urlopen(url)
  f = open(download_dir + file_name, 'wb')
  meta = u.info()
  file_size = int(meta.getheaders("Content-Length")[0])
  print "Downloading: %s Bytes: %s" % (file_name, file_size)

  file_size_dl = 0
  block_sz = 8192
  while True:
    buffer = u.read(block_sz)
    if not buffer:
      break

    file_size_dl += len(buffer)
    f.write(buffer)
    status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
    status = status + chr(8)*(len(status)+1)
    print status,

  f.close()

def extract_census_files(download_dir, state_abbr):
  zip_file_name = state_abbr + "2010.sf1.zip"
  zip_file = zipfile.ZipFile(download_dir + zip_file_name, "r")

  block_file_name = get_block_file_name(state_abbr)
  print "Extracting %s..." % (block_file_name)
  zip_file.extract(block_file_name, download_dir)

  geo_file_name = get_geo_file_name(state_abbr)
  print "Extracting %s..." % (geo_file_name)
  zip_file.extract(geo_file_name, download_dir)

  zip_file.close()

  print "Deleting %s..." % (zip_file_name)
  os.remove(download_dir + zip_file_name)

def get_block_file_name(state_abbr):
  return state_abbr + "000012010.sf1"

def get_geo_file_name(state_abbr):
  return state_abbr + "geo2010.sf1"

def prepare_alabama():
  state = "Alabama"
  state_abbr = "al"
  zip_file_name = state_abbr + "2010.sf1.zip"
  download_dir = "../../resources/" + state_abbr + "/"
  filepath = download_dir + zip_file_name
  url = "http://www2.census.gov/census_2010/04-Summary_File_1/" + state + "/" + zip_file_name

  #try:
  #  with open(filepath) as f: pass
  #except IOError as e:
  #  download(url, download_dir)

  #extract_census_files(download_dir, state_abbr)
  write_csv(download_dir, state_abbr)


def write_csv(download_dir, state_abbr):
  block_file_name = get_block_file_name(state_abbr)
  geo_file_name = get_geo_file_name(state_abbr)

  pop = {}
  with open(download_dir + block_file_name, 'r') as block_file:
    block_reader = csv.reader(block_file)
    for block_row in block_reader:
      rec_num = block_row[4]
      block_pop = block_row[5]
      pop[rec_num] = block_pop

  csv_file_name = state_abbr + ".csv"
  with open(download_dir + csv_file_name, 'w') as csv_file:
    csv_writer = csv.writer(csv_file)
    with open(download_dir + geo_file_name, 'r') as geo_file:
      for line in geo_file:
        region = line[8:11]
        if region == "101":
          rec_num = line[18:25]
          tract = line[55:61]
          group = line[61:62]
          lat = line[336:347]
          lon = line[347:359]
          block_pop = pop[rec_num]
          row = [tract, group, rec_num, block_pop, lat, lon]
          csv_writer.writerow(row)    

prepare_alabama()
