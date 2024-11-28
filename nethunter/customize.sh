## $ adb push *nethunter*.zip /sdcard/Download/nh.zip; adb shell 'su -c magisk --install-module /sdcard/Download/nh.zip'

TMPDIR=/dev/tmp
mkdir -p $TMPDIR
cd $TMPDIR/

echo "* Unpacking nethunter script"
unzip -o "$ZIPFILE" META-INF/com/google/android/update-binary -d $TMPDIR

echo "* Running nethunter script"
[ -f $TMPDIR/META-INF/com/google/android/update-binary ] && sh $TMPDIR/META-INF/com/google/android/update-binary   # Spawn a new session (aka using sh), don't do it in the current session (able to pass variables/functions)
