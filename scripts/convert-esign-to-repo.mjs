import fs from "fs";
import https from "https";

const esignUrl = "https://raw.githubusercontent.com/hieuitcz/ipa/refs/heads/main/esign.json";
const outPath = "repo.json";

function fetchJson(url) {
  return new Promise((resolve, reject) => {
    https
      .get(url, res => {
        if (res.statusCode !== 200) {
          reject(new Error(`HTTP ${res.statusCode} for ${url}`));
          return;
        }
        let data = "";
        res.on("data", chunk => (data += chunk));
        res.on("end", () => {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            reject(e);
          }
        });
      })
      .on("error", reject);
  });
}

const main = async () => {
  const esign = await fetchJson(esignUrl);

  const repo = {
    name: "hieuitcz IPA Repo",
    subtitle: "All my IPAs in one place",
    description: "AltStore-style repository for modified and premium iOS apps from hieuitcz.",
    iconURL: "https://raw.githubusercontent.com/hieuitcz/ipa/refs/heads/main/icons/ipa-repo.png",
    headerURL: "https://raw.githubusercontent.com/hieuitcz/ipa/refs/heads/main/icons/header.png",
    website: "https://github.com/hieuitcz/ipa",
    tintColor: "#FF6B35",
    featuredApps: [],
    apps: (esign.apps || []).map(app => ({
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
  console.log(`Generated ${outPath} from ${esignUrl}`);
};

main().catch(err => {
  console.error(err);
  process.exit(1);
});
