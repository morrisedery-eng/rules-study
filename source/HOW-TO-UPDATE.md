# How this app is built and updated

- Edit the source files in this folder (course data in `days.js` and `cards.js`, screens in the `*.js` and `*_step.py` files, Hebrew niqqud in `voc/`).
- Copy `app/rulesstudy.jks` next to `build_offline.py`, then run `python3 build_offline.py`. It regenerates the Android project in `RulesStudy/`.
- Copy the generated project to the repository root and push to `main`. GitHub Actions builds `RulesStudy.apk` and `version.json` and publishes them on the Releases page (tag `latest`).
- The installed app checks `releases/latest/download/version.json` and can download and install the new APK itself.
- The app is always signed with `app/rulesstudy.jks`, so every new version installs over the old one and keeps the user's progress.
