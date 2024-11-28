#!/sbin/sh
# Move safe apps from system to data partition to free up space for installation

print() {
  echo "${1:- }" \
    | while read -r line; do
       echo -e "ui_print $line" > "$console"
       echo -e "ui_print \n" > "$console"
    done
}

get_bb() {
  cd $tmp/tools
  BB_latest=$( (ls -v busybox_nh-* 2>/dev/null || ls busybox_nh-*) | tail -n 1)
  BB=$tmp/tools/$BB_latest # Use NetHunter BusyBox from tools
  chmod 0755 $BB # Make BusyBox executable
  echo $BB
  cd - >/dev/null
}

tmp=$(readlink -f "$0")
tmp=${tmp%/*/*}
. "$tmp/env.sh"

[ -f /tmp/console ] && console=$(cat /tmp/console)
[ "$console" ] || console=/proc/$$/fd/1

# Free space we require on /system (in Megabytes)
SpaceRequired=50
SYSTEM="/system"

MoveableApps="
QuickOffice
CloudPrint2
YouTube
PlusOne
PlayGames
Drive
Music2
Maps
Magazines
Newsstand
Currents
Photos
Books
Street
Hangouts
KoreanIME
GoogleHindiIME
GooglePinyinIME
iWnnIME
Keep
FaceLock
Wallet
HoloSpiralWallpaper
BasicDreams
PhaseBeam
LiveWallpapersPicker
"

IFS="
"
MNT=/system
SA=$MNT/app
DA=/data/app
AndroidV=$(grep 'ro.build.version.release' ${SYSTEM}/build.prop | cut -d'=' -f2)

case $AndroidV in
   4) android_ver="Kitkat";;
   5) android_ver="Lolipop";;
   6) android_ver="Marshmallow";;
   7) android_ver="Nougat";;
   8) android_ver="Oreo";;
   9) android_ver="Pie";;
  10) android_ver="Q";;
  11) android_ver="R";;
esac

# TWRP's df from /sbin doesn't has -m flag so we use BusyBox instead and use df from it
BB=$(get_bb)
FreeSpace=$($BB df -m $MNT | tail -n 1 | tr -s ' ' | cut -d' ' -f4)

if [ -z $FreeSpace ]; then
  print "! Warning: Could not get free space status, continuing anyway!"
  exit 0
fi

print "- $MNT free space: $FreeSpace MB"

if [ "$FreeSpace" -gt "$SpaceRequired" ]; then
  exit 0
else
  print "- You don't have enough free space in your ${SYSTEM}"
  print "- Freeing up some space on ${SYSTEM}"

  if [ "$AndroidV" -gt "7" ]; then
    print "- Android Version: $android_ver (Android $AndroidV)"
    print "- Starting from Oreo (Android 8), we can't move apps from /system to /data"
    print "! Aborting installation"
    exit 1
  else
    for app in $MoveableApps; do
      if [ "$FreeSpace" -gt "$SpaceRequired" ]; then
        break
      fi

      if [ -d "$SA/$app/" ]; then
        if [ -d "$DA/$app/" ] || [ -f "$DA/$app.apk" ]; then
          print "--- Removing $SA/$app/ (extra)"
          rm -rf "$SA/$app/"
        else
          print "--- Moving $app/ to $DA"
          mv "$SA/$app/" "$DA/"
        fi
      fi

      if [ -f "$SA/$app.apk" ]; then
        if [ -d "$DA/$app/" ] || [ -f "$DA/$app.apk" ]; then
          print "--- Removing $SA/$app.apk (extra)"
          rm -f "$SA/$app.apk"
        else
          print "--- Moving $app.apk to $DA"
          mv "$SA/$app.apk" "$DA/"
        fi
      fi
    done

    print "- Free space (after): $FreeSpace MB"

    if [ ! "$FreeSpace" -gt "$SpaceRequired" ]; then
      print "! Unable to free up $SpaceRequired MB of space on '$MNT'!"
      exit 1
    fi
  fi
fi
