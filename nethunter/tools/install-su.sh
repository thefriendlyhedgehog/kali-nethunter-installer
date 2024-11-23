#!/sbin/sh
# Install SuperSU in the specified mode

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

console=$(cat /tmp/console)
[ "$console" ] || console=/proc/$$/fd/1

sutmp=$1
supersu=$2

if [ "$supersu" = "systemless" ]; then
  print "- Installing SuperSU in systemless mode"
  cat <<EOF > "/system/.supersu"
SYSTEMLESS=true
EOF
elif [ "$supersu" = "system" ]; then
  print "- Installing SuperSU in system mode"
  cat <<EOF > "/system/.supersu"
SYSTEMLESS=false
EOF
else
  print "- Installing SuperSU in automatic mode"
  cat <<EOF > "/system/.supersu"
SYSTEMLESS=detect
EOF
fi

sh "$sutmp/META-INF/com/google/android/update-binary" dummy 1 "$tmp/supersu.zip"
