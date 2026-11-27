"""References to the law (GEP 11).

The first part checks the requirements of GEP 11 for all policy objects shipped with
GETTSIM, the second part the parser for German references.
"""

from __future__ import annotations

import datetime
from collections.abc import Hashable
from typing import Any

import pytest
from ttsim.tt.column_objects_param_function import ParamFunction, PolicyFunction
from ttsim.tt.legal_references import (
    LegalReferenceParser,
    LegalReferences,
    NoLegalReference,
    legal_references_from_spec,
)
from ttsim.tt.rounding import RoundingSpec

from gettsim import MainTarget, main
from gettsim.legal_references import (
    LEGAL_REFERENCES_PARSER,
    Act,
    GermanLegalReferenceParser,
    LegalReference,
    Provision,
)


@pytest.fixture(scope="module")
def orig_policy_objects() -> dict[str, Any]:
    return main(
        main_targets=[
            MainTarget.orig_policy_objects.column_objects_and_param_functions,
            MainTarget.orig_policy_objects.param_specs,
        ],
    )["orig_policy_objects"]


def _location(path: tuple[str, ...]) -> str:
    return "/".join(path)


def _problems(
    location: str,
    references: LegalReferences | str | None,
    *,
    required: bool,
) -> list[str]:
    if isinstance(references, str):
        return [f"{location}: {references}"]
    if references is None:
        return [f"{location}: missing reference"] if required else []
    if isinstance(references, NoLegalReference):
        return []
    problems = []
    for reference in references:
        try:
            LEGAL_REFERENCES_PARSER.parse_reference(reference)
        except ValueError as e:
            problems.append(f"{location}: {reference!r}\n    {str(e).splitlines()[0]}")
    return problems


def _references_of(
    obj: PolicyFunction | ParamFunction | RoundingSpec,
) -> LegalReferences | str | None:
    """The references of a policy object, or the error message if they are malformed."""
    try:
        return obj.legal_references
    except ValueError as e:
        return str(e).splitlines()[0]


def _fail_if_problems(problems: list[str], what: str) -> None:
    if problems:
        listing = "\n".join(problems)
        pytest.fail(
            f"{len(problems)} {what} violate GEP 11 (references to the law):\n\n"
            f"{listing}",
            pytrace=False,
        )


def test_policy_functions_have_valid_references(orig_policy_objects):
    problems: list[str] = []
    objects = orig_policy_objects["column_objects_and_param_functions"]
    for path, obj in objects.items():
        if not isinstance(obj, PolicyFunction):
            continue
        location = _location(path)
        problems.extend(_problems(location, _references_of(obj), required=True))
        if obj.rounding_spec is not None:
            problems.extend(
                _problems(
                    f"{location} (rounding_spec)",
                    _references_of(obj.rounding_spec),
                    required=True,
                )
            )
    _fail_if_problems(problems, "policy functions or rounding specs")


def test_param_functions_have_valid_references(orig_policy_objects):
    problems: list[str] = []
    objects = orig_policy_objects["column_objects_and_param_functions"]
    for path, obj in objects.items():
        if isinstance(obj, ParamFunction):
            problems.extend(
                _problems(_location(path), _references_of(obj), required=False)
            )
    _fail_if_problems(problems, "parameter functions")


def test_param_date_entries_have_valid_references(orig_policy_objects):
    problems: list[str] = []
    for path, spec in orig_policy_objects["param_specs"].items():
        for date, entry in spec.items():
            if not isinstance(date, datetime.date):
                continue
            location = f"{_location(path)} ({date})"
            try:
                references = legal_references_from_spec(entry.get("reference"))
            except (TypeError, AttributeError):
                problems.append(f"{location}: reference must be a string or a list")
                continue
            problems.extend(_problems(location, references, required=True))
    _fail_if_problems(problems, "date entries of parameters")


def test_parser_satisfies_protocol():
    assert isinstance(LEGAL_REFERENCES_PARSER, LegalReferenceParser)


def test_main_uses_german_parser_by_default():
    out = main(
        main_target=MainTarget.legal_references.by_query,
        legal_references_query="§ 66 Abs. 1 EStG",
        policy_date_str="2025-01-01",
    )
    assert "kindergeld__satz_m" in out
    assert all(isinstance(r, LegalReference) for refs in out.values() for r in refs)


def test_main_accepts_custom_parser():
    out = main(
        main_target=MainTarget.legal_references.by_query,
        legal_references_query=("EStG", "nothing"),
        legal_references_parser=_SubstringParser(),
        policy_date_str="2025-01-01",
    )
    assert set(out) == {"EStG", "nothing"}
    assert out["nothing"] == {}


class _SubstringParser:
    def parse_reference(self, reference: str) -> str:
        return reference

    def parse_query(self, query: str) -> str:
        return query

    def matches(self, query: Hashable, reference: Hashable) -> bool:
        return str(query) in str(reference)


@pytest.mark.parametrize(
    ("reference", "expected"),
    [
        (
            "§ 66 Abs. 1 EStG idF Art. 2 G. v. 08.12.2022 BGBl. I S. 2230",
            LegalReference(
                provision=Provision(paragraph="66", parts=(("Abs", "1"),), law="EStG"),
                act=Act(
                    kind="G.",
                    date=datetime.date(2022, 12, 8),
                    article="2",
                    page=2230,
                ),
            ),
        ),
        (
            "§ 32a Abs. 1 EStG idF Art. 1 G. v. 23.12.2024 BGBl. 2024 I Nr. 449",
            LegalReference(
                provision=Provision(paragraph="32a", parts=(("Abs", "1"),), law="EStG"),
                act=Act(
                    kind="G.",
                    date=datetime.date(2024, 12, 23),
                    article="1",
                    year=2024,
                    number=449,
                ),
            ),
        ),
        (
            (
                "§ 11b Abs. 1 Satz 1 Nr. 6 Buchst. a SGB II idF Art. 2 Nr. 3 "
                "G. v. 24.03.2011 BGBl. I S. 453"
            ),
            LegalReference(
                provision=Provision(
                    paragraph="11b",
                    parts=(("Abs", "1"), ("Satz", "1"), ("Nr", "6"), ("Buchst", "a")),
                    law="SGB II",
                ),
                act=Act(
                    kind="G.",
                    date=datetime.date(2011, 3, 24),
                    article="2",
                    article_number="3",
                    page=453,
                ),
            ),
        ),
        (
            "§ 4 Nr. 1 SolZG 1995 idF B. v. 15.10.2002 BGBl. I S. 4130",
            LegalReference(
                provision=Provision(
                    paragraph="4", parts=(("Nr", "1"),), law="SolZG 1995"
                ),
                act=Act(kind="B.", date=datetime.date(2002, 10, 15), page=4130),
            ),
        ),
    ],
)
def test_parse_reference(reference, expected):
    parsed = LEGAL_REFERENCES_PARSER.parse_reference(reference)
    assert parsed == expected
    assert str(parsed) == reference


def test_parse_reference_keeps_letter_of_nummer():
    parsed = LEGAL_REFERENCES_PARSER.parse_reference(
        "§ 12 Abs. 2 Nr. 1a SGB II idF Art. 1 G. v. 16.12.2022 BGBl. I S. 2328"
    )
    assert isinstance(parsed, LegalReference)
    assert parsed.provision is not None
    assert parsed.provision.parts == (("Abs", "2"), ("Nr", "1a"))
    assert not LEGAL_REFERENCES_PARSER.matches(
        LEGAL_REFERENCES_PARSER.parse_query("§ 12 Abs. 2 Nr. 1 SGB II"), parsed
    )


def test_nummer_with_letter_differs_from_buchstabe():
    parser = LEGAL_REFERENCES_PARSER
    nummer = parser.parse_reference(
        "§ 3 Nr. 14a EStG idF Art. 3 G. v. 16.12.2022 BGBl. I S. 2294"
    )
    buchstabe = parser.parse_reference(
        "§ 3 Nr. 14 Buchst. a EStG idF Art. 3 G. v. 16.12.2022 BGBl. I S. 2294"
    )
    assert nummer != buchstabe
    assert not parser.matches(parser.parse_query("§ 3 Nr. 14 EStG"), nummer)
    assert parser.matches(parser.parse_query("§ 3 Nr. 14 EStG"), buchstabe)


@pytest.mark.parametrize(
    "reference",
    [
        "§ 10 Abs. 1 Nr. 2 Satz 1 EStG idF Art. 1 G. v. 08.12.2022 BGBl. I S. 2230",
        "§ 10 Abs. 1 Nr. 3 Buchst. a Satz 2 EStG idF G. v. 08.12.2022 BGBl. I S. 2230",
        "§ 10 Abs. 1 Satz 1 Halbsatz 2 EStG idF G. v. 08.12.2022 BGBl. I S. 2230",
        "§ 3 Nr. 26 Buchst. a Doppelbuchst. aa EStG idF G. v. 08.12.2022 BGBl. I S. 1",
    ],
)
def test_parse_reference_keeps_order_of_parts(reference):
    assert str(LEGAL_REFERENCES_PARSER.parse_reference(reference)) == reference


@pytest.mark.parametrize(
    ("reference", "expected"),
    [
        (
            "§ 1 Abs. 1 V. v. 05.06.1992 BGBl. I S. 1017",
            LegalReference(
                provision=Provision(paragraph="1", parts=(("Abs", "1"),), law=None),
                act=Act(kind="V.", date=datetime.date(1992, 6, 5), page=1017),
            ),
        ),
        (
            "§ 1 Art. 5 G. v. 19.12.1998 BGBl. I S. 3843",
            LegalReference(
                provision=Provision(paragraph="1", parts=(), law=None),
                act=Act(
                    kind="G.", date=datetime.date(1998, 12, 19), article="5", page=3843
                ),
            ),
        ),
    ],
)
def test_parse_reference_to_provision_of_act(reference, expected):
    parsed = LEGAL_REFERENCES_PARSER.parse_reference(reference)
    assert parsed == expected
    assert str(parsed) == reference


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("§ 1 V. v. 05.06.1992 BGBl. I S. 1017", True),
        ("§ 1 Abs. 1 V v 5.6.1992 BGBl I S 1017", True),
        ("V. v. 05.06.1992 BGBl. I S. 1017", True),
        ("§ 1 Abs. 2 V. v. 05.06.1992 BGBl. I S. 1017", False),
        ("§ 1 V. v. 09.06.1993 BGBl. I S. 917", False),
        ("§ 1 EStG", False),
    ],
)
def test_matches_provision_of_act(query, expected):
    parser = LEGAL_REFERENCES_PARSER
    reference = parser.parse_reference("§ 1 Abs. 1 V. v. 05.06.1992 BGBl. I S. 1017")
    assert parser.matches(parser.parse_query(query), reference) is expected


def test_parse_reference_accepts_s_for_satz():
    parsed = LEGAL_REFERENCES_PARSER.parse_reference(
        "§ 66 Abs. 1 S. 2 EStG idF Art. 2 G. v. 08.12.2022 BGBl. I S. 2230"
    )
    assert str(parsed) == (
        "§ 66 Abs. 1 Satz 2 EStG idF Art. 2 G. v. 08.12.2022 BGBl. I S. 2230"
    )


@pytest.mark.parametrize(
    ("reference", "match"),
    [
        ("§ 66 Abs. 1 EStG", "must have the form"),
        ("Art. 2 G. v. 08.12.2022 BGBl. I S. 2230", "must have the form"),
        ("§ 66 Abs 1 EStG idF G. v. 08.12.2022 BGBl. I S. 2230", "canonical form"),
        ("§ 66 (1) EStG idF G. v. 08.12.2022 BGBl. I S. 2230", "canonical form"),
        ("§ 66 Estg idF G. v. 08.12.2022 BGBl. I S. 2230", "Unknown law 'Estg'"),
        ("§ 66 SGB 2 idF G. v. 08.12.2022 BGBl. I S. 2230", "Unknown law"),
        ("§ 32 Art. 2-4 EStG idF G. v. 08.12.2022 BGBl. I S. 2230", "single"),
        ("§ 66 f. EStG idF G. v. 08.12.2022 BGBl. I S. 2230", "single paragraph"),
        ("§ 66 Abs. 1 und 2 EStG idF G. v. 08.12.2022 BGBl. I S. 2230", "single"),
        (
            "§ 66 Abs. 1 EStG i.V.m. § 1 BKGG idF G. v. 08.12.2022 BGBl. I S. 2230",
            "single paragraph",
        ),
        ("§ 66 Abs. 1 idF G. v. 08.12.2022 BGBl. I S. 2230", "law is missing"),
        ("Abs. 1 EStG idF G. v. 08.12.2022 BGBl. I S. 2230", "starts with the"),
        ("§ 1 Abs. 1 EStG V. v. 05.06.1992 BGBl. I S. 1017", "names a law"),
        ("§ 1 Abs 1 V. v. 05.06.1992 BGBl. I S. 1017", "canonical form"),
        ("§§ 66, 67 EStG idF G. v. 08.12.2022 BGBl. I S. 2230", "single paragraph"),
        ("§ 66 Abs. 1 bis 3 EStG idF G. v. 08.12.2022 BGBl. I S. 2230", "single"),
        ("§ 66 EStG idF Artikel 2 G. v. 08.12.2022 BGBl. I S. 2230", "Cannot parse"),
        ("§ 66 EStG idF G. v. 8.12.2022 BGBl. I S. 2230", "Cannot parse the act"),
        ("§ 66 EStG idF G. v. 31.02.2022 BGBl. I S. 2230", "Invalid date"),
        ("§ 66 EStG idF G. v. 08.12.2024 BGBl. I S. 2230", "from 2023 on"),
        ("§ 66 EStG idF G. v. 08.12.2022 BGBl. 2022 I Nr. 3", "until 2022"),
        ("§ 66 EStG idF G. v. 08.12.2024 BGBl. 2026 I Nr. 3", "until 2022"),
    ],
)
def test_parse_reference_rejects_malformed(reference, match):
    with pytest.raises(ValueError, match=match):
        LEGAL_REFERENCES_PARSER.parse_reference(reference)


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("§ 66 EStG", "§ 66 EStG"),
        ("§66 Estg", "§ 66 EStG"),
        ("§ 66 (1) EStG", "§ 66 Abs. 1 EStG"),
        ("§ 66 Absatz 1 EStG", "§ 66 Abs. 1 EStG"),
        ("§ 66 Abs 1 S 2 EStG", "§ 66 Abs. 1 Satz 2 EStG"),
        ("§ 20 SGB 2", "§ 20 SGB II"),
        ("§ 32A EStG", "§ 32a EStG"),
        ("§ 3 Nummer 14 Buchstabe a EStG", "§ 3 Nr. 14 Buchst. a EStG"),
        ("§ 3 Nr 14 lit. a EStG", "§ 3 Nr. 14 Buchst. a EStG"),
        ("§ 10 Abs. 1 S. 1 Hs. 2 EStG", "§ 10 Abs. 1 Satz 1 Halbsatz 2 EStG"),
        ("G. v. 8.12.2022 BGBl. I S. 2230", "G. v. 08.12.2022 BGBl. I S. 2230"),
        (
            "§ 66 EStG i.d.F. G v. 08.12.2022 BGBl I S. 2230",
            "§ 66 EStG idF G. v. 08.12.2022 BGBl. I S. 2230",
        ),
    ],
)
def test_parse_query(query, expected):
    assert str(LEGAL_REFERENCES_PARSER.parse_query(query)) == expected


def test_parse_query_lists_closest_laws():
    with pytest.raises(ValueError, match="closest abbreviations are: EStG"):
        LEGAL_REFERENCES_PARSER.parse_query("§ 66 EStGG")


_REFERENCE = "§ 66 Abs. 1 Satz 2 EStG idF Art. 2 G. v. 08.12.2022 BGBl. I S. 2230"


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("§ 66 EStG", True),
        ("§ 66 Abs. 1 EStG", True),
        ("§ 66 Abs. 1 Satz 2 EStG", True),
        ("§ 66 Abs. 1 Satz 2 Nr. 1 EStG", True),
        ("§ 66 Abs. 2 EStG", False),
        ("§ 66 Abs. 1 Satz 1 EStG", False),
        ("§ 67 EStG", False),
        ("§ 66 BKGG", False),
        ("G. v. 08.12.2022 BGBl. I S. 2230", True),
        ("Art. 2 G. v. 08.12.2022 BGBl. I S. 2230", True),
        ("Art. 3 G. v. 08.12.2022 BGBl. I S. 2230", False),
        ("§ 66 EStG idF G. v. 08.12.2022 BGBl. I S. 2230", True),
        ("§ 66 EStG idF Art. 1 G. v. 23.12.2024 BGBl. 2024 I Nr. 449", False),
    ],
)
def test_matches(query, expected):
    parser = LEGAL_REFERENCES_PARSER
    reference = parser.parse_reference(_REFERENCE)
    assert parser.matches(parser.parse_query(query), reference) is expected


def test_less_precise_reference_covers_its_parts():
    parser = LEGAL_REFERENCES_PARSER
    reference = parser.parse_reference(
        "§ 66 EStG idF Art. 2 G. v. 08.12.2022 BGBl. I S. 2230"
    )
    assert parser.matches(parser.parse_query("§ 66 Abs. 2 EStG"), reference)


def test_custom_laws():
    parser = GermanLegalReferenceParser(laws={"XG": "X-Gesetz"})
    parser.parse_reference("§ 1 XG idF G. v. 01.01.2000 BGBl. I S. 1")
    with pytest.raises(ValueError, match="Unknown law"):
        parser.parse_reference("§ 1 EStG idF G. v. 01.01.2000 BGBl. I S. 1")
