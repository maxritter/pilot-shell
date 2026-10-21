import React, { type ComponentProps } from "react";
import { useLocation } from "@docusaurus/router";
import OriginalLayout from "@theme-original/Layout";
import SearchMain from "../../components/SearchMain";

/** Keep the header and footer outside the search results' main landmark. */
export default function Layout(props: ComponentProps<typeof OriginalLayout>) {
  const { pathname } = useLocation();
  const search = pathname.replace(/\/$/, "") === "/search";
  return <OriginalLayout {...props}>{search ? <SearchMain>{props.children}</SearchMain> : props.children}</OriginalLayout>;
}
