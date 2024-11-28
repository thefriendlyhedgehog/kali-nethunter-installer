## [Recovery/TWRP] [nethunter] [This is sourced, not a standalone script]
## Install Kali chroot/rootfs

verify_fs() {
  ## Valid architecture?
  case $FS_ARCH in
    armhf|arm64|i386|amd64) ;;
    *) return 1 ;;
  esac

  ## Valid build size?
  case $FS_SIZE in
    full|minimal|nano) ;;
    *) return 1 ;;
  esac
  return 0
}

# do_install [optional zip containing kalifs chroot/rootfs]
do_install() {
  print "- Found Kali chroot to be installed: $KALIFS"

  mkdir -p "$NHSYS"

  ## HACK 1/2: Rename to kali-(arm64,armhf,amd64,i386) as NetHunter app supports searching these directory after first boot
  CHROOT="$NHSYS/kali-$NH_ARCH" # Legacy rootfs directory prior to 2020.1
  ROOTFS="$NHSYS/kalifs"  # New symlink allowing to swap chroots via NetHunter app on the fly
  PRECHROOT=$($BB find /data/local/nhsystem -type d -name  "*-*" | head -n 1)  # Generic previous chroot location

  ## Remove previous chroot
  [ -d "$PRECHROOT" ] && {
    print "- Previous chroot detected! Removing"
    rm -rf "$PRECHROOT"
    rm -f "$ROOTFS"
  }

  ## Extract new chroot
  print "- Extracting Kali rootfs (This may take up to 25 minutes)"
  if [ "$1" ]; then
    unzip -p "$1" "$KALIFS" | $BB tar -xJf - -C "$NHSYS" --exclude "kali-$FS_ARCH/dev"
  else
    $BB tar -xJf "$KALIFS" -C "$NHSYS" --exclude "kali-$FS_ARCH/dev"
  fi

  [ $? = 0 ] || {
    print "! Error: Kali $FS_ARCH $FS_SIZE chroot failed to install!"
    print "- Maybe you ran out of space on your data partition?"
    return 1
  }

# HACK 2/2: Rename to kali-(arm64,armhf,amd64,i386) based on $NH_ARCH for legacy reasons and create a link to be used by apps effective 2020.1

  [ "$NH_ARCH" != "$FS_ARCH" ] && mv "$NHSYS/kali-$FS_ARCH" "$CHROOT"
  ln -sf "$CHROOT" "$ROOTFS"

  mkdir -m 0755 "$CHROOT/dev"
  print "- Kali $FS_ARCH $FS_SIZE chroot installed successfully!"

  ## We should remove the rootfs archive to free up device memory or storage space (if not zip install)
  if [ -z "$1" ]; then
    print "- Cleaning up old chroot/rootfs ($KALIFS)"
    rm -f "$KALIFS"
  fi
}

NHSYS=/data/local/nhsystem

## Get best possible ARCH
NH_ARCH=$ARCH
for x in system system_root/system system_root; do
  if [ -e /$x/build.prop ]; then
    NH_ARCH=$(cat /$x/build.prop | $BB dos2unix | $BB sed -n "s/^ro.product.cpu.abi=//p" | head -n 1)
    break
  fi
done

case $NH_ARCH in
  arm64*) NH_ARCH=arm64 ;;
  arm*) NH_ARCH=armhf ;;
  armeabi-v7a) NH_ARCH=armhf ;;
  x86_64) NH_ARCH=amd64 ;;
  x86*) NH_ARCH=i386 ;;
  *) print "! Unknown architecture detected ($NH_ARCH). Aborting chroot installation" && return 1 ;;
esac

## Check zip for kalifs-*.tar.xz first
[ -f "$ZIPFILE" ] && {
  KALIFS=$(unzip -lqq "$ZIPFILE" | awk '$4 ~ /^kalifs-/ { print $4; exit }')

  ## If zip contains a chroot/rootfs (kalifs-*.tar.xz)
  if [ -n "$KALIFS" ]; then
    FS_SIZE=$(echo "$KALIFS" | awk -F[-.] '{print $2}')
    FS_ARCH=$(echo "$KALIFS" | awk -F[-.] '{print $3}')
    ## Return if we have installed something - winning (Quitting while we're ahead!)
    verify_fs && do_install "$ZIPFILE" && return
  fi
}

## Zip doesn't container chroot/rootfs, so going check other locations (in priority order)
for fsdir in "$TMP" "/data/local" "/sdcard" "/external_sd"; do
  ## Check for: kalifs-[size]-[arch].tar.xz
  for KALIFS in "$fsdir"/kalifs-*-*.tar.xz; do
    [ -s "$KALIFS" ] || continue
    FS_SIZE=$(basename "$KALIFS" | awk -F[-.] '{print $2}')
    FS_ARCH=$(basename "$KALIFS" | awk -F[-.] '{print $3}')
    verify_fs && do_install && return
  done

  ## Check for legacy filename: kalifs-[size].tar.xz
  for KALIFS in "$fsdir"/kalifs-*.tar.xz; do
    [ -f "$KALIFS" ] || continue
    FS_ARCH=armhf
    FS_SIZE=$(basename "$KALIFS" | awk -F[-.] '{print $2}')
    verify_fs && do_install && return
  done
done

print "- No Kali rootfs archive found. Skipping"
