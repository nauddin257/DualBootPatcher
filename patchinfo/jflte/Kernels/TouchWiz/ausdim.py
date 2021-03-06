from fileinfo import FileInfo
import re

file_info = FileInfo()

filename_regex           = r"^v[0-9\.]+-Google-edition-ausdim-Kernel-.*\.zip$"
file_info.ramdisk        = 'jflte/TouchWiz/TouchWiz.def'
file_info.patch          = 'jflte/Kernels/TouchWiz/ausdim.dualboot.patch'

def matches(filename):
  if re.search(filename_regex, filename):
    return True
  else:
    return False

def print_message():
  print("Detected Ausdim kernel zip")

def get_file_info():
  return file_info
