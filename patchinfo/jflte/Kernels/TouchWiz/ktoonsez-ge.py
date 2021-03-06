from fileinfo import FileInfo
import re

file_info = FileInfo()

filename_regex           = r"^KT-SGS4-JB4.3-TWGE-.*\.zip$"
file_info.ramdisk        = 'jflte/GoogleEdition/GoogleEdition.def'
file_info.patch          = 'jflte/Kernels/AOSP/ktoonsez.dualboot.patch'

def matches(filename):
  if re.search(filename_regex, filename):
    if 'VZW' in filename or 'ATT' in filename:
      file_info.patch    = 'jflte/Kernels/AOSP/ktoonsez-loki.dualboot.patch'
      file_info.bootimg  = 'boot.lok'
      file_info.loki     = True
    return True
  else:
    return False

def print_message():
  print("Detected ktoonsez kernel zip")

def get_file_info():
  return file_info
