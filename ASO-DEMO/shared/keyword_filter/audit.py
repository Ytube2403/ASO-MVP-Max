from dataclasses import dataclass


HARD_FILTER_COLUMNS = [
    "is_competitor",
    "is_typo",
    "is_truncated",
    "is_irrelevant",
    "is_noise",
    "is_risky_ip",
    "is_platform_risk",
    "is_platform_only",
    "is_platform_affiliation",
    "is_ambiguous_brand",
    "HardFilterRule",
    "HardFilterTerm",
    "HardFilterSource",
    "PolicyFlags",
]


@dataclass(frozen=True)
class AuditMatch:
    rule: str
    term: str = ""
    source: str = ""
    completion: str = ""

    def flag(self):
        if self.completion:
            return f"{self.rule}:{self.term}->{self.completion}"
        if self.term:
            return f"{self.rule}:{self.term}"
        return self.rule
