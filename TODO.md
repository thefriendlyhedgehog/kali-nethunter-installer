## TO-DO

- `./build.py`: If `resolution` is set in `./kernels/devices.yml`, only copy those wallpapers when generating nethunter ZIP
- `./build.py`: When downloading Kali chroot/rootfs, add SHA512 retrieval function
- Sync external scripts with their upstream
  - https://github.com/Magisk-Modules-Alt-Repo/magic-flash
  - https://github.com/jcadduono/lazyflasher
  - https://github.com/osm0sis/AnyKernel3/
- Improve `--uninstall`
  - Remove our Bootanimation & restore defaults
  - Remove our wallpaper & restore defaults
  - Add Magisk support (https://github.com/topjohnwu/Magisk/blob/master/scripts/update_binary.sh // https://github.com/topjohnwu/Magisk/blob/master/scripts/uninstaller.sh)
- Create Magisk JSON
  - https://topjohnwu.github.io/Magisk/guides.html
  - `updateJson=https://gitlab.com/kalilinux/nethunter/build-scripts/kali-nethunter-installer/-/raw/main/magisk.json`
