import { readFile } from "node:fs/promises";
import { pathToFileURL } from "node:url";
import { QUALITYLAYER_PRODUCTS } from "../src/lib/polar-products.ts";

export const LEGACY_PRODUCTS = ["35801944-799d-4763-88fa-b2046765464f", "c0a1f846-2909-4aff-b3fe-42a4818c34b5", "bf3d0ac1-6cda-4122-bd76-a20d0beef958"];
const BENEFITS = { solo: "ae926479-bddd-4362-824d-7772cd4fbc72", team: "b65424b6-3609-42de-9be3-3c4d59bbff36" };
const PRICES = { solo: { monthly: 2900, yearly: 28800 }, team: { monthly: 4900, yearly: 46800 } };

export function verifyCatalog(products, discounts, now = Date.now()) {
  const errors = [];
  const require = (condition, message) => { if (!condition) errors.push(message); };
  const ids = Object.values(QUALITYLAYER_PRODUCTS).flatMap(Object.values).sort();
  for (const [plan, intervals] of Object.entries(QUALITYLAYER_PRODUCTS)) {
    for (const [interval, id] of Object.entries(intervals)) {
      const product = products.find(item => item.id === id);
      const label = `${plan} ${interval}`;
      require(product && !product.is_archived, `${label}: product missing or archived`);
      require(product?.recurring_interval === (interval === "monthly" ? "month" : "year"), `${label}: wrong billing interval`);
      const prices = product?.prices.filter(price => !price.is_archived) ?? [];
      require(prices.length === 1, `${label}: expected one active price`);
      const price = prices[0];
      require(price?.price_currency === "usd", `${label}: wrong currency`);
      if (plan === "solo") require(price?.amount_type === "fixed" && price.price_amount === PRICES[plan][interval], `${label}: wrong price`);
      else {
        const tiers = price?.seat_tiers;
        require(price?.amount_type === "seat_based" && tiers?.seat_tier_type === "volume" && tiers.minimum_seats === 1 && tiers.tiers.length === 1 && tiers.tiers[0].min_seats === 1 && tiers.tiers[0].max_seats == null && tiers.tiers[0].price_per_seat === PRICES[plan][interval], `${label}: wrong seat price or tiers`);
      }
      const benefit = product?.benefits.find(item => item.id === BENEFITS[plan]);
      require(benefit?.type === "license_keys" && !benefit.is_deleted && benefit.properties?.prefix === "QL" && benefit.properties?.activations?.limit > 0, `${label}: QL licence delivery benefit missing or invalid`);
    }
  }
  for (const id of LEGACY_PRODUCTS) require(products.find(product => product.id === id)?.is_archived === true, `Legacy product ${id}: new purchases still enabled`);
  const promo = discounts.find(discount => discount.code === "PILOTTHANKS20");
  require(promo?.type === "percentage" && promo.basis_points === 2000, "Newsletter offer: expected 20 percent");
  require(promo?.duration === "repeating" && promo.duration_in_months === 12, "Newsletter offer: must end after 12 months");
  require(JSON.stringify(promo?.products.map(product => product.id).sort()) === JSON.stringify(ids), "Newsletter offer: must apply to all four QL products and no others");
  require(promo && (!promo.starts_at || Date.parse(promo.starts_at) <= now) && (!promo.ends_at || Date.parse(promo.ends_at) > now) && (promo.max_redemptions == null || promo.redemptions_count < promo.max_redemptions), "Newsletter offer: not currently redeemable");
  if (errors.length) throw new Error(errors.join("\n"));
  return { products: 4, legacyProductsClosed: LEGACY_PRODUCTS.length, newsletterPercent: 20, newsletterMonths: 12, licenceBenefits: 2 };
}

export async function verifyRemoteCatalog(token, request = fetch) {
  if (!token) throw new Error("POLAR_ACCESS_TOKEN is required for the live commerce audit");
  const read = async resource => {
    const response = await request(`https://api.polar.sh/v1/${resource}/?limit=100`, { headers: { Authorization: `Bearer ${token}` }, signal: AbortSignal.timeout(15000) });
    if (!response.ok) throw new Error(`Polar ${resource}: HTTP ${response.status}`);
    const data = await response.json();
    if (data.pagination?.max_page > 1) throw new Error(`Polar ${resource}: audit requires pagination before this catalog can be verified`);
    return data.items;
  };
  const [products, discounts] = await Promise.all([read("products"), read("discounts")]);
  return verifyCatalog(products, discounts);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const credentialIndex = process.argv.indexOf("--credentials");
  const token = credentialIndex < 0 ? process.env.POLAR_ACCESS_TOKEN : (await readFile(process.argv[credentialIndex + 1], "utf8")).match(/polar_oat_[A-Za-z0-9_-]+/)?.[0];
  verifyRemoteCatalog(token).then(result => console.log(JSON.stringify(result))).catch(error => { console.error(error.message); process.exitCode = 1; });
}
