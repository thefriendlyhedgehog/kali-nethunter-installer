## [Recovery/TWRP] [nethunter] [This is sourced, not a standalone script]
## Install SuperSU in the specified mode

supersu_tmp=/tmp/supersu

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

sh "$supersu_tmp/META-INF/com/google/android/update-binary" dummy 1 "$TMP/supersu.zip" || print "update-binary/supersu.zip failed"
