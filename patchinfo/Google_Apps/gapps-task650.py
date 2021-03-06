from fileinfo import FileInfo
import re

file_info = FileInfo()

filename_regex           = r"^gapps-jb\([0-9\.]+\)-[0-9\.]+\.zip$"
file_info.patch          = 'Google_Apps/gapps-task650.dualboot.patch'
file_info.has_boot_image = False

def matches(filename):
  if re.search(filename_regex, filename):
    return True
  else:
    return False

def print_message():
  print("Detected Task650's Google Apps zip")

def get_file_info():
  return file_info
