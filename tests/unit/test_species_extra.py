"""Unit tests for the Aotearoa NZ species table (``species_extra``).

The table is a pure-data module — no dependencies on the FIA or NSVB
machinery. These tests verify the lookup API + the shape of the rows.
"""

from __future__ import annotations

from pyfia.constants.species_extra import (
    NZ_SPECIES_EXTRAS,
    SpeciesExtra,
    by_alias,
    by_name,
    lookup,
)


class TestTableContents:
    """Every row has the expected shape."""

    def test_table_is_not_empty(self) -> None:
        assert len(NZ_SPECIES_EXTRAS) > 0

    def test_each_row_is_a_species_extra(self) -> None:
        for entry in NZ_SPECIES_EXTRAS:
            assert isinstance(entry, SpeciesExtra)

    def test_no_duplicate_canonical_names(self) -> None:
        names = [s.name for s in NZ_SPECIES_EXTRAS]
        assert len(names) == len(set(names))

    def test_canonical_names_are_lowercase_hyphenated(self) -> None:
        # Convention: canonical name is lowercase, hyphen-separated.
        for entry in NZ_SPECIES_EXTRAS:
            assert entry.name == entry.name.lower()
            assert "_" not in entry.name
            assert " " not in entry.name

    def test_aliases_are_normalised(self) -> None:
        # Aliases are lowercase, hyphen-separated (no spaces/underscores).
        for entry in NZ_SPECIES_EXTRAS:
            for alias in entry.common_names:
                assert alias == alias.lower()
                assert " " not in alias

    def test_wdsg_is_plausible(self) -> None:
        for entry in NZ_SPECIES_EXTRAS:
            # Woods range from 0.3 (light pines) to 0.7 (heavy beech).
            assert 0.30 <= entry.wdsg <= 0.75, (
                f"{entry.name} WDSG {entry.wdsg} outside plausible range"
            )

    def test_spcd_is_valid_or_none(self) -> None:
        # When spcd is not None, it's a FIA SPCD integer in the
        # canonical range 1..999.
        for entry in NZ_SPECIES_EXTRAS:
            if entry.spcd is not None:
                assert isinstance(entry.spcd, int) and 1 <= entry.spcd <= 999

    def test_citation_present(self) -> None:
        for entry in NZ_SPECIES_EXTRAS:
            assert isinstance(entry.citation, str) and entry.citation


class TestLookupByName:
    """``by_name`` looks up canonical names."""

    def test_known_species(self) -> None:
        e = by_name("radiata-pine")
        assert e is not None
        assert e.spcd == 131
        assert e.wdsg == 0.41

    def test_unknown_species_returns_none(self) -> None:
        assert by_name("not-a-real-tree") is None


class TestLookupByAlias:
    """``by_alias`` handles common-name variants."""

    def test_common_alias(self) -> None:
        e = by_alias("pine")
        assert e is not None
        assert e.name == "radiata-pine"

    def test_underscore_input_normalised(self) -> None:
        # Aliases are stored with hyphens but callers may pass underscores.
        e = by_alias("pin_radiata")
        assert e is not None
        assert e.name == "radiata-pine"


class TestLookup:
    """``lookup`` is the convenience wrapper."""

    def test_canonical_name_works(self) -> None:
        assert lookup("kauri") is not None

    def test_alias_works(self) -> None:
        assert lookup("douglas") is not None
        assert lookup("douglas").name == "douglas-fir"

    def test_unknown_returns_none(self) -> None:
        assert lookup("made-up-tree") is None


class TestPlantedExoticsAtTop:
    """The first 5 rows are the planted exotics that account for ~95%
    of NZ plantation forestry area.

    If this ordering is broken — e.g., somebody adds a row to the
    middle — the table re-ordering should be an explicit decision.
    """

    def test_first_five_are_planted_exotics(self) -> None:
        first_five_names = [s.name for s in NZ_SPECIES_EXTRAS[:5]]
        for needle in (
            "radiata-pine",
            "douglas-fir",
            "cypress-macrocarpa",
            "eucalyptus",
            "larch",
        ):
            assert needle in first_five_names, (
                f"Exotic {needle} should be in the first 5 rows "
                f"(plantation first, indigenous second). Found: {first_five_names}"
            )
