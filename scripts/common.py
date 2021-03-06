import os
import re
import sys

## File manipulation

READ = 'r'
WRITE = 'wb'

def write(f, line):
  if sys.hexversion < 0x03000000:
    f.write(line)
  else:
    f.write(line.encode("UTF-8"))

def open_file(directory, f, flags):
  return open(os.path.join(directory, f), flags)

def get_lines_from_file(directory, f):
  f = open_file(directory, f, READ)
  lines = f.readlines()
  f.close()
  return lines

def write_lines_to_file(directory, f, lines):
  f = open_file(directory, f, WRITE)

  for i in lines:
    write(f, i)

  f.close()

def whitespace(line):
  m = re.search(r"^(\s+).*$", line)
  if m and m.group(1):
    return m.group(1)
  else:
    return ""

## Other stuff

def insert_line(index, line, lines):
  #lines.insert(index, (line + '\n').encode("UTF-8"))
  lines.insert(index, line + '\n')

def insert_dual_boot_sh(lines):
  insert_line(0, 'package_extract_file("dualboot.sh", "/tmp/dualboot.sh");', lines)
  insert_line(1, 'set_perm(0, 0, 0777, "/tmp/dualboot.sh");', lines)
  insert_line(2, 'ui_print("INSTALLING AS SECONDARY");', lines)
  return 3

def insert_write_kernel(bootimg, lines):
  # Look for last line containing the boot image string and insert after that
  i = 0
  while i < len(lines):
    if bootimg in lines[i]:
      insert_line(i + 1, 'run_program("/tmp/dualboot.sh", "set-secondary-kernel");', lines)
      break
    i += 1

def insert_mount_system(index, lines):
  insert_line(index, 'run_program("/tmp/dualboot.sh", "mount-system", "ext4", "/dev/block/platform/msm_sdcc.1/by-name/system");', lines)
  return 1

def insert_mount_cache(index, lines):
  insert_line(index, 'run_program("/tmp/dualboot.sh", "mount-cache", "ext4", "/dev/block/platform/msm_sdcc.1/by-name/cache");', lines)
  return 1

def insert_mount_data(index, lines):
  insert_line(index, 'run_program("/tmp/dualboot.sh", "mount-data", "ext4", "/dev/block/platform/msm_sdcc.1/by-name/userdata");', lines)
  return 1

def insert_unmount_system(index, lines):
  insert_line(index, 'run_program("/tmp/dualboot.sh", "unmount-system");', lines)
  return 1

def insert_unmount_cache(index, lines):
  insert_line(index, 'run_program("/tmp/dualboot.sh", "unmount-cache");', lines)
  return 1

def insert_unmount_data(index, lines):
  insert_line(index, 'run_program("/tmp/dualboot.sh", "unmount-data");', lines)
  return 1

def insert_format_system(index, lines):
  insert_line(index, 'run_program("/tmp/dualboot.sh", "format-system");', lines)
  return 1

def insert_format_cache(index, lines):
  insert_line(index, 'run_program("/tmp/dualboot.sh", "format-cache");', lines)
  return 1

def insert_format_data(index, lines):
  insert_line(index, 'run_program("/tmp/dualboot.sh", "format-data");', lines)
  return 1

def replace_mount_lines(lines):
  i = 0
  while i < len(lines):
    if re.search(r"^\s*mount\s*\(.*$", lines[i]) or \
       re.search(r"^run_program\s*\(\s*\"[^\"]*busybox\"\s*,\s*\"mount\".*$", lines[i]):
      # Mount /system as dual boot
      if 'system' in lines[i] or 'mmcblk0p16' in lines[i]:
        del lines[i]
        i += insert_mount_system(i, lines)

      # Mount /cache as dual boot
      elif 'cache' in lines[i] or 'mmcblk0p18' in lines[i]:
        del lines[i]
        i += insert_mount_cache(i, lines)

      # Mount /data as dual boot
      elif 'userdata' in lines[i] or 'mmcblk0p29' in lines[i]:
        del lines[i]
        i += insert_mount_data(i, lines)

      else:
        i += 1

    else:
      i += 1

def replace_unmount_lines(lines):
  i = 0
  while i < len(lines):
    if re.search(r"^\s*unmount\s*\(.*$", lines[i]) or \
       re.search(r"^run_program\s*\(\s*\"[^\"]*busybox\"\s*,\s*\"umount\".*$", lines[i]):
      # Mount /system as dual boot
      if 'system' in lines[i] or 'mmcblk0p16' in lines[i]:
        del lines[i]
        i += insert_unmount_system(i, lines)

      # Mount /cache as dual boot
      elif 'cache' in lines[i] or 'mmcblk0p18' in lines[i]:
        del lines[i]
        i += insert_unmount_cache(i, lines)

      # Mount /data as dual boot
      elif 'userdata' in lines[i] or 'mmcblk0p29' in lines[i]:
        del lines[i]
        i += insert_unmount_data(i, lines)

      else:
        i += 1

    else:
      i += 1

def replace_format_lines(lines):
  i = 0
  while i < len(lines):
    if re.search(r"^\s*format\s*\(.*$", lines[i]):
      # Mount /system as dual boot
      if 'system' in lines[i] or 'mmcblk0p16' in lines[i]:
        del lines[i]
        i += insert_format_system(i, lines)

      # Mount /cache as dual boot
      elif 'cache' in lines[i] or 'mmcblk0p18' in lines[i]:
        del lines[i]
        i += insert_format_cache(i, lines)

      # Mount /data as dual boot
      elif 'userdata' in lines[i] or 'mmcblk0p29' in lines[i]:
        del lines[i]
        i += insert_format_data(i, lines)

      else:
        i += 1

    else:
      i += 1

def unmount_everything(lines):
  i = len(lines)
  i += insert_unmount_system(i, lines)
  i += insert_unmount_cache(i, lines)
  i += insert_unmount_data(i, lines)

def attempt_auto_patch(lines, bootimg = None):
  insert_dual_boot_sh(lines)
  replace_mount_lines(lines)
  replace_unmount_lines(lines)
  replace_format_lines(lines)
  if bootimg:
    insert_write_kernel(bootimg, lines)
  # Too many ROMs don't unmount partitions after installation
  unmount_everything(lines)
