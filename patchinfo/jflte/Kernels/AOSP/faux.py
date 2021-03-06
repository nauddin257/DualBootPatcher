from fileinfo import FileInfo
import re

file_info = FileInfo()

filename_regex           = r"^jflte[a-z]+-aosp-faux123-.*\.zip$"
file_info.ramdisk        = 'jflte/AOSP/AOSP.def'
file_info.patch          = 'jflte/Kernels/AOSP/faux.dualboot.patch'

def matches(filename):
  if re.search(filename_regex, filename):
    return True
  else:
    return False

def print_message():
  print("Detected faux kernel zip")

def get_file_info():
  return file_info
