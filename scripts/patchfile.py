#!/usr/bin/env python3

# For Qualcomm based Samsung Galaxy S4 only!

import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ramdisk_offset  = "0x02000000"
rootdir         = os.path.dirname(os.path.realpath(__file__))
rootdir         = os.path.join(rootdir, "..")
ramdiskdir      = os.path.join(rootdir, "ramdisks")
patchdir        = os.path.join(rootdir, "patches")
binariesdir     = os.path.join(rootdir, "binaries")
remove_dirs     = []

mkbootimg       = "mkbootimg"
unpackbootimg   = "unpackbootimg"
if os.name == "nt":
  mkbootimg     = "mkbootimg.exe"
  unpackbootimg = "unpackbootimg.exe"

def clean_up_and_exit(exit_status):
  for d in remove_dirs:
    shutil.rmtree(d)
  sys.exit(exit_status)

def read_file_one_line(filepath):
  f = open(filepath, 'r')
  line = f.readline()
  f.close()
  return line.strip('\n')

def run_command(command):
  try:
    process = subprocess.Popen(
      command,
      stdout = subprocess.PIPE,
      universal_newlines = True
    )
    output = process.communicate()[0]
    exit_status = process.returncode
    return (exit_status, output)
  except:
    print("Failed to run command: \"%s\"" % ' '.join(command))
    clean_up_and_exit(1)

def apply_patch_file(patchfile, directory):
  patch = "patch"
  if os.name == "nt":
    # Windows wants anything named patch.exe to run as Administrator
    patch = os.path.join(binariesdir, "hctap.exe")

  exit_status, output = run_command(
    [ patch,
      '-p', '1',
      '-d', directory,
      '-i', os.path.join(patchdir, patchfile)]
  )
  if exit_status != 0:
    print("Failed to apply patch")
    clean_up_and_exit(1)

def patch_boot_image(boot_image, vendor):
  tempdir = tempfile.mkdtemp()
  remove_dirs.append(tempdir)

  exit_status, output = run_command(
    [ os.path.join(binariesdir, unpackbootimg),
      '-i', boot_image,
      '-o', tempdir]
  )
  if exit_status != 0:
    print("Failed to extract boot image")
    clean_up_and_exit(1)

  prefix   = os.path.join(tempdir, os.path.split(boot_image)[1])
  base     = "0x" + read_file_one_line(prefix + "-base")
  cmdline  =        read_file_one_line(prefix + "-cmdline")
  pagesize =        read_file_one_line(prefix + "-pagesize")
  os.remove(prefix + "-base")
  os.remove(prefix + "-cmdline")
  os.remove(prefix + "-pagesize")
  os.remove(prefix + "-ramdisk.gz")
  shutil.move(prefix + "-zImage", os.path.join(tempdir, "kernel.img"))

  if vendor == "ktoonsez":
    print("Using patched ktoonsez ramdisk")
    ramdisk = "ktoonsez.dualboot.cpio.gz"
  else:
    print("Using patched Cyanogenmod ramdisk")
    ramdisk = "cyanogenmod.dualboot.cpio.gz"

  ramdisk = os.path.join(ramdiskdir, ramdisk)
  shutil.copyfile(ramdisk, os.path.join(tempdir, "ramdisk.cpio.gz"))

  exit_status, output = run_command(
    [ os.path.join(binariesdir, mkbootimg),
      '--kernel',         os.path.join(tempdir, "kernel.img"),
      '--ramdisk',        os.path.join(tempdir, "ramdisk.cpio.gz"),
      '--cmdline',        cmdline,
      '--base',           base,
      '--pagesize',       pagesize,
      '--ramdisk_offset', ramdisk_offset,
      '--output',         os.path.join(tempdir, "complete.img")]
  )

  os.remove(os.path.join(tempdir, "kernel.img"))
  os.remove(os.path.join(tempdir, "ramdisk.cpio.gz"))

  if exit_status != 0:
    print("Failed to create boot image")
    clean_up_and_exit(1)

  return os.path.join(tempdir, "complete.img")

def patch_zip(zip_file, vendor):
  tempdir = tempfile.mkdtemp()
  remove_dirs.append(tempdir)

  z = zipfile.ZipFile(zip_file, "r")
  z.extractall(tempdir)
  z.close()

  boot_image = os.path.join(tempdir, "boot.img")
  new_boot_image = patch_boot_image(boot_image, vendor)

  os.remove(boot_image)
  shutil.move(new_boot_image, boot_image)

  if vendor == "ktoonsez":
    apply_patch_file("ktoonsez.dualboot.patch", tempdir)

  new_zip_file = os.path.join(tempdir, "complete.zip")
  z = zipfile.ZipFile(new_zip_file, 'w', zipfile.ZIP_DEFLATED)
  for root, dirs, files in os.walk(tempdir):
    for f in files:
      if f == "complete.zip":
        continue
      arcdir = os.path.relpath(root, start = tempdir)
      z.write(os.path.join(root, f), arcname = os.path.join(arcdir, f))
  z.close()

  return new_zip_file

def detect_kernel_vendor(path):
  if re.search(r"KT-SGS4-JB4.3-AOSP-.*.zip", path):
    print("Detected ktoonsez kernel zip")
    return "ktoonsez"
  else:
    return "UNKNOWN"

def detect_file_type(path):
  if path.endswith(".zip"):
    return "zip"
  elif path.endswith(".img"):
    return "img"
  else:
    return "UNKNOWN"

if len(sys.argv) < 2:
  print("Usage: %s [kernel file]" % sys.argv[0])
  clean_up_and_exit(1)

filename = sys.argv[1]

if not os.path.exists(filename):
  print("%s does not exist!" % filename)
  clean_up_and_exit(1)

filename = os.path.abspath(filename)
filetype = detect_file_type(filename)
kernel_vendor = detect_kernel_vendor(filename)

if filetype == "UNKNOWN":
  print("Unsupported file")
  clean_up_and_exit(1)

if filetype == "zip":
  if kernel_vendor == "UNKNOWN":
    print("Unsupported kernel zip")
    clean_up_and_exit(1)

  newfile = patch_zip(filename, kernel_vendor)
  print("Successfully patched kernel zip")
  newpath = re.sub(r"\.zip$", "_dualboot.zip", filename)
  shutil.move(newfile, newpath)
  print("Path: " + newpath)

elif filetype == "img":
  newfile = patch_boot_image(filename, kernel_vendor)
  print("Successfully patched boot image")
  newpath = re.sub(r"\.img$", "_dualboot.img", filename)
  shutil.move(newfile, newpath)
  print("Path: " + newpath)

clean_up_and_exit(0)