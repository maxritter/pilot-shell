// Written by video/scripts/publish.mjs: the films on the media host (Cloudflare R2 behind the
// qualitylayer-media Worker). Re-run the publish script for a new cut instead of editing by hand.

export type Film = { src: string; poster: string; duration: number };

export const FILMS = {
  launch: {
    src: "https://qualitylayer-media.max-ritter.workers.dev/launch-v6.mp4",
    poster: "https://qualitylayer-media.max-ritter.workers.dev/launch-v6.webp",
    duration: 198,
  },
  walkthrough: {
    src: "https://qualitylayer-media.max-ritter.workers.dev/walkthrough-v2.mp4",
    poster: "https://qualitylayer-media.max-ritter.workers.dev/walkthrough-v2.webp",
    duration: 592,
  },
} satisfies Record<string, Film>;
