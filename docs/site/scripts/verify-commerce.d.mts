export const LEGACY_PRODUCTS: string[];
export function verifyCatalog(products: readonly unknown[], discounts: readonly unknown[], now?: number): {
  products: number; legacyProductsClosed: number; newsletterPercent: number; newsletterMonths: number; licenceBenefits: number;
};
export function verifyRemoteCatalog(token: string | undefined, request?: (url: string, init: RequestInit) => Promise<Response>): Promise<ReturnType<typeof verifyCatalog>>;
