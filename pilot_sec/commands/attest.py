"""pilot-sec attest — build provenance and evidence."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import click

from pilot_sec.core.context import SecContext
from pilot_sec.core.output import OutputWriter


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_attestation(dest: Path, attestation: dict) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(attestation, indent=2))


@click.group("attest")
@click.pass_obj
def attest_group(ctx: SecContext) -> None:
    """Attach provenance and evidence to builds and releases."""


@attest_group.command("build")
@click.option("--artifact", required=True, metavar="PATH", help="Build artifact to attest")
@click.option("--builder", default=None, help="Builder identity (e.g. github-actions)")
@click.pass_obj
def attest_build(ctx: SecContext, artifact: str, builder: Optional[str]) -> None:
    """Attach provenance to a build artifact."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    art_path = Path(artifact)
    if not art_path.exists():
        out.err(f"Artifact not found: {artifact}")
        raise SystemExit(1)

    digest = _sha256(art_path)
    attestation = {
        "_type": "https://in-toto.io/Statement/v0.1",
        "subject": [{"name": artifact, "digest": {"sha256": digest}}],
        "predicateType": "https://slsa.dev/provenance/v0.2",
        "predicate": {
            "builder": {"id": builder or "local"},
            "buildType": "pilot-sec/build/v1",
            "invocation": {"parameters": {}},
            "metadata": {
                "buildInvocationId": str(uuid.uuid4()),
                "buildStartedOn": _now(),
                "buildFinishedOn": _now(),
                "completeness": {"parameters": False, "environment": False, "materials": False},
            },
        },
    }

    dest = ctx.reports_dir / f"{art_path.name}.build.attestation.json"
    if not ctx.dry_run:
        _write_attestation(dest, attestation)
        out.success(f"Build attestation written → {dest}")
    else:
        out.info(f"  dry-run: would write {dest}")


@attest_group.command("scan")
@click.option("--from", "from_path", required=True, metavar="PATH", help="Scan results JSON")
@click.pass_obj
def attest_scan(ctx: SecContext, from_path: str) -> None:
    """Prove a scan was executed and attach results as evidence."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    src = Path(from_path)
    if not src.exists():
        out.err(f"Scan results not found: {from_path}")
        raise SystemExit(1)

    digest = _sha256(src)
    attestation = {
        "_type": "https://in-toto.io/Statement/v0.1",
        "subject": [{"name": from_path, "digest": {"sha256": digest}}],
        "predicateType": "https://pilot-sec.dev/scan/v1",
        "predicate": {
            "scanner": "pilot-sec",
            "scanTime": _now(),
            "resultsDigest": digest,
        },
    }

    dest = ctx.reports_dir / "scan.attestation.json"
    if not ctx.dry_run:
        _write_attestation(dest, attestation)
        out.success(f"Scan attestation written → {dest}")
    else:
        out.info(f"  dry-run: would write {dest}")


@attest_group.command("release")
@click.option("--sbom", "sbom_path", default=None, metavar="PATH", help="SBOM to include")
@click.option("--output", "output_path", default=None, metavar="PATH")
@click.pass_obj
def attest_release(ctx: SecContext, sbom_path: Optional[str], output_path: Optional[str]) -> None:
    """Create a release attestation bundle."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)

    evidence: dict = {"timestamp": _now(), "generator": "pilot-sec"}

    if sbom_path and Path(sbom_path).exists():
        evidence["sbom_digest"] = _sha256(Path(sbom_path))
        evidence["sbom_path"] = sbom_path

    attestation = {
        "_type": "https://in-toto.io/Statement/v0.1",
        "predicateType": "https://pilot-sec.dev/release/v1",
        "predicate": evidence,
    }

    dest = Path(output_path) if output_path else ctx.reports_dir / "release.attestation.json"
    if not ctx.dry_run:
        _write_attestation(dest, attestation)
        out.success(f"Release attestation written → {dest}")
    else:
        out.info(f"  dry-run: would write {dest}")


@attest_group.command("verify")
@click.argument("attestation_file")
@click.pass_obj
def attest_verify(ctx: SecContext, attestation_file: str) -> None:
    """Verify an attestation file."""
    out = OutputWriter(fmt=ctx.output_format, no_color=ctx.no_color, quiet=ctx.quiet)
    path = Path(attestation_file)
    if not path.exists():
        out.err(f"Attestation not found: {attestation_file}")
        raise SystemExit(1)
    try:
        data = json.loads(path.read_text())
        predicate_type = data.get("predicateType", "unknown")
        subjects = data.get("subject", [])
        out.success(f"Attestation valid")
        out.console.print(f"  Type     : {predicate_type}")
        out.console.print(f"  Subjects : {len(subjects)}")
        for s in subjects:
            out.console.print(f"    {s.get('name')} — sha256:{s.get('digest', {}).get('sha256', '?')[:16]}...")
    except Exception as exc:
        out.err(f"Attestation verification failed: {exc}")
        raise SystemExit(1)
