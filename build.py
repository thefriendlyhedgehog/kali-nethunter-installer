#!/usr/bin/env python3

###############################################################
## Script to build/compile/merge Kali NetHunter installer per device model's kernel id
##
## Usage:
##   $ ./$0 -i <input file> -o <output directory> -r <release>
##
## E.g.:
##   $ ./build.py -d hammerhead --marshmallow --rootfs full --release 2024.3
##
## Dependencies:
##   $ sudo apt -y install python3 python3-requests python3-yaml
##   OR
##   $ python3 -m venv .env; source .env/bin/activate; python3 -m pip install requests pyyaml

from __future__ import print_function
import argparse
import datetime
import fnmatch
import hashlib
import os
import re
import requests # $ python3 -m venv .env; source .env/bin/activate; python3 -m pip install requests
import shutil
import sys
import yaml # $ python3 -m venv .env; source .env/bin/activate; python3 -m pip install pyyaml
import zipfile

android = ""
tmp_path = "tmp_out"

dl_headers = {
    "User-Agent": "Kali NetHunter Installer",
    "Accept-Encoding": "identity",
}

dl_supersu = {
    "beta": [
        "https://download.chainfire.eu/supersu-beta",
        False,
    ],
    "stable": [
        "https://download.chainfire.eu/1220/SuperSU/SR5-SuperSU-v2.82-SR5-20171001224502.zip",
        "62ee48420cacedee53b89503aa43b5449d07946fe7174ee03fc118c23f65ea988a94e5ba76dff5afd61c19fe9b23260c4cee8e293839babdf1b263ffaabb92f3",
    ],
}

# Install updated apps from the staging site (staging.nethunter.com) so that we can prepare images before we go live with releases
dl_apps = {
    # com.offsec.nethunter.store_2019030200.apk
    "NetHunterStore": [
        "https://store.nethunter.com/NetHunterStore.apk",
        "35fed79b55463f64c6b11d19df2ecb4ff099ef1dda1063b87eedaae3ebde32c3720e61cad2da73a46492d19180306adcf5f72d511da817712e1eed32068ec1ef",
    ],

    # com.offsec.nethunter.store.privileged_2110.apk
    "NetHunterStorePrivilegedExtension": [
        "https://store.nethunter.com/NetHunterStorePrivilegedExtension.apk",
        "668871f6e3cc03070db4b75a21eb0c208e88b609644bbc1408778217ed716478451ceb487d36bc1d131fa53b1b50c615357b150095c8fb7397db4b8c3e24267a",
    ],

    # com.offsec.nethunter_2024020400.apk
    # Alt: "https://store.nethunter.com/NetHunter.apk"
    "NetHunter": [
        "https://staging.nethunter.com/repo/com.offsec.nethunter_2024020400.apk",
        "199ea57119240f3e594020391983d0bec076a039863dc106d34f218eb5f20c02348c48fb6d03c9136e7b0a7313ec1ee8a9c42f4c86ac4627daaa4b92438895d7",
    ],

    # com.offsec.nhterm_2023040100.apk
    "NetHunterTerminal": [
        "https://store.nethunter.com/NetHunterTerminal.apk",
        "3e5524119e55d1217169d368113bc42763f654a8dc69175b6339f93a4f587c335b2a2252d9285d7ebfe3fcc11d5f41fe7a4caf3d1f82d0306d347519340a89a9",
    ],

    # com.offsec.nethunter.kex_11525001.apk
    "NetHunterKeX": [
        "https://store.nethunter.com/NetHunterKeX.apk",
        "f3e705532d0aa1372c8d19bdece6a1d82fbe6b1845ee6992c984dbe154fdc811230ddb0193a5c42c74926b54a6e0e689ecc3afc5ac5b93780ee0cc67d93a8dc9",
    ],
}


def copytree(src, dst):
    print("[i] Copying: %s -> %s" % (src, dst))

    def shouldcopy(f):
        global IgnoredFiles
        for pattern in IgnoredFiles:
            if fnmatch.fnmatch(f, pattern):
                return
        return True

    for sdir, subdirs, files in os.walk(src):
        for d in subdirs[:]:
            if not shouldcopy(d):
                subdirs.remove(d)
        ddir = sdir.replace(src, dst, 1)
        if not os.path.exists(ddir):
            os.makedirs(ddir)
            shutil.copystat(sdir, ddir)
        for f in files:
            if shouldcopy(f):
                sfile = os.path.join(sdir, f)
                dfile = os.path.join(ddir, f)
                if os.path.exists(dfile):
                    os.remove(dfile)
                shutil.copy2(sfile, ddir)


def download(url, file_name, verify_sha):
    try:
        u = requests.get(url, stream=True, headers=dl_headers)
        u.raise_for_status()
    except requests.exceptions.RequestException as e:
        abort(str(e))

    download_ok = False

    if u.headers.get("Content-Length"):
        file_size = int(u.headers["Content-Length"])
        print("[i] Downloading: %s (%s bytes) - %s" % (os.path.basename(file_name), file_size, url))
    else:
        file_size = 0
        print("[i] Downloading: %s (unknown size) - %s" % (os.path.basename(file_name), url))

    sha = hashlib.sha512()
    f = open(file_name, "wb")
    try:
        dl_bytes = 0
        for chunk in u.iter_content(chunk_size=8192):
            if not chunk:
                continue  # Ignore empty chunks
            f.write(chunk)
            sha.update(chunk)
            dl_bytes += len(chunk)
            if file_size:
                status = r"%10d  [%3.2f%%]" % (dl_bytes, dl_bytes * 100.0 / file_size)
            else:
                status = r"%10d" % dl_bytes

            status = status + chr(8) * (len(status) + 1)
            print(status + "\r", end="")
        download_ok = True
    except requests.exceptions.RequestException as e:
        print()
        print("[-] Error: " + str(e), file=sys.stderr)
    except KeyboardInterrupt:
        print()
        print("[-] Download cancelled", file=sys.stderr)

    f.flush()
    os.fsync(f.fileno())
    f.close()

    if download_ok:
        sha = sha.hexdigest()
        print("[i]   SHA512: " + sha)
        if verify_sha:
            print("[i]   Expect: " + verify_sha)
            if sha == verify_sha:
                print("[+]   Hash matches: OK")
            else:
                download_ok = False
                print("[-]   Hash mismatch! " + file_name, file=sys.stderr)
        else:
            print("[-]   Warning: No SHA512 hash specified for verification!", file=sys.stderr)

    if download_ok:
        print("[+]   Download OK: {}".format(file_name))
    else:
        # We should delete partially downloaded file so the next try doesn't skip it!
        if os.path.isfile(file_name):
            os.remove(file_name)
        # Better debug what file cannot be downloaded
        abort('There was a problem downloading the file: ' + file_name)


def download_supersu(beta):
    global dl_supersu
    global args

    def getdlpage(url):
        try:
            u = requests.head(url, headers=dl_headers)
            return u.url
        except requests.exceptions.ConnectionError as e:
            print("[-] Connection error: " + str(e), file=sys.stderr)
        except requests.exceptions.RequestException as e:
            print("[-] Error: " + str(e), file=sys.stderr)

    suzip_path = os.path.join("data", "supersu")
    if not os.path.exists(suzip_path):
        os.makedirs(suzip_path)
    suzip_file = os.path.join(suzip_path, "supersu.zip")

    # Remove previous supersu.zip if force re-downloading
    if args.force_download:
        print("[i] Force re-downloading SuperSU")
        if os.path.isfile(suzip_file):
            print("[i] Deleting: " + suzip_file)
            os.remove(suzip_file)

    if os.path.isfile(suzip_file):
        print("[i] Found SuperSU: " + suzip_file)
    else:
        if beta:
            surl = getdlpage(dl_supersu["beta"][0])
        else:
            surl = getdlpage(dl_supersu["stable"][0])

        if surl:
            if beta:
                download(surl + "?retrieve_file=1", suzip_file, dl_supersu["beta"][1])
            else:
                download(surl + "?retrieve_file=1", suzip_file, dl_supersu["stable"][1])
        else:
            abort('Could not retrieve download URL for SuperSU')

    print("[+] Finished setting up SuperSU")


def download_nethunter_apps():
    global dl_apps
    global args

    app_path = os.path.join("data", "apps")
    if not os.path.exists(app_path):
        os.makedirs(app_path)

    if args.force_download:
        print("[i] Force re-downloading all NetHunter apps")
    else:
        print("[i] Downloading all NetHunter apps")

    for key, value in dl_apps.items():
        apk_name = key + ".apk"
        apk_path = os.path.join(app_path, apk_name)
        apk_url = value[0]
        apk_hash = value[1] if len(value) == 2 else False

        # For force re-download, remove previous APK
        if os.path.isfile(apk_path):
            if args.force_download:
                print("[i] Deleting: " + apk_path)
                os.remove(apk_path)

        # Only download apk if we don't have it already
        if os.path.isfile(apk_path):
            print("[+] Found %s: %s" % (apk_name, apk_path))
        else:
            download(apk_url, apk_path, apk_hash)

    print("[+] Finished downloading NetHunter all apps")


def download_rootfs(fs_size):
    global arch
    global args

    fs_arch = arch
    fs_host = "https://kali.download/nethunter-images/current/rootfs/"
    fs_file = "kali-nethunter-rootfs-{}-{}.tar.xz".format(fs_size, fs_arch)
    fs_url = fs_host + fs_file

    fs_path = os.path.join("data", "rootfs")
    if not os.path.exists(fs_path):
        os.makedirs(fs_path)
    fs_localpath = os.path.join(fs_path, "kalifs-{}-{}.tar.xz".format(fs_size, fs_arch))

    if args.force_download:
        # For force re-download, remove previous rootfs
        print("[i] Force re-downloading Kali %s %s rootfs" % (fs_arch, fs_size))
        if os.path.isfile(fs_localpath):
            print("[i] Deleting: " + fs_localpath)
            os.remove(fs_localpath)
    else:
        print("[i] Downloading Kali rootfs")

    # Only download Kali rootfs if we don't have it already
    if os.path.isfile(fs_localpath):
        print("[+] Found local Kali %s %s rootfs: %s" % (fs_arch, fs_size, fs_localpath))
    else:
        print("[i] Downloading Kali %s %s rootfs (last-snapshot)" % (fs_arch, fs_size))
        download(fs_url, fs_localpath, False)  # TODO: We should add SHA512 retrieval function

    print("[+] Finished downloading Kali rootfs")


def zip_rootfs(fs_size, dst):
    global arch

    print("[i] Adding Kali rootfs archive to the installer zip")

    try:
        fs_arch = arch
        fs_file = "kalifs-{}-{}.tar.xz".format(fs_size, fs_arch)
        fs_localpath = os.path.join("data", "rootfs", fs_file)

        zf = zipfile.ZipFile(dst, "a", zipfile.ZIP_DEFLATED)
        zf.write(os.path.abspath(fs_localpath), fs_file)
        print("[+]   Added: " + fs_file)
        zf.close()
    except IOError as e:
        print("[-] IOError = " + e.reason, file=sys.stderr)
        abort('Unable to add to the zip file')

    print("[+] Finished adding rootfs")


def zip(src, dst):
    print("[i] Creating ZIP file: " + dst)

    try:
        zf = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
        abs_src = os.path.abspath(src)
        for dirname, subdirs, files in os.walk(src):
            for filename in files:
                absname = os.path.abspath(os.path.join(dirname, filename))
                arcname = absname[len(abs_src) + 1 :]
                zf.write(absname, arcname)
                print("[+]   Added: " + arcname)
        zf.close()
    except IOError as e:
        print("[-] IOError = " + e.reason, file=sys.stderr)
        abort('Unable to create the ZIP file')

    print("[+] Finished creating zip")


def read_key(key, default=""):
    global YAML
    global kernel

    try:
        # As 'author' is now in versions, need to go a little deeper
        if key not in YAML:
            for version in YAML.get('versions', default):
                if android == version.get('android', default):
                    return version.get(key, default).replace('"', "")
        return YAML.get(key, default)
    except:
        return default


def update_config(file_name, values, pure=False):
    print("[+] Updating: " + file_name)

    # Open file as read only and copy to string
    file_handle = open(file_name, "r")
    file_string = file_handle.read()
    file_handle.close()

    # Replace values of variables
    for key, value in values.items():
        # Quote value if not already quoted
        if value and not (
            value[0] == value[-1] and (value[0] == '"' or value[0] == "'")
        ):
            if pure:
                value = "%s" % value
            else:
                value = '"%s"' % value

        file_string = re.sub(
            "^" + re.escape(key) + "=.*$", key + "=" + value, file_string, flags=re.M
        )

    # Open file as writable and save the updated values
    file_handle = open(file_name, "w")
    file_handle.write(file_string)
    file_handle.close()


def setup_common(out_path=""):
    global tmp_path

    print("[i] Setting up common files")

    if not out_path:
        out_path = os.path.join(tmp_path, "boot-patcher")

    # Blindly copy directories (thats not in IgnoredFiles)
    print("[i] Common: Copying common files")
    copytree("common", out_path)

    print("[i] Common: Copying %s arch specific common files" % arch)
    copytree(os.path.join("common", "arch", arch), out_path)

    print("[+] Finished setting up common files")


def setup_installer():
    global YAML
    global kernel
    global android
    global flasher
    global args
    global tmp_path

    setup_common()

    print("[i] Setting up kernel installer (boot-patcher)")

    out_path = os.path.join(tmp_path, "boot-patcher")

    print("[i] Installer: Copying boot-patcher files")
    copytree("boot-patcher", out_path)

    print("[i] Installer: Copying %s arch specific boot-patcher files" % arch)
    copytree(os.path.join("boot-patcher", "arch", arch), out_path)

    if kernel == "generic":
        # Set up variables in the kernel installer script
        print("[i] Installer: Configuring installer script for generic %s kernel" % arch)
        update_config(
            os.path.join(
                out_path, "META-INF", "com", "google", "android", "update-binary"
            ),
            {"generic": arch},
        )
        # There's nothing left to configure
        print("[+] Finished setting up 'generic' kernel installer (boot-patcher)")
        return

    print("[i] Installer: Configuring installer script for " + kernel)

    if flasher == "anykernel":
        # Replace LazyFlasher with AnyKernel3
        x = "update-binary-anykernel_only" if not args.no_installer else "update-binary-anykernel"
        print("[i] Replacing LazyFlasher with AnyKernel3: " + x)
        shutil.move(
            os.path.join(
                out_path,
                "META-INF",
                "com",
                "google",
                "android",
                x,
            ),
            os.path.join(
                out_path, "META-INF", "com", "google", "android", "update-binary"
            ),
        )

        # Set up variables in the AnyKernel3 script
        update_config(
            os.path.join(out_path, "anykernel.sh"),
            {
                "kernel.string": kernelstring,
                "do.modules": modules,
                "block": block + ";",
                "is_slot_device": slot_device + ";",
                "ramdisk_compression": ramdisk + ";",
            },
            True,
        )

        i = 1
        for devicename in devicenames.split(","):
            print('[i] AnyKernel3 devicename: ' + devicename)
            key = "device.name" + str(i)
            update_config(os.path.join(out_path, "anykernel.sh"), {key: devicename}, True)
            i += 1

        update_config(
            os.path.join(out_path, "banner"),
            {
                "   Kernel": kernelstring,
                "   Version": version,
                "   Author": author,
            },
            True,
        )
    else:
        # Set up variables in the kernel installer script
        update_config(
            os.path.join(
                out_path, "META-INF", "com", "google", "android", "update-binary"
            ),
            {
                "kernel_string": kernelstring,
                "kernel_author": author,
                "kernel_version": version,
                "device_names": devicenames,
            },
        )

        # Set up variables in boot-patcher.sh
        print("[i] Installer: Configuring LazyFlasher's boot-patcher.sh script for " + kernel)
        update_config(
            os.path.join(out_path, "boot-patcher.sh"),
            {
                "boot_block": block,
                "ramdisk_compression": ramdisk,
            },
        )

    scan_kernel_image()

    device_path = os.path.join("kernels", android, kernel)

    # Copy kernel image from version/device to boot-patcher folder
    kernel_images = [
        "zImage",
        "zImage-dtb",
        "Image",
        "Image-dtb",
        "Image.gz",
        "Image.gz-dtb",
        "Image.lz4",
        "Image.lz4-dtb",
        "Image.fit",
    ]
    kernel_found = False
    for kernel_image in kernel_images:
        kernel_location = os.path.join(device_path, kernel_image)
        if os.path.exists(kernel_location):
            arm_arch = "ARMv7" if kernel_image[:1] == 'z' else "ARMv8"
            print("[+] Found {} kernel image: {}".format(arm_arch, kernel_location))
            shutil.copy(kernel_location, os.path.join(out_path, kernel_image))
            kernel_found = True
            break
    if not kernel_found:
        abort('Unable to find {} kernel image: {}'.format(android, device_path))

    # Copy dtb.img if it exists
    dtb_location = os.path.join(device_path, "dtb.img")
    if os.path.exists(dtb_location):
        print("[+] Found DTB image: " + dtb_location)
        shutil.copy(dtb_location, os.path.join(out_path, "dtb.img"))

    # Copy dtb if it exists
    dtb_location = os.path.join(device_path, "dtb")
    if os.path.exists(dtb_location):
        print("[+] Found DTB file: " + dtb_location)
        shutil.copy(dtb_location, os.path.join(out_path, "dtb"))

    # Copy dtbo.img if it exists
    dtbo_location = os.path.join(device_path, "dtbo.img")
    if os.path.exists(dtbo_location):
        print("[+] Found DTBO image: " + dtbo_location)
        shutil.copy(dtbo_location, os.path.join(out_path, "dtbo.img"))

    # Copy any patch.d scripts
    patchd_path = os.path.join(device_path, "patch.d")
    if os.path.exists(patchd_path):
        print("[+] Found additional patch.d scripts: " + patchd_path)
        copytree(patchd_path, os.path.join(out_path, "patch.d"))

    # Copy any ramdisk files
    ramdisk_path = os.path.join(device_path, "ramdisk")
    if os.path.exists(ramdisk_path):
        print("[+] Found additional ramdisk files: " + ramdisk_path)
        copytree(ramdisk_path, os.path.join(out_path, "ramdisk-patch"))

    # Copy any modules
    modules_path = os.path.join(device_path, "modules")
    if os.path.exists(modules_path):
        print("[+] Found additional kernel modules: " + modules_path)
        copytree(modules_path, os.path.join(out_path, "modules"))

    # Copy any device specific system binaries, libs, or init.d scripts
    system_path = os.path.join(device_path, "system")
    if os.path.exists(system_path):
        print("[+] Found additional /system files: " + system_path)
        copytree(system_path, os.path.join(out_path, "system"))

    # Copy any /data/local folder files
    local_path = os.path.join(device_path, "local")
    if os.path.exists(local_path):
        print("[+] Found additional /data/local files: " + local_path)
        copytree(local_path, os.path.join(out_path, "data", "local"))

    # Copy any AnyKernel3 additions
    ak_patches_path = os.path.join(device_path, "ak_patches")
    if os.path.exists(ak_patches_path):
        print("[+] Found additional AnyKernel3 patches: " + ak_patches_path)
        copytree(ak_patches_path, os.path.join(out_path, "ak_patches"))

    print("[+] Finished setting up kernel installer (boot-patcher)")


def setup_nethunter():
    global arch
    global resolution

    setup_common(tmp_path)

    print("[+] Setting up NetHunter")

    print("[i] NetHunter: Copying files")
    copytree("nethunter", tmp_path)

    print("[i] NetHunter: Copying %s arch specific files" % arch)
    copytree(os.path.join("nethunter", "arch", arch), tmp_path)

    print("[i] NetHunter: Copying kernel zip")
    copytree("kernel", tmp_path)

    # Set up variables in update-binary script
    print("[i] NetHunter: Configuring installer script for " + kernel)
    update_config(
        os.path.join(tmp_path, "META-INF", "com", "google", "android", "update-binary"),
        {"supersu": supersu},
    )

    # Overwrite screen resolution if defined in ./kernels/devices.yml
    if resolution:
        file_name = os.path.join(tmp_path, "wallpaper", "resolution.txt")
        file_handle = open(file_name, "w")
        file_handle.write(resolution)
        file_handle.close()

    # Device model specific (pre zip)
    # Change bootanimation folder for product partition devices
    if kernel.find("oneplus8") == 0:
        shutil.copytree(
            os.path.join(tmp_path, "system", "media"),
            os.path.join(tmp_path, "product", "media"),
            dirs_exist_ok=True,
        )
        shutil.rmtree(os.path.join(tmp_path, "system", "media"))

    print("[+] Finished setting up NetHunter")


def cleanup(domsg=False):
    if os.path.exists(tmp_path):
        if domsg:
            print("[i] Removing temporary build directory: " + tmp_path)
        shutil.rmtree(tmp_path)


def done():
    cleanup()
    exit(0)


def abort(err):
    print("[-] Error: " + err, file=sys.stderr)
    cleanup(True)
    exit(1)


def scan_kernel_image():
    global android
    android_suggestion = ""
    i = 0

    print("[+] Searching for kernel: " + kernel)
    subdirectories = [ x.path for x in os.scandir("kernels") if x.is_dir() and not x.path.startswith('{}.'.format("kernels/"))]
    # Remove non Android version directories
    subdirectories.remove('{}bin'.format("kernels/"))
    subdirectories.remove('{}example_scripts'.format("kernels/"))
    subdirectories.remove('{}patches'.format("kernels/"))

    for android_version_dir in subdirectories:
        android_version_dir = android_version_dir.lower()
        android_version_dir = android_version_dir.replace("kernels/", "")
        scan_path = os.path.join("kernels", android_version_dir, kernel)
        if os.path.exists(scan_path):
            print("[+]   Found matching Android version kernel image: " + scan_path)
            i += 1
            android_suggestion = android_version_dir
    if not android and android_suggestion and i == 1:
        return android_suggestion


def read_file(file):
    try:
        print('[i] Reading: {}'.format(file))
        with open(file) as f:
            data = f.read()
            f.close()
    except Exception as e:
        print("[-] Cannot open input file: {} - {}".format(file, e), file=sys.stderr)
        sys.exit(1)
    return data


def yaml_parse(data):
    result = ""
    lines = data.split('\n')
    for line in lines:
        if not line.startswith('#'):
            # yaml doesn't like tabs so let's replace them with four spaces
            result += "{}\n".format(line.replace('\t', '    '))
    return yaml.safe_load(result)


def main():
    global YAML
    global IgnoredFiles
    global args
    global devices_yml
    global kernel
    global arch
    global android
    global kernelstring
    global flasher
    global resolution
    global devicenames
    global ramdisk
    global block
    global version
    global modules
    global slot_device
    global author
    global supersu

    supersu_beta = False
    IgnoredFiles = ["arch", "placeholder", ".DS_Store", ".git*", ".idea", "README.md"]
    devices_yml = os.path.join("kernels", "devices.yml")
    t = datetime.datetime.now()
    TimeStamp = "%04d%02d%02d_%02d%02d%02d" % (
        t.year,
        t.month,
        t.day,
        t.hour,
        t.minute,
        t.second,
    )

    # Remove any existing builds that might be left
    cleanup(True)

    # Read devices.yml, get device names
    if not os.path.exists(devices_yml):
        abort('Could not find %s! Maybe you need to run ./bootstrap.sh?' % devices_yml)

    data = read_file(devices_yml)
    yml = yaml_parse(data)

    default = ""
    kernels = []
    for element in yml:
        for device_model in element.keys():
            for kernel in element[device_model].get('kernels', default):
                kernels.append(kernel.get('id', default))

    help_device = "Allowed kernel IDs: \n"
    for kernel in kernels:
        help_device += "    %s\n" % kernel

    parser = argparse.ArgumentParser(
        description="Kali NetHunter recovery flashable zip builder"
    )
    parser.add_argument(
        "--generic",
        "-g",
        action="store",
        metavar="ARCH",
        help="Build a generic installer (modify ramdisk only)",
    )
    parser.add_argument("--kernel", "-k", action="store", help=help_device)
    parser.add_argument("--kitkat", "-4", action="store_true", help="Android 4.4")
    parser.add_argument("--lollipop", "-5", action="store_true", help="Android 5")
    parser.add_argument("--marshmallow", "-6", action="store_true", help="Android 6")
    parser.add_argument("--nougat", "-7", action="store_true", help="Android 7")
    parser.add_argument("--oreo", "-8", action="store_true", help="Android 8")
    parser.add_argument("--pie", "-9", action="store_true", help="Android 9")
    parser.add_argument("--ten", "-10", action="store_true", help="Android 10")
    parser.add_argument("--eleven", "-11", action="store_true", help="Android 11")
    parser.add_argument("--twelve", "-12", action="store_true", help="Android 12")
    parser.add_argument("--thirteen", "-13", action="store_true", help="Android 13")
    parser.add_argument("--fourteen", "-14", action="store_true", help="Android 14")
    parser.add_argument("--fifteen", "-15", action="store_true", help="Android 15")
    parser.add_argument("--wearos", "-w", action="store_true", help="Wear OS")
    parser.add_argument(
        "--rootfs",
        "-fs",
        action="store",
        metavar="SIZE",
        help="Build with Kali rootfs (full, minimal or nano)",
    )
    parser.add_argument(
        "--force-download", "-f", action="store_true", help="Force re-downloading external resources"
    )
    parser.add_argument(
        "--uninstaller", "-u", action="store_true", help="Create an uninstaller"
    )
    parser.add_argument(
        "--installer", "-i", action="store_true", help="Build only the kernel installer (boot-patcher)"
    )
    parser.add_argument(
        "--no-installer",
        action="store_true",
        help="Build without the kernel installer (boot-patcher)",
    )
    parser.add_argument(
        "--no-branding",
        action="store_true",
        help="Build without wallpaper or boot animation",
    )
    parser.add_argument(
        "--no-freespace-check",
        action="store_true",
        help="Build without free space check",
    )
    parser.add_argument(
        "--supersu",
        "-su",
        action="store_true",
        help="Build with SuperSU installer included",
    )
    parser.add_argument(
        "--release",
        "-r",
        action="store",
        metavar="VERSION",
        help="Specify NetHunter release version",
    )

    args = parser.parse_args()

    if args.installer and args.no_installer:
        abort(
            "You seem to be having trouble deciding whether you want the kernel installer or not: --installer // --no-installer"
        )
    if args.kernel and args.generic:
        abort('The device and generic switches are mutually exclusive: --device // --generic')

    if args.kernel:
        if args.kernel in kernels:
            for element in yml:
                for device_model in element.keys():
                    for k in element[device_model].get('kernels', default):
                        if args.kernel == k.get('id', default):
                            YAML = k
                            kernel = args.kernel
        else:
            abort('kernel %s not found in %s' % (args.kernel, devices_yml))
    elif args.generic:
        arch = args.generic
        kernel = "generic"
    elif args.force_download:
        # Not sure how many people would use this ($0 --force-download)
        print('[i] Only downloading external resources (Caching, not building)')
        download_nethunter_apps()
        if args.supersu:
            download_supersu(supersu_beta)
        if args.rootfs:
            download_rootfs(args.rootfs)
        done()
    elif not args.uninstaller:
        abort('No valid arguments supplied. Try -h or --help')

    # If we found a device, set architecture and parse android OS release
    if args.kernel:
        i = 0
        if args.kitkat:
            android = "kitkat"
            i += 1
        if args.lollipop:
            android = "lollipop"
            i += 1
        if args.marshmallow:
            android = "marshmallow"
            i += 1
        if args.nougat:
            android = "nougat"
            i += 1
        if args.oreo:
            android = "oreo"
            i += 1
        if args.pie:
            android = "pie"
            i += 1
        if args.ten:
            android = "ten"
            i += 1
        if args.eleven:
            android = "eleven"
            i += 1
        if args.twelve:
            android = "twelve"
            i += 1
        if args.thirteen:
            android = "thirteen"
            i += 1
        if args.fourteen:
            android = "fourteen"
            i += 1
        if args.fifteen:
            android = "fifteen"
            i += 1
        if args.wearos:
            android = "wearos"
            i += 1
        if i == 0:
            android = scan_kernel_image()

            if android:
                print("[*] Auto selecting kernel image: " + android)
            else:
                abort(
                    "Missing Android version"
                )
        elif i > 1:
            scan_kernel_image()
            abort(
                "Select only one Android version, not " + str(i)
            )

        if args.rootfs and not (
            args.rootfs == "full" or args.rootfs == "minimal" or args.rootfs == "nano"
        ):
            abort(
                "Invalid Kali rootfs size. Available options: --rootfs full, --rootfs minimal, --rootfs nano"
            )

    #
    # Read arguments
    #

    kernelstring = read_key("kernelstring", "NetHunter kernel")
    devicenames = read_key("devicenames")
    arch = read_key("arch", "armhf")
    flasher = read_key("flasher", "LazyFlasher")
    x = 'auto' if flasher == "anykernel" else 'gzip'
    ramdisk = read_key("ramdisk", x)
    resolution = read_key("resolution")
    block = read_key("block")
    version = read_key("version", "1.0")
    supersu = read_key("supersu", "auto") # REF: See commit 922bea58931a50299e159d222285792303e69005
    modules = str(read_key("modules", "0"))
    slot_device = str(read_key("slot_device", "1"))
    author = read_key("author", "Unknown")

    #
    # Feedback
    #

    # Feedback about command line arguments
    if args.generic:
        print("[i] Generic image: true")
    if args.kernel:
        print("[i] Kernel ID: " + kernel)

    print("[i] Android version: " + android)

    if args.force_download:
        print("[i] Force downloading external resources: true")

    if args.uninstaller:
        print("[i] Create additional uninstaller: true")

    if args.installer:
        print("[i] Kernel installer only: true")
    if args.no_installer:
        print("[i] Skip kernel installer: true")

    if args.no_branding:
        print("[i] Skip branding: true")

    if args.no_freespace_check:
        print("[i] Disable freespace check: true")

    if args.supersu:
        print("[i] Include SuperSU: true")
        print("[i] SuperSU beta: " , supersu_beta)

    x = args.release if args.release else TimeStamp
    print("[i] NetHunter release version: " + x)

    x = args.rootfs if args.rootfs else '-'
    print("[i] rootfs: " + x)

    # Feedback with values from devices.yml
    print("[i] From: " + devices_yml)
    print("[i]   kernelstring: " + kernelstring)
    x = devicenames if devicenames else '-'
    x = x.split(",") if flasher == "anykernel" else x
    print("[i]   devicenames : " , x)
    print("[i]   arch        : " + arch)
    print("[i]   flasher     : " + flasher)
    print("[i]   ramdisk     : " + ramdisk)
    x = resolution if resolution else '-'
    print("[i]   resolution  : " + x)
    x = block if block else '-'
    print("[i]   block       : " + x)
    print("[i]   version     : " + version)
    x = supersu if supersu else '-'
    print("[i]   supersu     : " + x)
    if flasher == "anykernel":
        print("[i]   modules     : " + modules)
        print("[i]   slot_device : " + slot_device)
    print("[i]   author      : " + author)

    #
    # Filename output
    #

    file_tag = "nethunter"

    # Set file name tag depending on the options chosen
    if args.release:
        file_tag += "-" + args.release
    else:
        file_tag += "-" + TimeStamp

    file_tag += "-" + kernel.replace("-", "_")

    if args.kernel:
        file_tag += "-" + android
    else:
        file_tag += "-" + arch

    if args.no_branding and not args.installer:
        file_tag += "-no_branding"

    if args.installer:
        file_tag += "-installer"

    if args.no_installer:
        file_tag += "-no_installer"

    if args.uninstaller:
        file_tag += "-uninstaller"

    if args.supersu:
        file_tag += "-rooted"

    if args.rootfs:
        file_tag += "-kalifs_" + args.rootfs

    file_tag += ".zip"

    #
    # Add any other files to ignore
    #

    # Don't include wallpaper or boot animation if --no-branding is specified
    if args.no_branding:
        IgnoredFiles.append("wallpaper")
        IgnoredFiles.append("bootanimation.zip")

    # Don't include wallpaper or boot animation if --wearos is specified
    if args.wearos:
        IgnoredFiles.append("wallpaper")
        IgnoredFiles.append("bootanimation.zip")
        IgnoredFiles.append("NetHunterStorePrivilegedExtension.apk")
        IgnoredFiles.append("NetHunterStore.apk")
        if args.kernel == "ticwatchpro":
            IgnoredFiles.append("NetHunterKeX.apk")
    # Don't include wearos bootanimation by default
    else:
        IgnoredFiles.append("bootanimation_wearos.zip")

    # Don't include free space script if --no-freespace-check is specified
    if args.no_freespace_check:
        IgnoredFiles.append("freespace.sh")

    # Don't include SuperSU unless --supersu is specified
    if not args.supersu:
        IgnoredFiles.append("supersu.zip")

    #
    # Download external resources
    #

    # Download Kali rootfs if we are building a zip with the chroot environment included
    if args.rootfs:
        download_rootfs(args.rootfs)

    # We don't need the apps or SuperSU if we are only building the kernel installer
    if not args.installer:
        download_nethunter_apps()
        copytree(os.path.join("data", "apps"), os.path.join(tmp_path, "data", "app"))

        # Download SuperSU if we want it
        if args.supersu:
            download_supersu(supersu_beta)
            shutil.copy(os.path.join("data", "supersu", "supersu.zip"), os.path.join(tmp_path, "supersu.zip"))

    #
    # Do actions
    #

    # Build an uninstaller zip if --uninstaller is specified
    if args.uninstaller:
        zip("uninstaller", file_tag)

        print("[+] Created uninstaller: " + file_tag)
    # Only build a kernel installer zip and exit if --installer is specified
    if args.installer:
        setup_installer()

        zip(os.path.join(tmp_path, "boot-patcher"), file_tag)

        print("[+] Created kernel installer: " + file_tag)
    else:
        # Don't set up the kernel installer if --no-installer is specified
        if not args.no_installer:
            setup_installer()
            zip(os.path.join(tmp_path, "boot-patcher"), os.path.join(tmp_path, "nethunter-installer.zip"))

        setup_nethunter()

        zip(tmp_path, file_tag)

        #
        # Post zip creation
        #

        # Add the Kali rootfs archive if --rootfs is specified
        if args.rootfs:
            zip_rootfs(args.rootfs, file_tag)

        # Device model specific (post zip)
        # Rename bootanimation archive if --wearos is specified
        if args.wearos:
            bootanimation_rename = (
                'printf "@ system/media/bootanimation_wearos.zip\n@=system/media/bootanimation.zip\n" | zipnote -w '
                + file_tag
            )
            os.system(bootanimation_rename)

        print("[+] Created Kali NetHunter installer: " + file_tag)
    done()


if __name__ == "__main__":
    main()
