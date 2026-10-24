"use strict";

const fs = require("node:fs/promises");
const path = require("node:path");
const JSZip = require("jszip");

/** Apply the local presentation theme without machine-specific dependencies. */
async function applyTheme(fileName, theme) {
  const themeXml = await fs.readFile(path.join(__dirname, "theme.xml"));
  const archive = await JSZip.loadAsync(await fs.readFile(fileName));
  const themePath = "ppt/theme/theme1.xml";
  if (!archive.file(themePath)) {
    throw new Error("The presentation is missing its primary theme.");
  }
  if (theme && !themeXml.toString("utf8").includes(`name="${theme.name}"`)) {
    throw new Error("The local theme XML does not match the requested theme.");
  }
  archive.file(themePath, themeXml);
  await fs.writeFile(fileName, await archive.generateAsync({type: "nodebuffer"}));
}

module.exports = { applyTheme };
