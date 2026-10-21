/** Phones and tablets: they cannot open a desktop App, and have no download card. */
export const isPhone = (userAgent: string) => /iPhone|iPad|iPod|Android/.test(userAgent);
