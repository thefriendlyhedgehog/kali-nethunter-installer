## [Magisk & recovery/TWRP] [nethunter] [This is sourced, not a standalone script]
## Set the wallpaper based on device screen resolution

[ -d $TMP/wallpaper ] || return 1

## Define wallpaper variables
wp=/data/system/users/0/wallpaper
wpinfo=${wp}_info.xml

## If defined in https://gitlab.com/kalilinux/nethunter/build-scripts/kali-nethunter-kernels/-/blob/main/devices.yml (Manual)
if [ -f "$TMP/wallpaper/resolution.txt" ]; then
  echo "Method #1" >&2
  res=$(cat $TMP/wallpaper/resolution.txt)
fi

## Check if we grabbed resolution from devices.yml
[ -z $res ] && {
  echo "Method #2" >&2

  ## Get screen resolution using wm size
  res=$(wm size | grep "Physical size:" | cut -d' ' -f3 2>/dev/null)
}

## Check if we grabbed resolution from wm or not
[ -z $res ] && {
  echo "Method #3" >&2

  ## Try to grab the wallpaper height and width from /sys / sysfs
  res="$(cat /sys/class/drm/*/modes | head -n 1)"
}

## Check if we grabbed resolution from /sys / sysfs or not
[ -z $res ] && [ -f $TMP/tools/screenres ] && {
  echo "Method #4" >&2

  ## Try the old method for old devices
  res=$($TMP/tools/screenres)

  ([ -z "$res" ] || [[ "$res" == *"failed"* ]]) && unset res
}

## Give up...
[ -z $res ] && {
  print "! Can't get screen resolution of device! Skipping"
  return 1
}

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

print "- Found screen resolution: $res"
res_w=$(echo "$res" | cut -f1 -dx)
res_h=$(echo "$res" | cut -f2 -dx)

if [ ! -f "wallpaper/$res.png" ]; then
  print "! No wallpaper found for your screen resolution. Skipping"
  return 1
fi

[ -f "$wp" ] && [ -f "$wpinfo" ] || setup_wp=1

cat "wallpaper/$res.png" > "$wp"

echo "<?xml version='1.0' encoding='utf-8' standalone='yes' ?>" > "$wpinfo"
echo "<wp width=\"$res_w\" height=\"$res_h\" name=\"nethunter.png\" />" >> "$wpinfo"

if [ "$setup_wp" ]; then
  chown system:system "$wp" "$wpinfo"
  chmod 600 "$wp" "$wpinfo"
  chcon "u:object_r:wallpaper_file:s0" "$wp"
  chcon "u:object_r:system_data_file:s0" "$wpinfo"
fi

print "- NetHunter wallpaper applied successfully"
