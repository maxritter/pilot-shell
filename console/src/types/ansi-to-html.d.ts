declare module 'ansi-to-html' {
  interface AnsiToHtmlOptions {
    fg?: string;
    bg?: string;
    newline?: boolean;
    escapeXML?: boolean;
    stream?: boolean;
    colors?: string[] | Record<number, string>;
  }

  class Convert {
    constructor(options?: AnsiToHtmlOptions);
    toHtml(input: string): string;
  }

  export = Convert;
}
