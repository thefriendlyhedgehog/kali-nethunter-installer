#!/bin/bash
RELEASE="2020.1"
OUT_DIR="/media/re4son/dev/Nethunter/${RELEASE}/images/"

# NetHunter Light:
# ------------------
python build.py -g arm64 -fs full -r ${RELEASE} && mv *.zip ${OUT_DIR}
python build.py -g armhf -fs full -r ${RELEASE} && mv *.zip ${OUT_DIR}

# Gemini PDA Nougat:
# ------------------
python build.py -d gemini4g_p1 -n -fs full -r ${RELEASE} && mv *.zip ${OUT_DIR}

# Galaxy Tab S4 LTE Oreo:
# -------------------------
python build.py -d gts4llte -o -fs full -r ${RELEASE} && mv *.zip ${OUT_DIR}

# Galaxy Tab S4 4WiFi Oreo:
# -------------------------
python build.py -d gts4lwifi -o -fs full -r ${RELEASE} && mv *.zip ${OUT_DIR}

# LG H990DS Nougat:
# ------------------
python build.py -d h990 -n -fs full -r ${RELEASE} && mv *.zip ${OUT_DIR}

# Nexus 5 Marshmallow:
# --------------------
python build.py -d hammerhead -m -fs full -r ${RELEASE} && mv *.zip ${OUT_DIR}

# Nexus 5X Oreo:
# --------------------
python build.py -d bullhead -o -fs full -r ${RELEASE} && mv *.zip ${OUT_DIR}

# Nexus 6 Nougat:
# ----------------
python build.py -d shamu -n -fs full -r ${RELEASE} && mv *.zip ${OUT_DIR}

# Nexus 6 LOS 16:
# ----------------
python build.py -d shamucm -p -fs full -r ${RELEASE} && mv *.zip ${OUT_DIR}

# Nexus 6P Nougat:
# ----------------
python build.py -d angler -n -fs full -r ${RELEASE} && mv *.zip ${OUT_DIR}

# Nexus 7 Marshmallow:
# ----------------
python build.py -d flo -m -fs full -r ${RELEASE} && mv *.zip ${OUT_DIR}

# Nexus 7 CM 13.1:
# ----------------
python build.py -d flocm -m -fs full -r ${RELEASE} && mv *.zip ${OUT_DIR}

# Nexus 9 Flounder:
# ----------------
python build.py -d flounder -n -fs full -r ${RELEASE} && mv *.zip ${OUT_DIR}

# Nexus 10 Lollipop:
# ----------------
python build.py -d manta -l -fs full -r ${RELEASE} && mv *.zip ${OUT_DIR}

# Oneplus 1 CM 13:
# -----------------
python build.py -d oneplus1 -m -fs full -r ${RELEASE} && mv *.zip ${OUT_DIR}

# Oneplus 2 CM 14:
# -----------------
python build.py -d oneplus2cm -n -fs full -r ${RELEASE} && mv *.zip ${OUT_DIR} 

# Oneplus 2 LOS 15:
# -----------------
python build.py -d oneplus2cm -o -fs full -r ${RELEASE} && mv *.zip ${OUT_DIR}

# Oneplus 2 LOS 16:
# -----------------
python build.py -d oneplus2cm -p -fs full -r ${RELEASE} && mv *.zip ${OUT_DIR}

# Oneplus 7 OOS 9:
# -----------------
python build.py -d oneplus7-oos -p -fs full -r ${RELEASE} && mv *.zip ${OUT_DIR}

# Oneplus 7 OOS 10:
# -----------------
python build.py -d oneplus7-oos -q -fs full -r ${RELEASE} && mv *.zip ${OUT_DIR}

# Samsung Galaxy S6 Edge LOS 14.1:
# ---------------------------------
python build.py -d zerolte -n -fs full -r ${RELEASE} && mv *.zip ${OUT_DIR}

# XPeria Z1 Marshmallow:
# ----------------------
python build.py -d honami -m -fs full -r ${RELEASE} && mv *.zip ${OUT_DIR}

# ZTE Axon 7 Marshmallow:
-----------------------
python build.py -d ailsa_ii -m -fs full -r ${RELEASE} && mv *.zip ${OUT_DIR}

cd ${OUT_DIR} 
for f in `dir *-${RELEASE}.zip`; do sha256sum ${f} > ${f}.sha256; done
cd -
