#!/usr/bin/env python3
"""
Demonstration of the Aotearoa species extra table (`pyfia.constants.species_extra`).

This script shows how to look up non-FIA species (notably Aotearoa NZ
indigenous timber trees) and pass the result through pyFIA's standard
NSVB carbon pipeline.

Run:
    python examples/species_extra_nz_demo.py
"""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

from pyfia.constants.species_extra import (
    NZ_SPECIES_EXTRAS,
    lookup,
)

console = Console()


def demo_lookup() -> None:
    """Look up a handful of common NZ species — verbose friendly."""
    console.print("\n[bold blue]Species lookup demo[/bold blue]\n")

    table = Table(title="Aotearoa NZ species (sample)")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("FIA SPCD", justify="right")
    table.add_column("WDSG (g/cm³)", justify="right")
    table.add_column("Family", style="green")
    table.add_column("Citation", style="dim")

    for name in ("radiata-pine", "rimu", "kauri", "totara", "douglas-fir"):
        e = lookup(name)
        if e is None:
            console.print(f"[red]No entry for {name}[/red]")
            continue
        table.add_row(e.name, str(e.spcd), f"{e.wdsg:.2f}", e.family, e.citation)

    console.print(table)


def demo_passthrough() -> None:
    """Show how to wire the lookup into the NSVB pipeline.

    The lookup returns a `SpeciesExtra` row. The NSVB pipeline uses
    `SPCD` and `WDSG` (via `constants/columns`). For NZ-only species
    (spcd=None), NSVB's Jenkins Model 5 fallback dispatches with
    `WDSG` as the multiplier.
    """
    console.print("\n[bold blue]NSVB pass-through example[/bold blue]\n")

    for name in ("radiata-pine", "kauri", "rimu"):
        e = lookup(name)
        if e is None:
            continue
        spcd_str = str(e.spcd) if e.spcd is not None else "(NZ-only, Jenkins fallback)"
        console.print(
            f"  {e.name}: SPCD={spcd_str}, WDSG={e.wdsg:.2f} g/cm³"
        )
        # In practice: pass e.spcd to live_tree(..., spcd=e.spcd)
        # and e.wdsg as the multiplier for Jenkins Mode 5.
        # See pyfia.carbon.live_tree for the full call surface.


def demo_table_summary() -> None:
    """Print a one-line summary of the whole table."""
    n_with_spcd = sum(1 for s in NZ_SPECIES_EXTRAS if s.spcd is not None)
    n_without_spcd = len(NZ_SPECIES_EXTRAS) - n_with_spcd
    console.print(
        f"\n[bold blue]Table summary[/bold blue]: {len(NZ_SPECIES_EXTRAS)} species total, "
        f"{n_with_spcd} with FIA SPCD mapping, "
        f"{n_without_spcd} NZ-only (Jenkins fallback).\n"
    )


def main() -> None:
    demo_table_summary()
    demo_lookup()
    demo_passthrough()


if __name__ == "__main__":
    main()
