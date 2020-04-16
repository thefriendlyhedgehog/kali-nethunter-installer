#!/bin/bash

RELEASE=$1
DEVICES="devices/devices.cfg"
FS_SIZE="full"
BUILD_SCRIPT="build-${RELEASE}.sh"
OUT_DIR="/media/re4son/dev/Nethunter/${RELEASE}/images/"
MANIFEST="${OUT_DIR}/${RELEASE}-manifest.csv"

function setupenv() {
	mkdir -p ${OUT_DIR}
}

function getdevicelist () {
sed -n '/^## Image/ {N; s/[\r\n\#]//g; p;}' ${DEVICES}
}

function getdeviceqty () {
	i=$(grep -c "^## Device:" $DEVICES)
	printf "$i"
}

function getimageqty () {
	i=$(grep -c "^## Image:" $DEVICES)
	printf "$i"
}

function makebuildscript() {
	## Create build script starting with a hash bang and declarations
	printf "#!/bin/bash\n\n" > ${BUILD_SCRIPT} 
	printf "RELEASE=\"${RELEASE}\"\n" >> ${BUILD_SCRIPT}
	printf "OUT_DIR=\"${OUT_DIR}\"\n" >> ${BUILD_SCRIPT}
	printf "\n" >> ${BUILD_SCRIPT}

	## Ensure the OUT_DIR exists
	printf "mkdir -p \${OUT_DIR}\n" >> ${BUILD_SCRIPT}
	printf "\n" >> ${BUILD_SCRIPT}

	## Add builds for NetHunter light
	printf "# NetHunter Light:\n" >> ${BUILD_SCRIPT}
	printf "# -----------------------------------------------\n" >> ${BUILD_SCRIPT}
	printf "python build.py -g arm64 -fs ${FS_SIZE} -r \${RELEASE} && mv *\${RELEASE}*.zip \${OUT_DIR}\n" >> ${BUILD_SCRIPT}
	printf "python build.py -g armhf -fs ${FS_SIZE} -r \${RELEASE} && mv *\${RELEASE}*.zip \${OUT_DIR}\n" >> ${BUILD_SCRIPT}
	printf "\n" >> ${BUILD_SCRIPT}

	## Add build line for official images in the devices.txt
	while IFS='"' read -r a first a second a; do
		printf "# $first:\n" >> ${BUILD_SCRIPT}
		printf "# -----------------------------------------------\n" >> ${BUILD_SCRIPT}
		printf "python build.py $second -fs ${FS_SIZE} -r \${RELEASE} && mv *\${RELEASE}*.zip \${OUT_DIR}\n" >> ${BUILD_SCRIPT}
		printf "\n" >> ${BUILD_SCRIPT}
	done <<< $devices

	## Create sha files for each image
	printf "cd \${OUT_DIR}\n" >> ${BUILD_SCRIPT} 
	printf "for f in \`dir *-\${RELEASE}-*.zip\`; do sha256sum \${f} > \${f}.sha256; done\n" >> ${BUILD_SCRIPT}
	printf "cd -\n" >> ${BUILD_SCRIPT}

	chmod +x ${BUILD_SCRIPT}
}

function makemanifest() {
	## Create manifest file to map display name to image file for download page
	rm -f $MANIFEST && touch $MANIFEST

	## Add manifest line for official images in the devices.txt
	while IFS='"' read -r a first a second a; do
		printf "$first" >> ${MANIFEST}
		printf "," >> ${MANIFEST}
		c=$(echo $second|cut -d' ' -f2) 
		v=$(echo $second|cut -d' ' -f4) 
		printf "nethunter-${RELEASE}-${c}-${v}kalifs-${FS_SIZE}.zip\n" >> ${MANIFEST}
	done <<< $devices
	tempmanifest=$(sort -k1 -n -t, ${MANIFEST})
	printf "NetHunter Lite ARM64," > ${MANIFEST}
	printf "nethunter-${RELEASE}-generic-arm64-kalifs-${FS_SIZE}.zip\n" >> ${MANIFEST}
	printf "NetHunter Lite ARMhf," >> ${MANIFEST}
	printf "nethunter-${RELEASE}-generic-armhf-kalifs-${FS_SIZE}.zip\n" >> ${MANIFEST}
	printf "${tempmanifest}" >> ${MANIFEST}
}

# Main
if [ -z $RELEASE ]; then
	printf "\n\tError: Missing argument.\n"
	printf "\tPlease provide a name for the release, e.g.:\n"
	printf "\t\t\"$0 2020.2\"\n\n"
	exit 1
fi

devices=$(getdevicelist)
devqty=$(getdeviceqty)
imgqty=$(getimageqty)

printf "\nNumber of devices:\t$devqty\n"
printf "Number of images:\t$imgqty\n\n"
printf "Images to be build for ${RELEASE}:\n\n"
printf "$devices\n"

setupenv
makebuildscript
printf "\nBuild script:\t${BUILD_SCRIPT}\n"
makemanifest
printf "Manifest:\t${MANIFEST}\n\n"
