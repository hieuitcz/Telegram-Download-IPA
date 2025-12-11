import fs from "fs";
import https from "https";

// Link file gốc
const esignUrl = "https://raw.githubusercontent.com/hieuitcz/ipa/refs/heads/main/esign.json";
// File đầu ra
const outPath = "sidestore.json";

// Hàm tải JSON từ URL
function fetchJson(url) {
  return new Promise((resolve, reject) => {
    https
      .get(url, (res) => {
        if (res.statusCode !== 200) {
          reject(new Error(`HTTP ${res.statusCode} for ${url}`));
          return;
        }
        let data = "";
        res.on("data", (chunk) => (data += chunk));
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
  console.log(`Fetching ${esignUrl}...`);
  const esign = await fetchJson(esignUrl);

  // Cấu trúc SideStore json
  const sideStoreRepo = {
    name: "hieuitcz IPA Repo",
    identifier: "com.hieuitcz.ipa", // Identifier tự đặt
    sourceURL: "https://raw.githubusercontent.com/hieuitcz/Telegram-Download-IPA/refs/heads/main/sidestore.json", // Link tới file này sau khi push
    apps: (esign.apps || []).map((app) => ({
      name: app.name,
      bundleIdentifier: app.bundleIdentifier,
      developerName: app.developerName || "hieuitcz",
      subtitle: "Modified iOS application", // Subtitle mặc định vì esign.json không có
      version: app.version,
      versionDate: app.versionDate,
      versionDescription: app.versionDescription || "No description provided",
      downloadURL: app.downloadURL,
      localizedDescription: app.localizedDescription || app.versionDescription || "",
      iconURL: app.iconURL,
      tintColor: (app.tintColor || "FF6B35").replace("#", ""), // SideStore thường dùng hex không có dấu #
      screenshotURLs: [], // esign.json không có ảnh screenshot
      size: app.size,
    })),
  };

  fs.writeFileSync(outPath, JSON.stringify(sideStoreRepo, null, 2));
  console.log(`Generated ${outPath} with ${sideStoreRepo.apps.length} apps.`);
};

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
