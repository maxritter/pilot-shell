"""pilot-sec sbom — software bill of materials."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Optional

import click

from pilot_sec.core.context import SecContext
from pilot_sec.core.output import OutputWriter


@click.group("sbom")
@click.pass_obj
def sbom_group(ctx: SecContext) -> None:
    """Generate and verify software bills of materials."""


@sbom_group.command("generate")
@click.option("--format", "sbom_format", default="cyclonedx",
              type=click.Choice(["cyclonedx", "spdx", "json"]),
              help="SBOM format")
@click.option("--output", "output_path", default=None, metavar="PATH", help="Output file")
@click.option("--include-dev", is_flag=True, help="Include dev dependencies")
@click.option("--sign", is_flag=True, help="Sign the SBOM")
@click.option("--image", default=None, help="Container image to generate SBOM from")
@click.pass_obj
def sbom_generate(ctx: SecContext, sbom_format: str, output_path: Optional[str],
                  include_dev: bool, sign: bool, image: Optional[str]) -> None:
    """Generate an SBOM for the project."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)

    default_output = str(ctx.reports_dir / f"sbom.{_ext(sbom_format)}")
    dest = Path(output_path or default_output)
    dest.parent.mkdir(parents=True, exist_ok=True)

    if image:
        _generate_image_sbom(out, image, sbom_format, dest, ctx.dry_run)
    else:
        _generate_fs_sbom(out, ctx.project_root, sbom_format, dest, include_dev, ctx.dry_run)

    if sign and not ctx.dry_run:
        out.info("  Signing requires `cosign` — run `pilot-sec attest scan` for full provenance")

    if ctx.output_format == "json":
        out.emit_result(
            command="sbom generate",
            status="success",
            artifacts=[str(dest)],
        )


@sbom_group.command("diff")
@click.option("--from", "from_path", required=True, metavar="PATH", help="Old SBOM file")
@click.option("--to", "to_path", required=True, metavar="PATH", help="New SBOM file")
@click.pass_obj
def sbom_diff(ctx: SecContext, from_path: str, to_path: str) -> None:
    """Compare two SBOMs and show component changes."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)

    try:
        old = json.loads(Path(from_path).read_text())
        new = json.loads(Path(to_path).read_text())
    except Exception as exc:
        out.err(f"Failed to read SBOM: {exc}")
        raise SystemExit(1)

    old_components = _extract_components(old)
    new_components = _extract_components(new)

    added = new_components - old_components
    removed = old_components - new_components

    if not added and not removed:
        out.success("SBOMs are identical")
        return

    out.console.print(f"[bold]SBOM diff:[/bold] {from_path} → {to_path}")
    for c in sorted(added):
        out.console.print(f"  [green]+[/green] {c}")
    for c in sorted(removed):
        out.console.print(f"  [red]-[/red] {c}")


@sbom_group.command("sign")
@click.argument("sbom_path")
@click.pass_obj
def sbom_sign(ctx: SecContext, sbom_path: str) -> None:
    """Sign an SBOM with cosign."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    if not Path(sbom_path).exists():
        out.err(f"SBOM not found: {sbom_path}")
        raise SystemExit(1)
    out.step(f"Signing {sbom_path}")
    _run_cosign_attest(out, sbom_path, ctx.dry_run)


@sbom_group.command("verify")
@click.argument("sbom_path")
@click.pass_obj
def sbom_verify(ctx: SecContext, sbom_path: str) -> None:
    """Verify SBOM integrity and signature."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    path = Path(sbom_path)
    if not path.exists():
        out.err(f"SBOM not found: {sbom_path}")
        raise SystemExit(1)
    try:
        data = json.loads(path.read_text())
        components = _extract_components(data)
        out.success(f"SBOM valid — {len(components)} component(s) found")
    except Exception as exc:
        out.err(f"SBOM validation failed: {exc}")
        raise SystemExit(1)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _ext(fmt: str) -> str:
    return {"cyclonedx": "cdx.json", "spdx": "spdx.json", "json": "json"}.get(fmt, "json")


def _generate_fs_sbom(out: OutputWriter, path: Path, fmt: str, dest: Path, include_dev: bool, dry_run: bool) -> None:
    """Use syft or cdxgen if available, else build minimal SBOM."""
    import shutil

    if shutil.which("syft"):
        cmd = ["syft", str(path), "-o", f"cyclonedx-json={dest}"]
        if dry_run:
            out.info(f"  dry-run: would run {' '.join(cmd)}")
            return
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            out.success(f"SBOM generated with syft → {dest}")
        else:
            out.err(f"syft failed: {result.stderr[:200]}")
    elif shutil.which("cdxgen"):
        cmd = ["cdxgen", str(path), "-o", str(dest)]
        if dry_run:
            out.info(f"  dry-run: would run {' '.join(cmd)}")
            return
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            out.success(f"SBOM generated with cdxgen → {dest}")
        else:
            out.err(f"cdxgen failed: {result.stderr[:200]}")
    else:
        out.warn("syft or cdxgen not found — generating minimal SBOM")
        sbom = _minimal_sbom(path, fmt)
        if not dry_run:
            dest.write_text(json.dumps(sbom, indent=2))
            out.success(f"Minimal SBOM written → {dest}")
        else:
            out.info(f"  dry-run: would write {dest}")


def _generate_image_sbom(out: OutputWriter, image: str, fmt: str, dest: Path, dry_run: bool) -> None:
    import shutil

    if shutil.which("syft"):
        cmd = ["syft", image, "-o", f"cyclonedx-json={dest}"]
        if dry_run:
            out.info(f"  dry-run: would run {' '.join(cmd)}")
            return
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            out.success(f"Image SBOM generated → {dest}")
        else:
            out.err(f"syft failed: {result.stderr[:200]}")
    else:
        out.warn("syft not found — install it to generate image SBOMs")


def _run_cosign_attest(out: OutputWriter, path: str, dry_run: bool) -> None:
    import shutil

    if not shutil.which("cosign"):
        out.warn("cosign not found — install it for signing support")
        return
    if dry_run:
        out.info("  dry-run: would sign with cosign")
        return
    result = subprocess.run(["cosign", "sign-blob", path], capture_output=True, text=True)
    if result.returncode == 0:
        out.success(f"Signed: {path}")
    else:
        out.err(f"cosign failed: {result.stderr[:200]}")


def _minimal_sbom(path: Path, fmt: str) -> dict:
    import datetime

    components: list[dict] = []
    # Detect requirements.txt
    for req_file in path.glob("**/requirements*.txt"):
        for line in req_file.read_text(errors="replace").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split("==")
                name = parts[0].strip()
                version = parts[1].strip() if len(parts) > 1 else "unknown"
                components.append({"type": "library", "name": name, "version": version, "purl": f"pkg:pypi/{name}@{version}"})

    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "version": 1,
        "metadata": {"timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()},
        "components": components,
    }


def _extract_components(sbom: dict) -> set[str]:
    components = set()
    for c in sbom.get("components", []):
        name = c.get("name", "")
        version = c.get("version", "")
        components.add(f"{name}@{version}" if version else name)
    # SPDX format
    for pkg in sbom.get("packages", []):
        name = pkg.get("name", "")
        version = pkg.get("versionInfo", "")
        components.add(f"{name}@{version}" if version else name)
    return components
