## [Recovery/TWRP] [boot-patcher & nethunter] [This is sourced, not a standalone script]
## Install NetHunter's BusyBox

print() {
  echo "${1:- }" \
    | while read -r line; do
       echo -e "ui_print $line" > "$console"
       echo -e "ui_print \n" > "$console"
    done
}

tmp=$(readlink -f "$0")
tmp=${tmp%/*/*}
. "$tmp/env.sh"

[ -f /tmp/console ] && console=$(cat /tmp/console)
[ "$console" ] || console=/proc/$$/fd/1

xbin=/system/xbin
[ -d $xbin ] || mkdir -p $xbin

cd "$tmp/tools"
for bb in busybox_nh-*; do 
  print "- Installing $bb"
  rm -f $xbin/$bb
  cp $bb $xbin/$bb
  chmod 0755 $xbin/$bb
done

cd $xbin
rm -f busybox_nh
busybox_nh=$( (/sbin/busybox_nh ls -v busybox_nh-* || ls busybox_nh-*) | tail -n 1 )
print "- Setting $busybox_nh as default"
ln -s $xbin/$busybox_nh busybox_nh
$xbin/busybox_nh --install -s $xbin

[ -e $xbin/busybox ] || {
  print "- $xbin/busybox not found! Symlinking"
  ln -s $xbin/busybox_nh $xbin/busybox
}
