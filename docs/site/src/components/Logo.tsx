interface LogoProps {
  variant?: "hero" | "footer";
}

const Logo = ({ variant = "hero" }: LogoProps) => {
  const sizeClass = variant === "hero"
    ? "w-[85vw] max-w-[240px] xs:max-w-[280px] sm:max-w-[400px] md:max-w-[500px] lg:max-w-[600px]"
    : "w-full max-w-[160px] xs:max-w-[180px] sm:max-w-[240px]";

  const paddingClass = variant === "hero" ? "p-2 xs:p-4 sm:p-6" : "p-4";
  const isEager = variant === "hero";

  return (
    <div className={`inline-block ${paddingClass}`}>
      <img
        src="/logo_sm.webp"
        srcSet="/logo_sm.webp 980w, /logo.webp 1228w"
        sizes="(min-width: 1024px) 600px, (min-width: 768px) 500px, (min-width: 640px) 400px, (min-width: 475px) 280px, 240px"
        alt="Pilot Shell — how real engineers run Claude Code and Codex"
        className={`${sizeClass} h-auto animate-glow logo-fade-mask`}
        loading={isEager ? "eager" : "lazy"}
        decoding={isEager ? "sync" : "async"}
        width={1228}
        height={691}
      />
    </div>
  );
};

export default Logo;
