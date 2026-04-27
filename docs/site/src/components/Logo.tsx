import logoWebp from "@/assets/logo.webp";
import logoPng from "@/assets/logo.png";

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
      <picture>
        <source srcSet={logoWebp} type="image/webp" />
        <img
          src={logoPng}
          alt="Pilot Shell — the Claude Code engineering platform"
          className={`${sizeClass} h-auto animate-glow`}
          loading={isEager ? "eager" : "lazy"}
          fetchPriority={isEager ? "high" : undefined}
          width={1200}
          height={676}
        />
      </picture>
    </div>
  );
};

export default Logo;
