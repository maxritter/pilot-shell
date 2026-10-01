// Export the approved vector mark exactly; no generated replacement symbol.
import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import sharp from "sharp";

const publicDir = fileURLToPath(new URL("../public/", import.meta.url));
const brandDir = `${publicDir}brand/`;
const fontDir = fileURLToPath(new URL("../public/fonts/", import.meta.url));
const font = await readFile(`${fontDir}geist-latin.woff2`);
const originalMark = await readFile(`${brandDir}qualitylayer-mark.svg`, "utf8");
const paths = (originalMark.match(/<path\b[^>]*\/>/g) ?? []).join("");
if (!paths) throw new Error("The approved mark has no paths");
const style = `<style>@font-face{font-family:Geist;src:url(data:font/woff2;base64,${font.toString("base64")}) format('woff2');font-weight:100 900}:root{color:#171717}@media(prefers-color-scheme:dark){:root{color:#ededed}}</style>`;
const horizontal = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 310 88" width="310" height="88">${style}<g transform="translate(0 23) scale(.43)">${paths}</g><text x="62" y="61" font-family="Geist" font-size="44" font-weight="600" letter-spacing="-1.8" fill="currentColor">qualitylayer</text></svg>`;
const stacked = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 360" width="512" height="360">${style}<g transform="translate(155 36) scale(1.8)">${paths}</g><text x="256" y="310" text-anchor="middle" font-family="Geist" font-size="60" font-weight="600" letter-spacing="-2.4" fill="currentColor">qualitylayer</text></svg>`;
await writeFile(`${brandDir}qualitylayer-logo.svg`, horizontal);
await writeFile(`${brandDir}qualitylayer-logo-stacked.svg`, stacked);
// Register the same self-hosted font with the raster exporter before any text.
await sharp({ text: { text: "qualitylayer", font: "Geist 44", fontfile: `${fontDir}geist-latin.woff2`, dpi: 72, rgba: true } }).png().toBuffer();

function themed(source, dark) {
  return source.replace(/<style>[\s\S]*?<\/style>/g, "")
    .replaceAll("currentColor", dark ? "#ededed" : "#171717")
    .replaceAll("var(--tile)", dark ? "#0a0a0a" : "#fafafa");
}

const names = ["qualitylayer-mark", "qualitylayer-logo", "qualitylayer-logo-stacked"];
for (const name of names) {
  const svg = await readFile(`${brandDir}${name}.svg`, "utf8");
  await writeFile(`${brandDir}${name}-light.svg`, themed(svg, false));
  const width = name === "qualitylayer-mark" ? 512 : 1000;
  await sharp(Buffer.from(themed(svg, true))).resize({ width }).png().toFile(`${brandDir}${name}.png`);
  await sharp(Buffer.from(themed(svg, false))).resize({ width }).png().toFile(`${brandDir}${name}-light.png`);
}

const icon = themed(await readFile(`${brandDir}qualitylayer-icon.svg`, "utf8"), false);
for (const size of [180, 192, 512]) {
  await sharp(Buffer.from(icon)).resize(size, size).png().toFile(`${brandDir}qualitylayer-icon-${size}.png`);
}
await sharp(Buffer.from(icon)).resize(180, 180).png().toFile(`${publicDir}apple-touch-icon.png`);
await sharp(Buffer.from(icon)).resize(192, 192).png().toFile(`${publicDir}favicon.png`);
await sharp(Buffer.from(icon)).resize(512, 512).png().toFile(`${publicDir}logo.png`);

const sizes = [16, 32, 48, 64];
const images = await Promise.all(sizes.map((size) => sharp(Buffer.from(icon)).resize(size, size).png().toBuffer()));
const header = Buffer.alloc(6 + sizes.length * 16);
header.writeUInt16LE(1, 2);
header.writeUInt16LE(sizes.length, 4);
let offset = header.length;
images.forEach((image, index) => {
  const start = 6 + index * 16;
  header[start] = sizes[index];
  header[start + 1] = sizes[index];
  header.writeUInt16LE(1, start + 4);
  header.writeUInt16LE(32, start + 6);
  header.writeUInt32LE(image.length, start + 8);
  header.writeUInt32LE(offset, start + 12);
  offset += image.length;
});
const ico = Buffer.concat([header, ...images]);
await writeFile(`${brandDir}favicon.ico`, ico);
await writeFile(`${publicDir}favicon.ico`, ico);

const wordmark = themed(await readFile(`${brandDir}qualitylayer-logo.svg`, "utf8"), false);
const logo = await sharp(Buffer.from(wordmark)).resize({ width: 300 }).png().toBuffer();
const headline = await sharp({ text: {
  text: '<span foreground="#11243a" weight="600">The software factory\nfor your coding agents</span>',
  font: "Geist 68", fontfile: `${fontDir}geist-latin.woff2`, width: 1056, dpi: 72, rgba: true,
} }).png().toBuffer();
const caption = await sharp({ text: {
  text: '<span foreground="#2076c5">Plan · Build · Verify</span>',
  font: "Geist Mono 22", fontfile: `${fontDir}geist-mono-latin.woff2`, dpi: 72, rgba: true,
} }).png().toBuffer();
await sharp({ create: { width: 1200, height: 630, channels: 4, background: "#e9f2fb" } })
  .composite([{ input: logo, left: 72, top: 68 }, { input: headline, left: 72, top: 224 }, { input: caption, left: 72, top: 504 }])
  .png().toFile(`${publicDir}og.png`);

console.log("Exported monochrome brand assets, adaptive SVGs, app icons, favicon and 1200×630 social image.");
