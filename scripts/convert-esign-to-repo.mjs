import fs from "fs";

const esignPath = "esign.json";
const outPath = "esign_repo.json";

const esign = JSON.parse(fs.readFileSync(esignPath, "utf8"));

const repo = {
  name: "hieuitcz IPA Repo",
  subtitle: "All my IPAs in one place",
  description: "AltStore-style repository for modified and premium iOS apps from hieuitcz.",
  iconURL: "https://raw.githubusercontent.com/hieuitcz/ipa/main/icons/ipa-repo.png",
  headerURL: "https://raw.githubusercontent.com/hieuitcz/ipa/main/icons/header.png",
  website: "https://github.com/hieuitcz/ipa",
  tintColor: "#FF6B35",
  featuredApps: [],
  apps: esign.apps.map(app => ({
    name: app.name,
    bundleIdentifier: app.bundleIdentifier,
    developerName: app.developerName,
    subtitle: "Modified iOS application",
    localizedDescription: app.localizedDescription || app.versionDescription || "",
    iconURL: app.iconURL,
    tintColor: "#FF6B35",
    screenshots: [],
    appPermissions: {
      entitlements: [],
      privacy: {}
    },
    versions: [
      {
        version: app.version,
        minOSVersion: "14.0",
        date: app.versionDate,
        size: app.size,
        downloadURL: app.downloadURL,
        localizedDescription: app.versionDescription || ""
      }
    ]
  }))
};

fs.writeFileSync(outPath, JSON.stringify(repo, null, 2));
console.log(`Generated ${outPath}`);
