## [Recovery/TWRP] [nethunter] [This is sourced, not a standalone script]
## Check for previous install of Kali apps & chroot/rootfs

ARCH_TMP=armhf # HACK: Old installations only exist as armhf anyways
NH=/data/local/kali-$ARCH_TMP
NHAPP=/data/data/com.offsec.nethunter/files/chroot/kali-$ARCH_TMP
NHSYS=/data/local/nhsystem/kali-$ARCH_TMP

## Fix for TWRP chasing symbolic links (mentioned by triryland)
rm -rf "$NHSYS/dev/"* "$NHAPP/dev/"* "$NH/dev/"*

## We probably don't want two old chroots in the same folder, so pick newer location in /data/local first
if [ -d "$NH" ]; then
  print "- Detected outdated previous install of Kali $ARCH_TMP, moving chroot"
  mv "$NH" "$NHSYS"
elif [ -d "$NHAPP" ]; then
  print "- Detected outdated previous install of Kali $ARCH_TMP, moving chroot"
  mv "$NHAPP" "$NHSYS"
fi

## Just to be safe lets remove old version of NetHunter app
rm -rf /data/data/com.offsec.nethunter
rm -rf /data/app/com.offsec.nethunter
rm -f  /data/app/NetHunter.apk
rm -f  /data/app/nethunter.apk
rm -rf /system/app/NetHunter

sleep 3
