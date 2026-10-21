#!/bin/sh
# Downloads the app's fonts (IBM Plex Sans, IBM Plex Sans Hebrew, Frank Ruhl Libre; SIL Open Font License) into the app.
# The app works without them (it falls back to the phone's fonts), but looks best with them.
set -e
mkdir -p app/src/main/assets/fonts
cd app/src/main/assets/fonts
curl -fsSLO https://cdn.jsdelivr.net/npm/@fontsource/ibm-plex-sans-hebrew@5.3.0/files/ibm-plex-sans-hebrew-hebrew-400-normal.woff2
curl -fsSLO https://cdn.jsdelivr.net/npm/@fontsource/ibm-plex-sans-hebrew@5.3.0/files/ibm-plex-sans-hebrew-hebrew-500-normal.woff2
curl -fsSLO https://cdn.jsdelivr.net/npm/@fontsource/ibm-plex-sans-hebrew@5.3.0/files/ibm-plex-sans-hebrew-hebrew-600-normal.woff2
curl -fsSLO https://cdn.jsdelivr.net/npm/@fontsource/ibm-plex-sans@5.3.0/files/ibm-plex-sans-latin-400-normal.woff2
curl -fsSLO https://cdn.jsdelivr.net/npm/@fontsource/ibm-plex-sans@5.3.0/files/ibm-plex-sans-latin-500-normal.woff2
curl -fsSLO https://cdn.jsdelivr.net/npm/@fontsource/ibm-plex-sans@5.3.0/files/ibm-plex-sans-latin-600-normal.woff2
