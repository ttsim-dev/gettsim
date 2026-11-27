"""Parser for references to German law (GEP 11).

A reference consists of a provision and the act that gave the provision its wording::

    § 66 Abs. 1 EStG idF Art. 2 G. v. 08.12.2022 BGBl. I S. 2230

A provision cites a single paragraph, optionally narrowed down by Absatz, Satz,
Halbsatz, Nummer, Buchstabe and Doppelbuchstabe, followed by the abbreviation of the
law, which must be listed in `laws.yaml`. The act is cited by its publication in the
BGBl.

A provision of an act without an official abbreviation, typically a Verordnung that sets
the values for one year, is cited by the act itself, without `idF`::

    § 1 Abs. 1 V. v. 05.06.1992 BGBl. I S. 1017

References in the code are parsed strictly: they must be written in canonical form.
Queries entered by users are parsed leniently, e.g., `§66 Estg` and `§ 66 (1) EStG` are
accepted as well.
"""

from __future__ import annotations

import datetime
import difflib
import re
from collections.abc import Hashable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

import yaml

LAWS_PATH = Path(__file__).parent / "laws.yaml"

#: Separator of provision and act.
IDF = "idF"

ActKind = Literal["G.", "V.", "B."]

_ROMAN = {
    "I": 1,
    "II": 2,
    "III": 3,
    "IV": 4,
    "V": 5,
    "VI": 6,
    "VII": 7,
    "VIII": 8,
    "IX": 9,
    "X": 10,
    "XI": 11,
    "XII": 12,
    "XIII": 13,
    "XIV": 14,
}

_ACT_STRICT_RE = re.compile(
    r"^(?:Art\. (?P<article>\d+[a-z]?)(?: Nr\. (?P<article_number>\d+[a-z]?))? )?"
    r"(?P<kind>[GVB])\. v\. (?P<date>\d{2}\.\d{2}\.\d{4}) "
    r"BGBl\. (?:I S\. (?P<page>[1-9]\d*)|(?P<year>\d{4}) I Nr\. (?P<number>[1-9]\d*))$"
)

_ACT_LENIENT_RE = re.compile(
    r"^(?:Art(?:ikel|\.)?\s*(?P<article>\d+[a-z]?)"
    r"(?:\s*Nr\.?\s*(?P<article_number>\d+[a-z]?))?\s+)?"
    r"(?P<kind>[GVB])\.?\s*v(?:om|\.)?\s*(?P<date>\d{1,2}\.\d{1,2}\.\d{4})\s*"
    r"BGBl\.?\s*(?:I\s*S\.?\s*(?P<page>\d+)|(?P<year>\d{4})\s*I\s*Nr\.?\s*(?P<number>\d+))$",
    re.IGNORECASE,
)

#: The levels of a provision below the paragraph: name, lenient spellings, number.
_LEVELS = (
    ("Abs", r"Abs(?:atz|\.)?", r"\d+[a-z]?"),
    ("Satz", r"(?:Satz|S\.)", r"\d+"),
    ("Halbsatz", r"(?:Halbsatz|Hs\.?)", r"\d+"),
    ("Nr", r"(?:Nr\.?|Nummer)", r"\d+[a-z]*"),
    ("Buchst", r"(?:Buchst(?:abe|\.)?|lit\.?)", r"[a-z]{1,2}"),
    ("Doppelbuchst", r"(?:Doppelbuchst(?:abe|\.)?|Dbuchst\.?)", r"[a-z]{2}"),
)

_PARAGRAPH_RE = re.compile(r"^§\s*(?P<paragraph>\d+\s?[a-z]?)(?=\s)", re.IGNORECASE)

_PART_RES = tuple(
    (
        level,
        re.compile(rf"^\s+{spelling}\s*(?P<number>{number})(?=\s)", re.IGNORECASE),
    )
    for level, spelling, number in _LEVELS
)

#: Citations of more than one paragraph or part, which a provision must not contain.
_SEVERAL_RE = re.compile(
    r"^§§|\d\s*[-\u2013]\s*\d|\bff?\.|\bbis\b|\bund\b|,|\bi\.\s*V\.\s*m\.",
    re.IGNORECASE,
)

#: Where the act starts in a reference to a provision of the act itself.
_ACT_START_STRICT_RE = re.compile(
    r" (?=(?:Art\. \d+[a-z]?(?: Nr\. \d+[a-z]?)? )?"
    r"[GVB]\. v\. \d{2}\.\d{2}\.\d{4} BGBl\.)"
)

_ACT_START_LENIENT_RE = re.compile(
    r"\s(?=(?:Art(?:ikel|\.)?\s*\d+[a-z]?(?:\s*Nr\.?\s*\d+[a-z]?)?\s+)?"
    r"[GVB]\.?\s*v(?:om|\.)?\s*\d{1,2}\.\d{1,2}\.\d{4})",
    re.IGNORECASE,
)

_IDF_LENIENT_RE = re.compile(r"\s+i\.?\s*d\.?\s*F\.?(?:\s+|$)", re.IGNORECASE)


@dataclass(frozen=True)
class Provision:
    """A provision of a law, e.g., `§ 66 Abs. 1 Satz 2 EStG`.

    `law` is `None` for a provision of an act without an official abbreviation, which
    is then identified by the act of the reference.
    """

    paragraph: str
    parts: tuple[tuple[str, str], ...]
    law: str | None

    def __str__(self) -> str:
        parts = "".join(f" {_format_part(level, n)}" for level, n in self.parts)
        law = "" if self.law is None else f" {self.law}"
        return f"§ {self.paragraph}{parts}{law}"

    def covers(self, other: Provision) -> bool:
        """Whether one provision is part of the other or vice versa."""
        if (self.law, self.paragraph) != (other.law, other.paragraph):
            return False
        return all(a == b for a, b in zip(self.parts, other.parts, strict=False))


@dataclass(frozen=True)
class Act:
    """The act that gave a provision its wording, cited by its publication in the BGBl.

    Acts published until 2022 are cited by their first page (`page`), acts published
    from 2023 on by the year and number of the issue of the BGBl (`year`, `number`).
    """

    kind: ActKind
    date: datetime.date
    article: str | None = None
    article_number: str | None = None
    page: int | None = None
    year: int | None = None
    number: int | None = None

    def __str__(self) -> str:
        article = ""
        if self.article is not None:
            article = f"Art. {self.article} "
            if self.article_number is not None:
                article = f"Art. {self.article} Nr. {self.article_number} "
        bgbl = (
            f"BGBl. I S. {self.page}"
            if self.page is not None
            else f"BGBl. {self.year} I Nr. {self.number}"
        )
        return f"{article}{self.kind} v. {self.date:%d.%m.%Y} {bgbl}"

    def matches(self, other: Act) -> bool:
        """Whether `other` is this act. Articles not given in `self` match any."""
        same_act = (self.kind, self.date, self.page, self.year, self.number) == (
            other.kind,
            other.date,
            other.page,
            other.year,
            other.number,
        )
        if not same_act:
            return False
        if self.article is not None and self.article != other.article:
            return False
        return self.article_number is None or self.article_number == (
            other.article_number
        )


@dataclass(frozen=True)
class LegalReference:
    """A parsed reference or query.

    A reference always has a provision and an act. If the provision has no law, it is a
    provision of the act itself. A query may lack either of them.
    """

    provision: Provision | None
    act: Act | None

    def __str__(self) -> str:
        if self.provision is None:
            return str(self.act)
        if self.act is None:
            return str(self.provision)
        if self.provision.law is None:
            return f"{self.provision} {self.act}"
        return f"{self.provision} {IDF} {self.act}"


def _format_part(level: str, number: str) -> str:
    if level in {"Satz", "Halbsatz"}:
        return f"{level} {number}"
    return f"{level}. {number}"


def _law_key(law: str) -> str:
    """Key of a law for lenient lookup: `Estg` -> `estg`, `SGB 2` -> `sgbii`."""
    key = "".join(law.split()).lower()
    sgb = re.fullmatch(r"sgb(\d+)", key)
    if sgb:
        by_number = {v: k for k, v in _ROMAN.items()}
        n = int(sgb.group(1))
        if n in by_number:
            key = f"sgb{by_number[n].lower()}"
    return key


class GermanLegalReferenceParser:
    """Parser for references to German law, passed to `ttsim.main` by GETTSIM."""

    def __init__(self, laws: Mapping[str, str] | None = None) -> None:
        if laws is None:
            laws = yaml.safe_load(LAWS_PATH.read_text(encoding="utf-8"))
        self.laws: dict[str, str] = dict(laws)
        self._laws_by_key = {_law_key(law): law for law in self.laws}

    def parse_reference(self, reference: str) -> Hashable:
        """Parse a reference as written in the code (strict)."""
        provision, sep, act = reference.partition(f" {IDF} ")
        if sep and f" {IDF} " not in act:
            return LegalReference(
                provision=self._parse_provision(provision, strict=True),
                act=_parse_act(act, strict=True),
            )
        start = _ACT_START_STRICT_RE.search(reference)
        if not sep and reference.startswith("§") and start is not None:
            return LegalReference(
                provision=self._parse_provision(
                    reference[: start.start()], strict=True, law_required=False
                ),
                act=_parse_act(reference[start.end() :], strict=True),
            )
        raise ValueError(
            f"A reference must have the form '<provision> {IDF} <act>', or "
            "'<provision> <act>' for a provision of an act without an official "
            f"abbreviation, e.g.,\n\n"
            f"    § 66 Abs. 1 EStG {IDF} Art. 2 G. v. 08.12.2022 BGBl. I S. 2230\n"
            "    § 1 Abs. 1 V. v. 05.06.1992 BGBl. I S. 1017"
        )

    def parse_query(self, query: str) -> Hashable:
        """Parse a reference as entered by a user (lenient).

        The query may consist of a provision, an act, or both.
        """
        text = " ".join(query.split())
        if not text:
            raise ValueError("The query is empty.")
        if not text.startswith("§"):
            text = _IDF_LENIENT_RE.sub("", f" {text}", count=1).strip()
            return LegalReference(provision=None, act=_parse_act(text, strict=False))
        parts = _IDF_LENIENT_RE.split(text, maxsplit=1)
        start = _ACT_START_LENIENT_RE.search(text)
        if len(parts) == 1 and start is not None:
            return LegalReference(
                provision=self._parse_provision(
                    text[: start.start()], strict=False, law_required=False
                ),
                act=_parse_act(text[start.end() :], strict=False),
            )
        provision = self._parse_provision(parts[0], strict=False)
        act = _parse_act(parts[1], strict=False) if len(parts) > 1 else None
        return LegalReference(provision=provision, act=act)

    def matches(self, query: Hashable, reference: Hashable) -> bool:
        """Whether a parsed reference matches a parsed query.

        A query matches references to the provision and to its parts. A reference that
        is less precise than the query covers all of its parts. The act is only taken
        into account if it is part of the query.
        """
        if not isinstance(query, LegalReference) or not isinstance(
            reference, LegalReference
        ):
            return False
        if query.provision is not None and (
            reference.provision is None
            or not query.provision.covers(reference.provision)
        ):
            return False
        return query.act is None or (
            reference.act is not None and query.act.matches(reference.act)
        )

    def _parse_provision(
        self, text: str, *, strict: bool, law_required: bool = True
    ) -> Provision:
        normalized = (
            _normalize_provision_strict(text)
            if strict
            else _normalize_provision_lenient(text)
        )
        if _SEVERAL_RE.search(normalized):
            raise ValueError(
                f"Cannot parse the provision {text!r}. A provision cites a single "
                "paragraph, e.g., '§ 66 Abs. 1 Satz 2 EStG'."
            )
        paragraph, parts, law = _split_provision(
            _normalize_provision_lenient(text), law_required=law_required
        )
        if law and not law_required:
            raise ValueError(
                f"The provision {text!r} names a law ({law!r}). A provision of a law "
                f"is cited with '{IDF}', e.g., '§ 66 Abs. 1 EStG {IDF} Art. 2 G. v. "
                "08.12.2022 BGBl. I S. 2230'."
            )
        provision = Provision(
            paragraph=paragraph,
            parts=parts,
            law=self._law(law, strict=strict) if law else None,
        )
        if strict and str(provision) != normalized:
            raise ValueError(
                f"The provision {text!r} is not written in canonical form. Expected:"
                f"\n\n    {provision}"
            )
        return provision

    def _law(self, law: str, *, strict: bool) -> str:
        if law in self.laws:
            return law
        if not strict and _law_key(law) in self._laws_by_key:
            return self._laws_by_key[_law_key(law)]
        closest = difflib.get_close_matches(law, self.laws, n=3, cutoff=0.4) or (
            difflib.get_close_matches(
                _law_key(law), list(self._laws_by_key), n=3, cutoff=0.4
            )
        )
        closest = [self._laws_by_key.get(c, c) for c in closest]
        hint = (
            f" The closest abbreviations are: {', '.join(closest)}." if closest else ""
        )
        raise ValueError(
            f"Unknown law {law!r}. Laws are cited by their official abbreviation as "
            f"listed in {LAWS_PATH.name}, e.g., 'EStG' or 'SGB II'.{hint}"
        )


def _split_provision(
    text: str, *, law_required: bool
) -> tuple[str, tuple[tuple[str, str], ...], str]:
    """Split a provision into paragraph, parts and law."""
    text = f"{text} "
    m = _PARAGRAPH_RE.match(text)
    if m is None:
        raise ValueError(
            f"Cannot parse the provision {text!r}. A provision starts with the "
            "paragraph, e.g., '§ 66 Abs. 1 Satz 2 EStG'."
        )
    paragraph = "".join(m.group("paragraph").split()).lower()
    rest = text[m.end() :]
    parts: list[tuple[str, str]] = []
    while True:
        for level, regex in _PART_RES:
            part = regex.match(rest)
            if part is not None:
                parts.append((level, part.group("number").lower()))
                rest = rest[part.end() :]
                break
        else:
            break
    law = rest.strip()
    if not law and law_required:
        raise ValueError(
            f"Cannot parse the provision {text.strip()!r}. The law is missing, e.g., "
            "'§ 66 Abs. 1 EStG'."
        )
    return paragraph, tuple(parts), law


def _normalize_provision_strict(text: str) -> str:
    # Within the provision, `S.` denotes a sentence.
    return re.sub(r"(?<= )S\. (?=\d)", "Satz ", text)


def _normalize_provision_lenient(text: str) -> str:
    text = re.sub(r"^§\s*", "§ ", text)
    text = re.sub(r"\((\d+[a-z]?)\)", r"Abs. \1", text, flags=re.IGNORECASE)
    text = re.sub(r"\bS(?:atz|\.)?\s*(?=\d)", "Satz ", text)
    return " ".join(text.split())


def _parse_act(text: str, *, strict: bool) -> Act:
    regex = _ACT_STRICT_RE if strict else _ACT_LENIENT_RE
    m = regex.match(text.strip())
    if m is None:
        raise ValueError(
            f"Cannot parse the act {text!r}. Expected, e.g.,\n\n"
            "    Art. 2 G. v. 08.12.2022 BGBl. I S. 2230 (until 2022)\n"
            "    Art. 1 G. v. 23.12.2024 BGBl. 2024 I Nr. 449 (from 2023 on)"
        )
    try:
        date = datetime.datetime.strptime(m.group("date"), "%d.%m.%Y").date()  # noqa: DTZ007
    except ValueError as e:
        raise ValueError(f"Invalid date in the act {text!r}.") from e
    kind = cast("ActKind", f"{m.group('kind').upper()}.")
    act = Act(
        kind=kind,
        date=date,
        article=m.group("article").lower() if m.group("article") else None,
        article_number=(
            m.group("article_number").lower() if m.group("article_number") else None
        ),
        page=int(m.group("page")) if m.group("page") else None,
        year=int(m.group("year")) if m.group("year") else None,
        number=int(m.group("number")) if m.group("number") else None,
    )
    _validate_act(act, text)
    return act


def _validate_act(act: Act, text: str) -> None:
    if act.page is not None and act.date.year > 2022:  # noqa: PLR2004
        raise ValueError(
            f"Acts from 2023 on are cited by the number of the BGBl, e.g., "
            f"'BGBl. {act.date.year} I Nr. 449', got:\n\n    {text}"
        )
    if act.year is not None and (
        act.year < 2023 or act.year not in {act.date.year, act.date.year + 1}  # noqa: PLR2004
    ):
        raise ValueError(
            "Acts published until 2022 are cited by the page of the BGBl, e.g., "
            "'BGBl. I S. 2230', and the year of the BGBl must be the year of the act "
            f"or the following year, got:\n\n    {text}"
        )


#: The parser GETTSIM passes to TTSIM.
LEGAL_REFERENCES_PARSER = GermanLegalReferenceParser()

__all__ = [
    "LEGAL_REFERENCES_PARSER",
    "Act",
    "GermanLegalReferenceParser",
    "LegalReference",
    "Provision",
]
