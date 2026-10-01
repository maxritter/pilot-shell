import type { ReactNode } from "react";
import Footer from "@/components/Footer";
import NavBar from "@/components/NavBar";

/** The frame every page shares. The wrapper is the size container the responsive rules key on. */
const Page = ({ children, className }: { children: ReactNode; className?: string }) => (
  <div className={className ? `w7-root ${className}` : "w7-root"}>
    <a className="w7-skip" href="#main">Skip to content</a>
    <NavBar />
    <main id="main">{children}</main>
    <Footer />
  </div>
);

export default Page;
