"""
_norm_utils.py — shared utilities for 06_data_normalization scripts.

NOT a standalone script. Import from other normalization scripts.
"""

import logging
import re
from pathlib import Path

import pandas as pd


# ── Logging ───────────────────────────────────────────────────────────────────

def setup_logging(log_dir: Path, script_name: str) -> logging.Logger:
    from datetime import datetime
    import sys
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"{script_name}_{ts}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    logger = logging.getLogger(script_name)
    logger.info(f"Log: {log_file}")
    return logger


# ── CSV loaders ───────────────────────────────────────────────────────────────

def load_input(path: Path, logger: logging.Logger) -> pd.DataFrame | None:
    """Load input CSV; return None (with warning) if missing."""
    if not path.exists():
        logger.warning(f"[SKIP] Input not found: {path}")
        return None
    try:
        df = pd.read_csv(path, dtype=str).fillna("")
        logger.info(f"Loaded: {path.name} ({len(df)} rows)")
        return df
    except Exception as exc:
        logger.error(f"Could not load {path}: {exc}")
        return None


def load_dictionary(path: Path, key_col: str,
                    logger: logging.Logger) -> dict[str, dict]:
    """
    Load a dictionary CSV and return {lowercase(raw_term): row_dict}.
    key_col is the column containing the raw/input term.
    """
    if not path.exists():
        logger.warning(f"[SKIP] Dictionary not found: {path}")
        return {}
    try:
        df = pd.read_csv(path, dtype=str).fillna("")
        mapping = {
            str(row[key_col]).strip().lower(): row.to_dict()
            for _, row in df.iterrows()
            if str(row.get(key_col, "")).strip()
        }
        logger.info(f"Dictionary: {path.name} ({len(mapping)} entries)")
        return mapping
    except Exception as exc:
        logger.warning(f"Could not load dictionary {path}: {exc}")
        return {}


# ── Term normalizer ───────────────────────────────────────────────────────────

def normalize_term(raw: str, mapping: dict[str, dict],
                   value_col: str) -> tuple[str, bool]:
    """
    Return (normalized_value, was_mapped).
    Tries: exact → lowercase → stripped lowercase.
    """
    if not raw or raw.strip() == "":
        return "", False

    raw_clean = raw.strip()

    # Exact match
    if raw_clean in mapping:
        return str(mapping[raw_clean].get(value_col, raw_clean)).strip(), True

    # Lowercase match
    raw_lower = raw_clean.lower()
    if raw_lower in mapping:
        return str(mapping[raw_lower].get(value_col, raw_clean)).strip(), True

    # Normalized (strip punctuation) lowercase match
    raw_norm = re.sub(r"[_\-\s]+", " ", raw_lower).strip()
    if raw_norm in mapping:
        return str(mapping[raw_norm].get(value_col, raw_clean)).strip(), True

    return raw_clean, False  # unmapped — return original


def normalize_column(df: pd.DataFrame, raw_col: str, norm_col: str,
                     mapping: dict[str, dict], value_col: str,
                     unmapped_collector: list[str],
                     logger: logging.Logger) -> pd.DataFrame:
    """
    Add norm_col and a <norm_col>_mapped flag column to df.
    Append unmapped terms to unmapped_collector.
    """
    df = df.copy()
    norm_values = []
    mapped_flags = []

    for raw in df[raw_col]:
        norm, mapped = normalize_term(str(raw), mapping, value_col)
        norm_values.append(norm)
        mapped_flags.append("Yes" if mapped else "No")
        if not mapped and str(raw).strip() not in ("", "unclear", "not reported"):
            unmapped_collector.append(str(raw).strip())

    df[norm_col] = norm_values
    df[f"{norm_col}_mapped"] = mapped_flags
    n_unmapped = mapped_flags.count("No")
    if n_unmapped:
        logger.info(f"  Column '{raw_col}': {n_unmapped} unmapped terms (see QA report)")
    return df


REFERENCE_TARGET_RE = re.compile(
    r"\b(16s|18s|23s|rrna|rdna|housekeeping|reference gene|recA|rpoB|gyrB)\b",
    re.IGNORECASE,
)

HOST_NON_ARG_TARGET_RE = re.compile(
    r"\b("
    r"e\.?\s*coli|escherichia coli|enterococci|enterococcus|staphylococci|"
    r"a\.?\s*baumannii|p\.?\s*aeruginosa|pseudomonas|bacteroides|nitrospira|"
    r"uidA|bacteria|bacterial|total bacteria|"
    r"fecal|crassphage|hf183|bacr287|host|arb|arbs|hpc|cod|nh4|"
    r"chemical|antibiotic|sulfamethoxazole|smx|dna concentration|total dna|"
    r"mag(?:s)?|pathogen|indicator"
    r")\b",
    re.IGNORECASE,
)

AGGREGATE_ARG_TARGET_RE = re.compile(
    r"\b("
    r"total|all|overall|sum|combined|cumulative|aggregate|aggregated|"
    r"abundance|diversity|richness|frequency|detected|types?|subtypes?|"
    r"resistome|mobilome|argome|args?|antibiotic resistance genes?"
    r")\b",
    re.IGNORECASE,
)

CLASS_OR_GROUP_TARGET_RE = re.compile(
    r"\b("
    r"tet genes?|tet[- ]?args?|tetracycline(?: resistance)? genes?|tetracyclines?|"
    r"sul genes?|sul[- ]?args?|sulfonamide(?: resistance)? genes?|sulfonamides?|"
    r"erm genes?|mls(?: resistance)? genes?|macrolide(?: resistance)? genes?|"
    r"bla genes?|beta[- ]?lactam(?:ase)?(?: resistance)? genes?|beta[- ]?lactamase genes?|"
    r"qnr genes?|quinolone(?: resistance)? genes?|quinolones?|"
    r"aminoglycoside(?: resistance)? genes?|vancomycin(?: resistance)? genes?|"
    r"multidrug(?: resistance)? genes?|mdrgs?|mrgs?|bmrg(?:s)?|"
    r"class(?:es)?|famil(?:y|ies)|panel|selected genes|target genes|typical args?"
    r")\b",
    re.IGNORECASE,
)

MGE_TARGET_RE = re.compile(
    r"\b("
    r"intI?[123]|intl1|integron|integrase|iscr\d*|is\d+|tnpA|transposon|"
    r"plasmids?|inc[A-Z0-9]+|pB10|korB|mge(?:s)?|mobile genetic elements?"
    r")\b",
    re.IGNORECASE,
)

MULTI_TARGET_SCOPE_RE = re.compile(
    r"[,;]|\s+(?:and|or)\s+|\+|_to_|\bincluding\b|\bmultiple\b|\bseveral\b",
    re.IGNORECASE,
)

GENE_SPECIFIC_TARGET_RE = re.compile(
    r"^(?:"
    r"sul\s*(?:i{1,3}|[123])|"
    r"tet(?:\([A-Za-z0-9-]+\)|[A-Za-z]{1,3}\d*(?:-\d+)?|\d{1,3})|"
    r"erm(?:\([A-Za-z0-9-]+\)|[A-Za-z0-9-]+)|"
    r"mef[A-Za-z0-9-]*|mph(?:\([A-Za-z0-9-]+\)|[A-Za-z0-9-]+)|ere[A-Za-z0-9-]*|"
    r"bla[A-Za-z0-9-]+|(?:TEM|SHV|OXA|KPC|VIM|IMP|NDM|GES|CTX-M|CMY|ampC|cfxA|cepA|bexA|mecA)[A-Za-z0-9-]*|"
    r"qnr[A-Za-z0-9-]*|qepA|oqx[AB]|"
    r"dfrA[A-Za-z0-9-]*|"
    r"aac(?:\([^)]+\))?[A-Za-z0-9'_-]*(?:-Ib-cr)?|aph(?:\([^)]+\))?[A-Za-z0-9'_-]*|aadA[A-Za-z0-9-]*|nptII|"
    r"van[A-Za-z0-9-]*|mcr-[0-9]+|"
    r"mex[A-Za-z0-9-]*|acrB|macB|bacA|linA|qacE|fabI|cmlA|floR|optrA|cfr"
    r")$",
    re.IGNORECASE,
)


def _target_text(row: pd.Series) -> tuple[str, str, str, str]:
    raw = str(row.get("raw_target_name", row.get("target_name", ""))).strip()
    normalized = str(row.get("normalized_target_name", "")).strip()
    target_type = str(row.get("normalized_target_type", row.get("target_type", ""))).strip()
    arg_class = str(row.get("normalized_arg_class", "")).strip()
    return raw, normalized, target_type, arg_class


def classify_target_scope(row: pd.Series) -> tuple[str, str, str, str]:
    """
    Return (target_scope, target_eligibility_for_quant, source, note).

    This classifies the biological scope of a target independently from
    dictionary mapping success. Aggregate/group/reference/host terms are kept
    out of gene-level quantitative cohorts even when their wording resembles an
    ARG family.
    """
    raw, normalized, target_type, arg_class = _target_text(row)
    text = " ".join([raw, normalized, target_type, arg_class]).strip()
    lower_raw = raw.lower()
    lower_text = text.lower()
    mapped = str(row.get("normalized_target_name_mapped", "")).strip() == "Yes"

    if not raw:
        return "unknown", "No", "rule_missing", "blank target"

    if target_type in {"reference_gene"} or REFERENCE_TARGET_RE.search(text):
        # Ratios such as sul1/16S still contain a true ARG/MGE target; classify
        # them before the reference-gene fallback if the left-hand side is clear.
        left = re.split(r"/| normalized to | per ", raw, maxsplit=1, flags=re.IGNORECASE)[0].strip()
        if left and (GENE_SPECIFIC_TARGET_RE.fullmatch(left) or MGE_TARGET_RE.search(left)):
            scope = "mge_marker" if MGE_TARGET_RE.search(left) else "gene_specific"
            eligibility = "Yes"
            return scope, eligibility, "rule_ratio_left_target", "target normalized to reference gene"
        return "reference_gene", "No", "dictionary_or_rule_reference", "reference/housekeeping target"

    if target_type in {"MGE", "intI1_marker"}:
        return "mge_marker", "Yes", "dictionary_target_type", target_type

    if target_type in {"resistome"}:
        return "aggregate_ARG", "separate_cohort", "dictionary_target_type", target_type

    if (
        MULTI_TARGET_SCOPE_RE.search(raw)
        or raw.count("/") >= 2
        or re.search(
            r"\b(?:sul|tet|bla|erm|qnr|intI|intl|aac|aph|dfr|qac)[^/]+/"
            r"(?:sul|tet|bla|erm|qnr|intI|intl|aac|aph|dfr|qac)",
            raw,
            re.IGNORECASE,
        )
    ):
        return "class_or_group", "separate_cohort", "rule_multi_target", "multiple targets or combined gene list"

    if MGE_TARGET_RE.search(text):
        if re.search(r"\b(total|all|overall|combined|sum|aggregate|mges?|mobile genetic elements?|plasmids?|integrons?)\b", lower_text) and not re.search(r"\b(intI?[123]|intl1|iscr\d*|is\d+|tnpA|inc[A-Z0-9]+|pB10|korB)\b", text, re.IGNORECASE):
            return "class_or_group", "separate_cohort", "rule_mge_group", "MGE/plasmid/integron group"
        return "mge_marker", "Yes", "rule_mge_marker", "specific MGE marker pattern"

    if HOST_NON_ARG_TARGET_RE.search(text):
        return "host_or_non_ARG", "No", "rule_host_non_arg", "host/taxon/chemical/non-ARG target"

    if AGGREGATE_ARG_TARGET_RE.search(text):
        if GENE_SPECIFIC_TARGET_RE.fullmatch(raw) or (mapped and target_type == "ARG"):
            return "gene_specific", "Yes", "dictionary_or_rule_gene", "specific gene despite aggregate-looking class"
        return "aggregate_ARG", "separate_cohort", "rule_aggregate_arg", "aggregate ARG/resistome wording"

    if CLASS_OR_GROUP_TARGET_RE.search(text):
        if GENE_SPECIFIC_TARGET_RE.fullmatch(raw) or (mapped and target_type == "ARG"):
            return "gene_specific", "Yes", "dictionary_or_rule_gene", "specific gene despite family-looking prefix"
        return "class_or_group", "separate_cohort", "rule_class_or_group", "ARG family/class/group wording"

    if target_type == "ARG" or (mapped and arg_class and arg_class not in {"reference gene", "resistome"}):
        return "gene_specific", "Yes", "dictionary_target_type", target_type or arg_class

    ratio_left = re.split(r"/| normalized to | per ", raw, maxsplit=1, flags=re.IGNORECASE)[0].strip()
    if ratio_left and ratio_left != raw and GENE_SPECIFIC_TARGET_RE.fullmatch(ratio_left):
        return "gene_specific", "Yes", "rule_ratio_left_target", "specific gene normalized to denominator"

    cleaned = re.sub(r"\s+", "", raw)
    if GENE_SPECIFIC_TARGET_RE.fullmatch(cleaned) or GENE_SPECIFIC_TARGET_RE.fullmatch(raw):
        return "gene_specific", "Yes", "rule_gene_pattern", "specific ARG-family gene pattern"

    return "unknown", "No", "rule_unresolved", "target not safely classifiable"


def add_target_scope_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add target_scope, target_eligibility_for_quant, and trace columns."""
    df = df.copy()
    scopes = []
    eligibilities = []
    sources = []
    notes = []
    for _, row in df.iterrows():
        scope, eligibility, source, note = classify_target_scope(row)
        scopes.append(scope)
        eligibilities.append(eligibility)
        sources.append(source)
        notes.append(note)
    df["target_scope"] = scopes
    df["target_eligibility_for_quant"] = eligibilities
    df["target_scope_source"] = sources
    df["target_scope_note"] = notes
    return df


MATRIX_FRACTION_RE = re.compile(
    r"\b("
    r"exdna|e[- ]?dna|extracellular(?: dna| arg| args)?|"
    r"idna|i[- ]?dna|intracellular(?: dna| arg| args)?|"
    r"cell[- ]?free|cf[- ]?dna|cell[- ]?associated|particle[- ]?associated|total"
    r")\b",
    re.IGNORECASE,
)

SITE_LABEL_RE = re.compile(
    r"\b("
    r"wwtp\s*[A-Za-z0-9-]*|wrrf\s*[A-Za-z0-9-]*|plant\s*[A-Za-z0-9-]*|"
    r"hospital|municipal|urban|rural|industrial|lab(?:oratory)?|pilot|"
    r"site\s*[A-Za-z0-9-]*|sampling site\s*[A-Za-z0-9-]*|reactor\s*[A-Za-z0-9-]*|"
    r"system\s*[A-Za-z0-9-]*|train\s*[A-Za-z0-9-]*"
    r")\b",
    re.IGNORECASE,
)

STAGE_TIMEPOINT_RE = re.compile(
    r"\b("
    r"day\s*\d+|d\s*\d+|t\s*[-]?\s*\d+\s*h?|h\s*\d+|"
    r"before|after|pre[- ]?|post[- ]?|baseline|"
    r"after\s+[A-Za-z0-9-]+|before\s+[A-Za-z0-9-]+|"
    r"uv|chlorination|ozone|anaerobic|aerobic|oxic|anoxic|hrt|srt|"
    r"summer|winter|spring|autumn|fall"
    r")\b",
    re.IGNORECASE,
)

MATRIX_KEYWORDS: list[tuple[str, str]] = [
    (r"\b(raw wastewater|raw sewage|wastewater influent|untreated wastewater|influent)\b", "influent"),
    (r"\b(primary effluent|settled wastewater)\b", "primary_effluent"),
    (r"\b(secondary effluent|biological effluent|biologically treated effluent)\b", "secondary_effluent"),
    (r"\b(tertiary effluent)\b", "tertiary_effluent"),
    (r"\b(final effluent|treated effluent|final treated wastewater|treated wastewater|"
     r"wwtp effluent|wwtp effluents|plant effluent|wastewater effluent|final filtrate|effluent)\b", "final_effluent"),
    (r"\b(reclaimed water|recycled water|reuse water)\b", "reclaimed_water"),
    (r"\b(activated sludge|mixed liquor suspended solids|mixed liquor|mlss)\b", "activated_sludge"),
    (r"\b(cas system|conventional activated sludge)\b", "activated_sludge"),
    (r"\b(waste activated sludge|was|excess sludge|wasted sludge|surplus sludge|surplus activated sludge)\b", "waste_activated_sludge"),
    (r"\b(anaerobically digested sludge|anaerobic sludge|digested sludge)\b", "anaerobic_sludge"),
    (r"\b(digestate|anaerobic digestate|digested samples?(?: at end of ad)?)\b", "digestate"),
    (r"\b(composted sludge|biosolids)\b", "biosolids"),
    (r"\b(biofilm)\b", "biofilm"),
    (r"\b(vermicompost)\b", "vermicompost"),
    (r"\b(composted swine manure|composted manure)\b", "composted_manure"),
    (r"\b(fresh swine manure|swine manure|animal manure)\b", "animal_manure"),
    (r"\b(dewatered sludge|sewage sludge|wwtp sludge|primary sludge|sludge)\b", "sewage_sludge"),
    (r"\b(bioaerosol|aerosol)\b", "bioaerosol"),
    (r"\b(receiving water upstream|upstream water|river upstream)\b", "receiving_water_upstream"),
    (r"\b(receiving water downstream|downstream water|river downstream|downstream reservoirs?|surface water|receiving water)\b", "receiving_water_downstream"),
]


def _matrix_fraction_from_text(text: str) -> str:
    lower = text.lower()
    if re.search(r"\b(exdna|e[- ]?dna|extracellular|cell[- ]?free|cfdna)\b", lower):
        return "eDNA"
    if re.search(r"\b(idna|i[- ]?dna|intracellular|cell[- ]?associated|particle[- ]?associated)\b", lower):
        return "iDNA"
    if re.search(r"\b(total)\b", lower):
        return "total"
    return ""


def _first_match(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    return match.group(0).strip() if match else ""


def _matrix_from_text(text: str, matrix_map: dict[str, dict]) -> tuple[str, str]:
    clean = str(text or "").strip()
    if not clean:
        return "", "no_matrix_text"
    direct = matrix_map.get(clean.lower(), {})
    if direct:
        return str(direct.get("normalized_matrix", "")).strip(), "dictionary_exact"
    normalized_clean = re.sub(r"[_/-]+", " ", clean).strip().lower()
    direct = matrix_map.get(normalized_clean, {})
    if direct:
        return str(direct.get("normalized_matrix", "")).strip(), "dictionary_normalized"
    for pattern, normalized in MATRIX_KEYWORDS:
        if re.search(pattern, clean, re.IGNORECASE):
            return normalized, "keyword_matrix"
    return "", "no_matrix_keyword"


def parse_matrix_context_value(raw_value: str, matrix_map: dict[str, dict]) -> dict[str, str]:
    """Parse one raw matrix/context string into orthogonal components."""
    text = str(raw_value or "").strip()
    normalized_matrix, _signal = _matrix_from_text(text, matrix_map)
    fraction = _matrix_fraction_from_text(text)
    site = _first_match(SITE_LABEL_RE, text)
    stage = _first_match(STAGE_TIMEPOINT_RE, text)
    if normalized_matrix:
        confidence = "parsed_matrix_found"
    elif fraction or site or stage:
        confidence = "context_only_no_matrix"
    else:
        confidence = "no_context_found"
    return {
        "normalized_matrix": normalized_matrix,
        "matrix_fraction": fraction,
        "site_or_system_label": site,
        "stage_or_timepoint": stage,
        "matrix_parse_confidence": confidence,
    }


def _choose_matrix_context_source(row: pd.Series, fallback_cols: list[str]) -> tuple[str, str]:
    raw_label = str(row.get("raw_matrix_label", "")).strip()
    raw_conf = str(row.get("matrix_label_backfill_confidence", "")).strip()
    if raw_label and raw_conf not in {"not_applicable_existing_legacy", "ambiguous_left_blank", "no_source_found"}:
        return raw_label, "raw_matrix_label"
    for col in fallback_cols:
        value = str(row.get(col, "")).strip()
        if value:
            return value, col
    return "", "no_matrix_source"


def add_measurement_matrix_context(df: pd.DataFrame, matrix_map: dict[str, dict]) -> pd.DataFrame:
    """Add parser context columns for measurement matrix values."""
    df = df.copy()
    values: list[dict[str, str]] = []
    sources: list[str] = []
    for _, row in df.iterrows():
        raw_value, source = _choose_matrix_context_source(row, ["matrix", "raw_matrix"])
        parsed = parse_matrix_context_value(raw_value, matrix_map)
        values.append(parsed)
        sources.append(source)
    df["normalized_matrix"] = [v["normalized_matrix"] for v in values]
    df["matrix_fraction"] = [v["matrix_fraction"] for v in values]
    df["site_or_system_label"] = [v["site_or_system_label"] for v in values]
    df["stage_or_timepoint"] = [v["stage_or_timepoint"] for v in values]
    df["matrix_parse_source"] = sources
    df["matrix_parse_confidence"] = [v["matrix_parse_confidence"] for v in values]
    return df


def add_outcome_matrix_context(df: pd.DataFrame, matrix_map: dict[str, dict]) -> pd.DataFrame:
    """Add parser context columns for outcome matrix_before/matrix_after values."""
    df = df.copy()
    main_values: list[dict[str, str]] = []
    main_sources: list[str] = []
    for _, row in df.iterrows():
        main_raw, main_source = _choose_matrix_context_source(
            row, ["matrix_after", "raw_matrix_after", "matrix_before", "raw_matrix_before"]
        )
        main_values.append(parse_matrix_context_value(main_raw, matrix_map))
        main_sources.append(main_source)

    df["normalized_matrix"] = [v["normalized_matrix"] for v in main_values]
    df["matrix_fraction"] = [v["matrix_fraction"] for v in main_values]
    df["site_or_system_label"] = [v["site_or_system_label"] for v in main_values]
    df["stage_or_timepoint"] = [v["stage_or_timepoint"] for v in main_values]
    df["matrix_parse_source"] = main_sources
    df["matrix_parse_confidence"] = [v["matrix_parse_confidence"] for v in main_values]
    return df


MATRIX_TRANSITION_TREATMENT_RE = re.compile(
    r"\b("
    r"treat(?:ed|ment)?|chlorinat(?:ed|ion)?|uv|ultraviolet|gamma|irradiat(?:ed|ion)?|"
    r"ozon(?:e|ated|ation)|o3|h2o2|hydrogen peroxide|persulfate|peroxymonosulfate|"
    r"\bps\b|pms|balo|compost(?:ed|ing)?|pretreat(?:ed|ment)?|digestion|digester|"
    r"biolysis|free ammonia|\bfa\b|zvi|zero[- ]valent iron|additive|ct value|"
    r"dose|dosage|contact time|filtrat(?:e|ion)|membrane|nanofiltration|microfiltration|"
    r"coagulat(?:ed|ion)?|disinfect(?:ed|ion)?|advanced oxidation|aop|"
    r"electro(?:chemical|coagulation)|photocatal(?:ysis|ytic)|fenton|starvation"
    r")\b",
    re.IGNORECASE,
)

MATRIX_TRANSITION_TEMPORAL_RE = re.compile(
    r"\b("
    r"day\s*\d+|d\s*\d+|t\s*[-]?\s*\d+\s*h?|"
    r"\d+\s*(?:min|h|hr|hrs|hour|hours|d|day|days)|"
    r"after\s+\d+\s*(?:min|h|hr|hrs|hour|hours|d|day|days)|"
    r"over\s+\d+\s*(?:d|day|days)|during the first|period of cultivation|"
    r"baseline|before|after|pre[- ]|post[- ]|time[- ]?point|incubation"
    r")\b",
    re.IGNORECASE,
)


def _matrix_transition_is_clear(value: str) -> bool:
    return str(value or "").strip().lower() not in {
        "",
        "unclear",
        "other",
        "unknown",
        "not_reported",
        "not applicable",
        "not_applicable",
        "nan",
        "none",
    }


def _classify_matrix_transition(
    before_class: str,
    after_class: str,
    evidence_text: str,
) -> tuple[str, str, str]:
    before = str(before_class or "").strip()
    after = str(after_class or "").strip()
    before_clear = _matrix_transition_is_clear(before)
    after_clear = _matrix_transition_is_clear(after)
    if not before_clear or not after_clear:
        return (
            "ambiguous",
            "missing_or_unclear_matrix_class",
            "matrix_before and matrix_after could not both be parsed to clear matrix classes",
        )

    if before != after:
        return (
            "cross_stage_route",
            "before_after_matrix_classes_differ",
            f"parsed matrix transition: {before} -> {after}",
        )

    if MATRIX_TRANSITION_TREATMENT_RE.search(evidence_text):
        return (
            "within_matrix_treatment",
            "same_matrix_with_treatment_signal",
            "same matrix class, but evidence/treatment fields indicate treatment/control/dose/contact-time contrast",
        )

    if MATRIX_TRANSITION_TEMPORAL_RE.search(evidence_text):
        return (
            "within_matrix_temporal",
            "same_matrix_with_temporal_signal",
            "same matrix class with temporal signal and no explicit treatment signal",
        )

    return (
        "ambiguous",
        "same_matrix_without_treatment_or_temporal_signal",
        "same matrix class, but available fields do not distinguish treatment effect from temporal/other contrast",
    )


def add_matrix_transition_type(df: pd.DataFrame, matrix_map: dict[str, dict]) -> pd.DataFrame:
    """Classify outcome matrix transitions for removal-route analyses."""
    df = df.copy()
    before_classes: list[str] = []
    after_classes: list[str] = []
    transition_types: list[str] = []
    signals: list[str] = []
    notes: list[str] = []

    context_cols = [
        "treatment_process",
        "raw_treatment_process",
        "normalized_treatment_process",
        "treatment_group",
        "outcome_type",
        "raw_outcome_type",
        "normalized_outcome_type",
        "pairing_basis",
        "paired_data_status",
        "normalized_paired_data_status",
        "interpretation",
        "evidence_quote",
        "extraction_note",
        "raw_stage_label",
    ]

    for _, row in df.iterrows():
        before_raw = str(row.get("matrix_before", row.get("raw_matrix_before", ""))).strip()
        after_raw = str(row.get("matrix_after", row.get("raw_matrix_after", ""))).strip()
        before_parsed = parse_matrix_context_value(before_raw, matrix_map)
        after_parsed = parse_matrix_context_value(after_raw, matrix_map)
        before_class = before_parsed["normalized_matrix"]
        after_class = after_parsed["normalized_matrix"]
        evidence_text = " | ".join(str(row.get(col, "")).strip() for col in context_cols)
        transition_type, signal, note = _classify_matrix_transition(
            before_class,
            after_class,
            evidence_text,
        )
        before_classes.append(before_class)
        after_classes.append(after_class)
        transition_types.append(transition_type)
        signals.append(signal)
        notes.append(note)

    df["matrix_transition_type"] = transition_types
    df["matrix_transition_before_class"] = before_classes
    df["matrix_transition_after_class"] = after_classes
    df["matrix_transition_signal"] = signals
    df["matrix_transition_note"] = notes
    return df


LOG_LIKE_UNIT_RE = re.compile(
    r"\b("
    r"log10|log[- ]?units?|log[- ]?unit|log scale|logs decrease|log decrease|"
    r"log10 copies/100 ?m[lL]|orders? of magnitude|lrv"
    r")\b|(?:^|\s)-log(?:\s|$)",
    re.IGNORECASE,
)

LOG_REMOVAL_EVIDENCE_RE = re.compile(
    r"\b("
    r"log(?:10)?\s+reduction|log[- ]?units?\s+removal|"
    r"reduction(?:s)?|reduced|decrease(?:d|s)?|removal|removed|"
    r"lrv|orders? of magnitude|inactivation|eliminat(?:ed|ion)|"
    r"difference between .* sample sets"
    r")\b",
    re.IGNORECASE,
)

LOG_ENRICHMENT_EVIDENCE_RE = re.compile(
    r"\b("
    r"increase(?:d|s)?|enrichment|enriched|negative log reduction|"
    r"negative\s+(?:value|log|lrv|removal)"
    r")\b",
    re.IGNORECASE,
)


def _single_numeric_float(value: str) -> float | None:
    text = _clean_numeric_text(value)
    if not text or not _is_single_numeric_value(text):
        return None
    try:
        return float(re.sub(r"^[<>=~ ]+", "", text))
    except ValueError:
        return None


def _log_harmonization_context(row: pd.Series) -> str:
    fields = [
        "evidence_quote",
        "interpretation",
        "pairing_basis",
        "extraction_note",
        "reported_outcome_unit",
        "raw_reported_outcome_unit",
        "normalized_outcome_unit",
    ]
    return " | ".join(str(row.get(field, "")).strip() for field in fields if str(row.get(field, "")).strip())


def _is_log_like_alias(row: pd.Series) -> bool:
    unit_text = " ".join([
        str(row.get("reported_outcome_unit", "")),
        str(row.get("raw_reported_outcome_unit", "")),
        str(row.get("normalized_outcome_unit", "")),
    ]).strip().lower()
    if str(row.get("outcome_unit_family", "")).strip() == "log_reduction":
        return False
    if str(row.get("normalized_outcome_unit", "")).strip() == "log_reduction":
        return False
    return bool(LOG_LIKE_UNIT_RE.search(unit_text))


def add_log_reduction_harmonization(df: pd.DataFrame) -> pd.DataFrame:
    """
    Harmonize safe log-reduction aliases and route negative log reductions.

    This intentionally uses row context/evidence rather than dictionary-only
    mapping because log-like unit strings can encode either reduction or
    enrichment depending on direction.
    """
    df = df.copy()
    statuses: list[str] = []
    notes: list[str] = []
    directions: list[str] = []
    removed_flags: list[str] = []
    exclusion_notes: list[str] = []

    for idx, row in df.iterrows():
        status = "not_applicable"
        note = ""
        direction = ""
        removed = "No"
        exclusion_note = ""
        context = _log_harmonization_context(row)
        value = _single_numeric_float(str(row.get("reported_outcome_value", "")))
        unit_family = str(row.get("outcome_unit_family", "")).strip()
        norm_unit = str(row.get("normalized_outcome_unit", "")).strip()
        norm_type = str(row.get("normalized_outcome_type", "")).strip()

        is_log_removal_metric = (
            unit_family == "log_reduction"
            or norm_unit == "log_reduction"
            or norm_type == "log_reduction"
        )
        if value is not None and value < 0 and is_log_removal_metric:
            status = "routed_enrichment_negative_log_reduction"
            note = "negative log reduction means abundance increased through treatment; excluded from removal pool"
            direction = "enrichment"
            removed = "Yes"
            exclusion_note = "negative log reduction routed to enrichment cohort"
            df.at[idx, "normalized_outcome_type"] = "enrichment"
            df.at[idx, "outcome_group"] = "quantitative_enrichment"
        elif _is_log_like_alias(row):
            has_removal = bool(LOG_REMOVAL_EVIDENCE_RE.search(context))
            has_enrichment = bool(LOG_ENRICHMENT_EVIDENCE_RE.search(context))
            if has_enrichment and not has_removal:
                status = "routed_enrichment_log_like"
                note = "log-like unit has explicit increase/enrichment direction; excluded from removal pool"
                direction = "enrichment"
                removed = "Yes"
                exclusion_note = "log-like unit indicates enrichment/increase"
                df.at[idx, "normalized_outcome_type"] = "enrichment"
                df.at[idx, "outcome_group"] = "quantitative_enrichment"
            elif has_removal and not has_enrichment:
                status = "harmonized_log_reduction"
                note = "log-like alias has explicit reduction/removal/decrease/LRV evidence; unit harmonized to log_reduction"
                direction = "removal"
                df.at[idx, "normalized_outcome_unit"] = "log_reduction"
                df.at[idx, "outcome_unit_family"] = "log_reduction"
                if "normalized_outcome_unit_mapped" in df.columns:
                    df.at[idx, "normalized_outcome_unit_mapped"] = "Yes_harmonized"
            elif has_removal and has_enrichment:
                status = "needs_harmonization_conflicting_direction"
                note = "both removal and enrichment cues present; kept out of harmonized log-reduction pool"
            else:
                status = "needs_harmonization_unclear_direction"
                note = "log-like alias lacks clear reduction/removal/decrease/LRV evidence in source fields"

        statuses.append(status)
        notes.append(note)
        directions.append(direction)
        removed_flags.append(removed)
        exclusion_notes.append(exclusion_note)

    df["log_harmonization_status"] = statuses
    df["log_harmonization_note"] = notes
    df["outcome_direction"] = directions
    df["removed_from_removal_pool"] = removed_flags
    df["removal_pool_exclusion_note"] = exclusion_notes
    return df


def pre_normalize_unit_name(raw: str, context: str = "") -> tuple[str, str]:
    """
    Return (pre_normalized_unit_name, note) before dictionary lookup.

    This harmonizes spelling and notation only. It intentionally does not
    normalize units that require changing the numeric basis (for example
    copies/100 mL or copies/uL), because numeric values are not converted here.
    """
    if not raw or raw.strip() == "":
        return "", ""

    original = raw.strip()
    value = original
    value = value.replace("−", "-").replace("–", "-").replace("—", "-")
    value = value.replace("µ", "u").replace("μ", "u")
    value = re.sub(r"\s+", " ", value).strip()
    lower = value.lower()

    def changed(canonical: str, note: str) -> tuple[str, str]:
        if canonical == original:
            return canonical, ""
        return canonical, note

    # Refuse risky cases where name normalization would change numeric meaning
    # or collapse incompatible bases. These are routed for later handling.
    if re.search(r"(?:x|×)\s*10\s*(?:\^|[-+])?\s*[-+]?\d+", lower) or re.search(r"\b10\s*\^\s*-\s*\d+", lower):
        return original, "unit_contains_multiplier: not pre-normalized"
    if "%" in lower and "relative abundance" in lower:
        return original, "unclear_percent_relative_abundance: not pre-normalized"
    if re.search(r"copies?.*(?:/|per|\s)m\s*l", lower) and re.search(r"\bor\b|/|\bg\s+sludge\b|\bg\s+dry\b", lower) and re.search(r"\bg\b|sludge|solid", lower):
        return original, "unclear_mixed_denominator: not pre-normalized"

    # Detection-status wording.
    if re.fullmatch(r"(presence\s*/\s*absence|presence absence|presence-absence)", lower):
        return changed("detected", "unit pre-normalized: qualitative presence/absence -> detected")
    if re.fullmatch(r"(detected|not detected|nd)", lower):
        return changed(value, "")

    # Percent/removal variants already represented by '%' in the dictionary.
    if re.fullmatch(r"(percent|percentage|%)", lower):
        return changed("%", "unit pre-normalized: percent spelling -> %")
    if re.fullmatch(r"%\s*(change|reduction|removal|decrease|increase)", lower):
        return changed("%", "unit pre-normalized: percent outcome variant -> %")
    if re.fullmatch(r"(percent|percentage)\s+(change|reduction|removal|decrease|increase)", lower):
        return changed("%", "unit pre-normalized: percent outcome variant -> %")

    # Log-reduction/outcome variants. Bare 'log' is only safe for outcomes.
    if re.fullmatch(r"log10?\s*(reduction|removal)|log\s*(reduction|removal)", lower):
        return changed("log reduction", "unit pre-normalized: log removal/reduction variant -> log reduction")
    if context == "outcome" and re.fullmatch(r"(log|logs|log unit|log units|orders of magnitude)", lower):
        return changed("log reduction", "unit pre-normalized: outcome log shorthand -> log reduction")

    # Relative abundance / 16S variants.
    if "relative abundance" in lower and re.search(r"\b16s\b|rrna|rdna", lower):
        return changed("relative abundance/16S", "unit pre-normalized: relative abundance 16S variant -> relative abundance/16S")
    has_log_prefix = bool(re.search(r"\blog\s*10\b|\blog10\b|\blog\s*[\[(]", lower) or lower.startswith("log "))
    if has_log_prefix and re.search(r"\b16s\b|rrna|rdna", lower):
        return original, ""
    if re.search(r"(gene\s+)?copies\s*(per|/)\s*(copy of )?16s", lower):
        return changed("copies/16S", "unit pre-normalized: copies per 16S variant -> copies/16S")
    if re.search(r"arg copies\s*/\s*16s|arg copies\s+per\s+16s", lower):
        return changed("copies/16S", "unit pre-normalized: ARG copies per 16S variant -> copies/16S")

    # Log abundance variants with the same denominator; no numeric conversion.
    per_100_ml = bool(re.search(r"\b100\s*m\s*l\b|/100\s*m\s*l|per\s+100\s*m\s*l", lower))
    if has_log_prefix:
        if re.search(r"(copies|copy|cell equivalents?|ce).*(/|per|\s)m\s*l\b", lower) or re.search(r"(copies|copy|cell equivalents?|ce).*m\s*l\^-?1|(copies|copy|cell equivalents?|ce).*m\s*l-1", lower):
            if not per_100_ml:
                return changed("log copies/mL", "unit pre-normalized: log copies per mL variant -> log copies/mL")
        if re.search(r"(copies|copy|cell equivalents?|ce).*(/|per|\s)l\b", lower) or re.search(r"(copies|copy|cell equivalents?|ce).*\bl\^-?1|(copies|copy|cell equivalents?|ce).*\bl-1", lower):
            return changed("log copies/L", "unit pre-normalized: log copies per L variant -> log copies/L")
        if re.search(r"(copies|copy|cell equivalents?|ce).*(/|per|\s)g\b", lower) or re.search(r"(copies|copy|cell equivalents?|ce).*\bg\^-?1|(copies|copy|cell equivalents?|ce).*\bg-1", lower):
            if re.search(r"\b(vss|volatile suspended solids)\b", lower):
                return changed("log copies/g VSS", "unit pre-normalized: log copies per g VSS variant -> log copies/g VSS")
            if re.search(r"\b(vs|volatile solids)\b", lower):
                return changed("log copies/g VS", "unit pre-normalized: log copies per g VS variant -> log copies/g VS")
            if re.search(r"\b(ts|total solids)\b", lower):
                return changed("log copies/g TS", "unit pre-normalized: log copies per g TS variant -> log copies/g TS")
            if re.search(r"\b(ds|dry sludge)\b", lower):
                return changed("log copies/g DS", "unit pre-normalized: log copies per g DS variant -> log copies/g DS")
            if re.search(r"\b(dw|dry weight)\b", lower):
                return changed("log copies/g DW", "unit pre-normalized: log copies per g DW variant -> log copies/g DW")
            if re.search(r"\b(wet soil|wet sludge|sediment|soil|sludge)\b", lower):
                return original, "unclear_solid_basis: not pre-normalized"
            return changed("log copies/g", "unit pre-normalized: log copies per g variant -> log copies/g")

    # Absolute abundance notation variants with the same denominator.
    if re.search(r"(gene\s+)?copies?\s*(/|per|\s)m\s*l\b", lower) or re.search(r"copy number\s*/\s*m\s*l", lower) or re.search(r"(gene\s+)?copies?.*m\s*l\^-?1|(gene\s+)?copies?.*m\s*l-1", lower):
        if not per_100_ml:
            return changed("copies/mL", "unit pre-normalized: copies per mL variant -> copies/mL")
    if re.search(r"(gene\s+)?copies?\s*(/|per|\s)l\b", lower) or re.search(r"(gene\s+)?copies?.*\bl\^-?1|(gene\s+)?copies?.*\bl-1", lower):
        return changed("copies/L", "unit pre-normalized: copies per L variant -> copies/L")
    if re.search(r"(gene\s+)?copies?\s*(/|per|\s)g\b", lower) or re.search(r"(gene\s+)?copies?.*\bg\^-?1|(gene\s+)?copies?.*\bg-1", lower):
        if re.search(r"\b(vss|volatile suspended solids)\b", lower):
            return changed("copies/g VSS", "unit pre-normalized: copies per gram VSS variant -> copies/g VSS")
        if re.search(r"\b(ds|dry sludge)\b", lower):
            return changed("copies/g DS", "unit pre-normalized: copies per gram dry-sludge variant -> copies/g DS")
        if re.search(r"\b(dw|dry weight)\b", lower):
            return changed("copies/g DW", "unit pre-normalized: copies per gram dry-weight variant -> copies/g DW")
        if re.search(r"\b(ts|total solids)\b", lower):
            return changed("copies/g TS", "unit pre-normalized: copies per gram total-solids variant -> copies/g TS")
        if re.search(r"\b(vs|vss|volatile solids)\b", lower):
            return changed("copies/g VS", "unit pre-normalized: copies per gram volatile-solids variant -> copies/g VS")
        if re.search(r"\b(ss|suspended solids)\b", lower):
            return changed("copies/g SS", "unit pre-normalized: copies per gram suspended-solids variant -> copies/g SS")
        if re.search(r"\b(wet soil|wet sludge|sediment|soil|sludge)\b", lower):
            return original, "unclear_solid_basis: not pre-normalized"
        return changed("copies/g", "unit pre-normalized: copies per g variant -> copies/g")
    if re.search(r"(gene\s+)?copies?\s*(/|per|\s)m3\b", lower) or re.search(r"(gene\s+)?copies?.*m\^-?3|(gene\s+)?copies?.*m-3", lower):
        return changed("copies/m3", "unit pre-normalized: copies per m3 variant -> copies/m3")

    return original, ""


def normalize_unit_column(df: pd.DataFrame, raw_col: str, norm_col: str,
                          mapping: dict[str, dict], value_col: str,
                          unmapped_collector: list[str],
                          logger: logging.Logger,
                          context: str = "") -> pd.DataFrame:
    """
    Unit-specific normalization wrapper.

    Preserves the original raw unit column, adds <raw_col>_pre_normalized and
    <raw_col>_pre_normalization_note, and matches the dictionary using only the
    pre-normalized unit name. Numeric values are not converted by this step.
    """
    df = df.copy()
    pre_col = f"{raw_col}_pre_normalized"
    note_col = f"{raw_col}_pre_normalization_note"
    route_col = f"{raw_col}_pre_normalization_route"
    pre_values = []
    notes = []
    routes = []
    for raw in df[raw_col]:
        # Preserve existing exact/dictionary matches. Regex is only for terms
        # that would otherwise be unmapped.
        _, already_mapped = normalize_term(str(raw), mapping, value_col)
        if already_mapped:
            pre, note = str(raw).strip(), ""
        else:
            pre, note = pre_normalize_unit_name(str(raw), context=context)
        pre_values.append(pre)
        notes.append(note)
        if already_mapped:
            routes.append("already_mapped")
        elif note.startswith("unit pre-normalized:"):
            routes.append("regex_mapped")
        elif note.startswith("unit_contains_multiplier:"):
            routes.append("unit_contains_multiplier")
        elif note.startswith("unclear_"):
            routes.append("unclear")
        else:
            routes.append("unchanged_unmapped")
    df[pre_col] = pre_values
    df[note_col] = notes
    df[route_col] = routes

    before = len(unmapped_collector)
    df = normalize_column(df, pre_col, norm_col, mapping, value_col,
                          unmapped_collector, logger)
    if len(unmapped_collector) > before:
        # Report original terms, not just pre-normalized spellings, for QA.
        new_unmapped = set(unmapped_collector[before:])
        unmapped_collector[before:] = [
            str(raw).strip()
            for raw, pre in zip(df[raw_col], df[pre_col])
            if pre in new_unmapped and str(raw).strip() not in ("", "unclear", "not reported")
        ]

    n_changed = sum(1 for note in notes if note)
    if n_changed:
        logger.info(f"  Column '{raw_col}': {n_changed} unit names pre-normalized before dictionary lookup")
    return df


QUANTITATIVE_UNIT_FAMILIES = {
    "absolute_abundance_liquid",
    "absolute_abundance_solid",
    "absolute_abundance_air",
    "log_abundance",
    "relative_abundance_metagenomic",
    "relative_abundance_16S",
    "concentration",
}

AGGREGATE_TARGET_RE = re.compile(
    r"\b("
    r"total|all|overall|sum|combined|aggregate|aggregated|"
    r"resistome|mobilome|plasmidome|virulome|"
    r"args?|mges?|mrgs?|arbs?|antibiotic resistance genes?|"
    r"arg subtypes?|subtypes?|classes?|famil(?:y|ies)|markers?|"
    r"tet genes?|sul genes?|erm genes?|qnr genes?|bla genes?|"
    r"beta[-_ ]?lactam args?|tetracycline resistance genes?|"
    r"sulfonamide resistance genes?|macrolide resistance genes?|"
    r"quinolone resistance genes?"
    r")\b",
    re.IGNORECASE,
)

MULTI_GENE_TARGET_RE = re.compile(
    r"[,;]|\s+(?:and|or)\s+|/|\+|\bplus\b|\bmultiple\b|\bseveral\b",
    re.IGNORECASE,
)

MULTI_GENE_QUOTE_RE = re.compile(
    r"\b("
    r"all (?:tested |targeted |detected )?(?:genes|markers|args|mges)|"
    r"total (?:arg|mge|mrg|gene|plasmid)|"
    r"sum of|combined abundance|average (?:abundance|value|removal)|"
    r"gene markers|arg subtypes|across (?:the )?(?:genes|markers|targets)"
    r")\b",
    re.IGNORECASE,
)


def _clean_numeric_text(value: str) -> str:
    value = str(value or "").strip().replace(",", "")
    value = value.replace("−", "-").replace("–", "-").replace("—", "-")
    value = re.sub(r"([eE])\s*([+-])\s*(\d+)", r"\1\2\3", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def _is_single_numeric_value(value: str) -> bool:
    value = _clean_numeric_text(value)
    if not value:
        return False
    if re.search(r"\b(?:to|and|or)\b|[,;]", value, re.IGNORECASE):
        return False
    if re.search(r"\d\s*[-/]\s*\d", value):
        return False
    if re.fullmatch(r"[<>≤≥=~ ]*[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", value):
        return True
    return False


DETECTION_STATUS_COLUMNS = [
    "detection_status",
    "lod_loq_value",
    "lod_loq_unit",
    "detection_status_source",
    "detection_status_note",
]

LOD_LOQ_THRESHOLD_RE = re.compile(
    r"\b(?P<label>LOD|LOQ|limit of detection|limit of quantification|"
    r"detection limit|quantification limit|QL)\b"
    r"[^0-9<>=~]{0,40}"
    r"(?P<op>[<>=~]{0,2})\s*"
    r"(?P<value>[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:\s*(?:x|X|times)\s*10\s*\^?\s*[+-]?\d+|\s+10\s+[+-]?\d+|[eE][+-]?\d+)?)"
    r"\s*(?P<unit>[A-Za-z%][A-Za-z0-9%/(). _-]{0,60})?",
    re.IGNORECASE,
)

NUMERIC_START_RE = re.compile(
    r"^[<>~= ]*[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?(?:\s|$)",
    re.IGNORECASE,
)

UNIT_LIKE_RE = re.compile(
    r"\b(cop(?:y|ies)|gene|cell|cfu|ml|l\b|g\b|kg|ng|ug|uL|reaction|16s|"
    r"rrna|dna|log|percent|%|ppm|reads?|rpkm|tpm|hpm)\b",
    re.IGNORECASE,
)

THRESHOLD_UNIT_RE = re.compile(
    r"\b(cop(?:y|ies)|gene|cell|cfu|mPN|ml|l\b|g\b|kg|ng|ug|uL|reaction|"
    r"16s|rrna|dna)\b",
    re.IGNORECASE,
)

LOQ_BELOW_RE = re.compile(
    r"(<\s*LOQ|\bbelow\s+(?:the\s+)?(?:LOQ|limit of quantification|quantification limit)\b|"
    r"\bless than\s+(?:the\s+)?(?:LOQ|limit of quantification|quantification limit)\b|"
    r"\bbelow LOQ / not quantifiable\b)",
    re.IGNORECASE,
)

LOD_BELOW_RE = re.compile(
    r"(<\s*LOD|\bbelow\s+(?:the\s+)?(?:LOD|limit of detection|detection limit)\b|"
    r"\bless than\s+(?:the\s+)?(?:LOD|limit of detection|detection limit)\b|"
    r"\bdropped below the detection limit\b)",
    re.IGNORECASE,
)

NOT_DETECTED_RE = re.compile(
    r"(\bN\.?\s*D\.?\b|\bnot detected\b|\bnon[- ]?detect(?:ed|ion)?\b|"
    r"\bundetected\b|\bnot found\b|\bno amplification\b|\bnot present\b)",
    re.IGNORECASE,
)

DETECTED_PRESENCE_RE = re.compile(
    r"(\bpresence\s*/\s*absence\b|\bpresence[- ]absence\b|\bqualitative presence\b|"
    r"\blisted as present\b|\bpresence only\b|\bpresent\b|\bdetected\b)",
    re.IGNORECASE,
)

NOT_REPORTED_RE = re.compile(
    r"(\bnot reported\b|\bnot measured\b|\bnot determined\b|\bno data\b|"
    r"\bnot available\b|\bunit not visible\b)",
    re.IGNORECASE,
)

LOD_LOQ_METADATA_ONLY_RE = re.compile(
    r"\b(LOQ|LOD|QL)\s+(?:values?|was|were|stated|for|of method|of qPCR|"
    r"of assay|limit of method)\b",
    re.IGNORECASE,
)


def _clean_detection_text(value: str) -> str:
    text = str(value or "")
    text = text.replace("\u2212", "-").replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("\u00b5", "u").replace("\u03bc", "u")
    text = text.replace("\u00d7", "x")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _measurement_value_text(row: pd.Series) -> str:
    cols = [
        "raw_value",
        "value_min",
        "value_max",
        "mean_value",
        "median_value",
        "unit",
        "raw_unit",
        "raw_unit_pre_normalized",
        "normalized_unit",
        "final_unit",
        "unit_family",
    ]
    return _clean_detection_text(" | ".join(str(row.get(c, "")) for c in cols))


def _measurement_context_text(row: pd.Series) -> str:
    cols = [
        "evidence_quote",
        "detection_method",
        "basis",
        "normalization_method",
        "target_name",
        "raw_target_name",
    ]
    text = _clean_detection_text(" | ".join(str(row.get(c, "")) for c in cols))
    text = re.sub(r"\|\s*AI verified evidence:.*$", "", text, flags=re.IGNORECASE)
    return text


def _has_measurement_numeric_value(row: pd.Series) -> bool:
    for col in ["raw_value", "mean_value", "median_value", "value_min", "value_max", "normalized_value"]:
        text = _clean_numeric_text(row.get(col, ""))
        if not text:
            continue
        if re.search(r"\b(?:to|and|or)\b|[,;]", text, re.IGNORECASE):
            continue
        if re.search(r"\b(?:below|LOD|LOQ|not detected|ND|not reported)\b", text, re.IGNORECASE):
            continue
        if _is_single_numeric_value(text) or NUMERIC_START_RE.search(text):
            return True
    return False


def _extract_lod_loq_threshold(row: pd.Series) -> tuple[str, str]:
    value_text = _measurement_value_text(row)
    context_text = _measurement_context_text(row)
    raw_value = _clean_detection_text(row.get("raw_value", ""))
    raw_unit = _clean_detection_text(row.get("unit", row.get("raw_unit", "")))
    if re.search(r"\bstill present\b", context_text, re.IGNORECASE):
        return "", ""
    if (
        _is_single_numeric_value(raw_value)
        and raw_unit
        and THRESHOLD_UNIT_RE.search(raw_unit)
        and re.search(
            r"\b(LOD|LOQ|limit of detection|limit of quantification|"
            r"detection limit|quantification limit|limit of method)\b",
            context_text,
            re.IGNORECASE,
        )
    ):
        return raw_value, raw_unit

    text = " | ".join([value_text, context_text])
    for match in LOD_LOQ_THRESHOLD_RE.finditer(text):
        unit = _clean_detection_text(match.group("unit") or "")
        unit = re.split(r"[.;|]", unit, maxsplit=1)[0].strip(" :,-")
        unit = re.split(r"\s+for\s+", unit, maxsplit=1, flags=re.IGNORECASE)[0].strip(" :,-")
        unit = unit.rstrip(")")
        if unit and re.search(r"\bout of\b", unit, re.IGNORECASE):
            continue
        if not unit:
            continue
        if not THRESHOLD_UNIT_RE.search(unit):
            continue
        value = _clean_detection_text(match.group("value") or "")
        if value:
            return value, unit
    return "", ""


def _target_in_exception_clause(row: pd.Series, context_text: str) -> bool:
    target = str(row.get("target_name", row.get("raw_target_name", ""))).strip().lower()
    normalized = str(row.get("normalized_target_name", "")).strip().lower()
    targets = {t for t in [target, normalized] if t}
    if not targets:
        return False
    for match in re.finditer(
        r"(?:except|with the exception of|exception of)\s+([^.;|]+)",
        context_text,
        re.IGNORECASE,
    ):
        clause = match.group(1).lower()
        if any(t in clause for t in targets):
            return True
    return False


def _is_lod_loq_metadata_target(row: pd.Series) -> bool:
    text = " ".join([
        str(row.get("target_name", "")),
        str(row.get("raw_target_name", "")),
        str(row.get("normalized_target_name", "")),
        str(row.get("unit", "")),
        str(row.get("raw_unit", "")),
    ])
    return bool(re.search(r"\b(LOD|LOQ|qPCR_LOQ|assay LOQ|assay LOD)\b", text, re.IGNORECASE))


def _is_lod_loq_metadata_only(row: pd.Series, context_text: str) -> bool:
    text = " ".join([
        str(row.get("target_name", "")),
        str(row.get("raw_target_name", "")),
        str(row.get("unit", "")),
        str(row.get("raw_unit", "")),
        context_text,
    ])
    return bool(re.search(
        r"\b("
        r"limit of method|detection limit of method|quantification limit of method|"
        r"printed exact LOQ|LOQ stated|LOD was set|LOD equivalent|"
        r"limit of quantification stated|lower bound of printed limit|"
        r"upper bound of printed limit|qPCR_LOQ|assay LOQ|assay LOD|"
        r"\(LOQ\)|\(LOD"
        r")\b",
        text,
        re.IGNORECASE,
    ))


def classify_measurement_detection_status(row: pd.Series) -> tuple[str, str, str, str, str]:
    """
    Classify censored/occurrence status without substituting censored values.

    Explicit below-LOD/LOQ and not-detected cues take precedence over numeric
    values so that censored observations are not silently treated as zero or
    quantified abundance.
    """
    value_text = _measurement_value_text(row)
    context_text = _measurement_context_text(row)
    combined_text = f"{value_text} | {context_text}"
    value_lower = value_text.lower()
    combined_lower = combined_text.lower()
    has_numeric = _has_measurement_numeric_value(row)
    unit_family = str(row.get("unit_family", "")).strip()
    normalized_unit = str(row.get("normalized_unit", "")).strip()
    lod_loq_value, lod_loq_unit = _extract_lod_loq_threshold(row)

    value_has_loq = bool(LOQ_BELOW_RE.search(value_text))
    value_has_lod = bool(LOD_BELOW_RE.search(value_text))
    context_has_loq = bool(LOQ_BELOW_RE.search(context_text)) and not bool(
        LOD_LOQ_METADATA_ONLY_RE.search(context_text)
    )
    context_has_lod = bool(LOD_BELOW_RE.search(context_text)) and not bool(
        LOD_LOQ_METADATA_ONLY_RE.search(context_text)
    )
    if _target_in_exception_clause(row, context_text):
        context_has_loq = False
        context_has_lod = False
    if has_numeric and re.search(
        r"\b(still present|above (?:the )?(?:detection limit|LOD|LOQ)|"
        r"above detection limit|yielded results above detection limit)\b",
        context_text,
        re.IGNORECASE,
    ):
        context_has_loq = False
        context_has_lod = False
    if _is_lod_loq_metadata_target(row) and not (value_has_loq or value_has_lod):
        context_has_loq = False
        context_has_lod = False

    if value_has_loq or context_has_loq:
        return (
            "below_LOQ",
            lod_loq_value,
            lod_loq_unit,
            "explicit_below_loq",
            "explicit below-LOQ cue; no numeric substitution applied",
        )
    if value_has_lod or context_has_lod:
        return (
            "below_LOD",
            lod_loq_value,
            lod_loq_unit,
            "explicit_below_lod",
            "explicit below-LOD cue; no numeric substitution applied",
        )
    if NOT_DETECTED_RE.search(value_text) or (
        NOT_DETECTED_RE.search(context_text) and not has_numeric
    ):
        return (
            "not_detected",
            lod_loq_value,
            lod_loq_unit,
            "explicit_not_detected",
            "explicit non-detect cue without LOD/LOQ wording",
        )
    if unit_family == "detection_status" or normalized_unit == "detection_status":
        if re.search(r"\b(not detected|ND)\b", value_lower, re.IGNORECASE):
            return (
                "not_detected",
                lod_loq_value,
                lod_loq_unit,
                "unit_detection_status_not_detected",
                "unit dictionary marks detection status and text is non-detect",
            )
        return (
            "detected_not_quantified",
            lod_loq_value,
            lod_loq_unit,
            "qualitative_detected_presence",
            "presence/absence or detected-only unit; no abundance value quantified",
        )
    if (
        lod_loq_value
        and not (value_has_loq or value_has_lod or context_has_loq or context_has_lod)
        and _is_lod_loq_metadata_only(row, context_text)
    ):
        return (
            "not_reported",
            lod_loq_value,
            lod_loq_unit,
            "lod_loq_metadata_only",
            "LOD/LOQ method-threshold metadata retained; no sample detection result inferred",
        )
    if has_numeric:
        note = "numeric measurement value present"
        if re.search(r"^0(?:\.0+)?$", _clean_numeric_text(row.get("raw_value", ""))):
            note = "numeric zero with no explicit censored/non-detect cue"
        return (
            "detected_quantified",
            lod_loq_value,
            lod_loq_unit,
            "numeric_quantified",
            note,
        )
    if DETECTED_PRESENCE_RE.search(combined_text):
        return (
            "detected_not_quantified",
            lod_loq_value,
            lod_loq_unit,
            "qualitative_detected_presence",
            "detected/present cue but no usable quantitative value",
        )
    if NOT_REPORTED_RE.search(combined_text) or not combined_lower.strip(" |"):
        return (
            "not_reported",
            lod_loq_value,
            lod_loq_unit,
            "not_reported_or_missing",
            "measurement value not reported; no detection/non-detection status inferred",
        )
    return (
        "not_reported",
        lod_loq_value,
        lod_loq_unit,
        "unresolved_no_detection_signal",
        "no numeric value or explicit detection-status cue found",
    )


def add_detection_status_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    statuses = []
    lod_values = []
    lod_units = []
    sources = []
    notes = []
    for _, row in df.iterrows():
        status, lod_value, lod_unit, source, note = classify_measurement_detection_status(row)
        statuses.append(status)
        lod_values.append(lod_value)
        lod_units.append(lod_unit)
        sources.append(source)
        notes.append(note)
    df["detection_status"] = statuses
    df["lod_loq_value"] = lod_values
    df["lod_loq_unit"] = lod_units
    df["detection_status_source"] = sources
    df["detection_status_note"] = notes
    return df


def _has_range_value(row: pd.Series) -> bool:
    if str(row.get("value_min", "")).strip() or str(row.get("value_max", "")).strip():
        return True
    value_fields = [
        row.get("raw_value", ""),
        row.get("mean_value", ""),
        row.get("median_value", ""),
    ]
    for value in value_fields:
        text = _clean_numeric_text(value)
        if re.search(r"\d\s*(?:-|to|/)\s*\d", text, re.IGNORECASE):
            return True
        if re.search(r"\b(?:range|ranged|between)\b", text, re.IGNORECASE):
            return True
    quote = _clean_numeric_text(row.get("evidence_quote", ""))
    if re.search(r"\b(?:range|ranged|between|upper endpoint|lower endpoint)\b", quote, re.IGNORECASE):
        return True
    if re.search(
        r"\d(?:\.\d+)?(?:\s*(?:x|×)\s*10\^?[+-]?\d+)?\s*(?:-|to)\s*"
        r"\d(?:\.\d+)?(?:\s*(?:x|×)\s*10\^?[+-]?\d+)?",
        quote,
        re.IGNORECASE,
    ):
        return True
    return False


def _has_single_numeric_measurement(row: pd.Series) -> bool:
    if _has_range_value(row):
        return False
    value_fields = [
        row.get("raw_value", ""),
        row.get("mean_value", ""),
        row.get("median_value", ""),
    ]
    numeric_fields = [value for value in value_fields if _is_single_numeric_value(value)]
    populated_fields = [str(value).strip() for value in value_fields if str(value).strip()]
    return len(numeric_fields) == 1 and len(populated_fields) == 1


def _is_quantitative_unit(row: pd.Series) -> bool:
    if str(row.get("raw_unit_pre_normalization_route", "")).strip() == "unit_contains_multiplier":
        return False
    if str(row.get("normalized_unit_mapped", "")).strip() != "Yes":
        return False
    return str(row.get("unit_family", "")).strip() in QUANTITATIVE_UNIT_FAMILIES


def _is_specific_gene_target(row: pd.Series) -> bool:
    target = str(row.get("target_name", "")).strip()
    normalized = str(row.get("normalized_target_name", "")).strip()
    target_type = str(row.get("target_type", "")).strip().lower()
    quote = str(row.get("evidence_quote", "")).strip()
    combined_target = " ".join([target, normalized, target_type])

    if not target or str(row.get("normalized_target_name_mapped", "")).strip() != "Yes":
        return False
    if AGGREGATE_TARGET_RE.search(combined_target):
        return False
    if MULTI_GENE_TARGET_RE.search(target) or MULTI_GENE_TARGET_RE.search(normalized):
        return False
    if MULTI_GENE_QUOTE_RE.search(quote):
        return False
    return True


def infer_legacy_value_scope(df: pd.DataFrame) -> pd.DataFrame:
    """
    Infer value_scope for legacy rows that predate the v3 prompt.

    Only blank legacy rows are inferred. The rule is intentionally conservative:
    aggregate targets, ranges, multi-gene hints, non-quantitative units, and
    multiplier units are left outside the inferred quantitative stream.
    """
    df = df.copy()
    if "value_scope" not in df.columns:
        df["value_scope"] = ""

    original_scope = df["value_scope"].astype(str).fillna("").str.strip()
    inferred_scope = []
    origins = []
    notes = []

    for idx, row in df.iterrows():
        current = str(row.get("value_scope", "")).strip()
        legacy_blank = (
            current == ""
            and str(row.get("matrix_label_backfill_confidence", "")).strip()
            == "not_applicable_existing_legacy"
        )

        if not legacy_blank:
            inferred_scope.append(current)
            if current in {"target_specific", "group_level_value", "group_level_range", "unclear"}:
                origins.append("vision_prompt_original")
            elif current == "not_applicable_legacy_only":
                origins.append("legacy_not_applicable_existing")
            elif current:
                origins.append("existing_nonblank")
            else:
                origins.append("missing_value_scope")
            notes.append("")
            continue

        has_range = _has_range_value(row)
        specific_target = _is_specific_gene_target(row)
        quantitative_unit = _is_quantitative_unit(row)
        single_numeric = _has_single_numeric_measurement(row)
        target_text = " ".join([
            str(row.get("target_name", "")),
            str(row.get("normalized_target_name", "")),
            str(row.get("target_type", "")),
        ])
        quote = str(row.get("evidence_quote", ""))
        aggregate_or_multi = bool(
            AGGREGATE_TARGET_RE.search(target_text)
            or MULTI_GENE_TARGET_RE.search(str(row.get("target_name", "")))
            or MULTI_GENE_TARGET_RE.search(str(row.get("normalized_target_name", "")))
            or MULTI_GENE_QUOTE_RE.search(quote)
        )

        if has_range or aggregate_or_multi:
            inferred_scope.append("group_level_inferred_legacy")
            origins.append("rule_inferred_legacy")
            reason = "range_value" if has_range else "aggregate_or_multi_gene_signal"
            notes.append(reason)
        elif single_numeric and specific_target and quantitative_unit:
            inferred_scope.append("target_specific_inferred_legacy")
            origins.append("rule_inferred_legacy")
            notes.append("single_numeric_specific_gene_quantitative_unit")
        else:
            inferred_scope.append("")
            origins.append("legacy_blank_unresolved")
            missing = []
            if not single_numeric:
                missing.append("not_single_numeric")
            if not specific_target:
                missing.append("not_specific_mapped_gene")
            if not quantitative_unit:
                missing.append("not_quantitative_mapped_unit")
            notes.append(";".join(missing))

    df["value_scope"] = inferred_scope
    df["value_scope_origin"] = origins
    df["value_scope_inference_note"] = notes
    df["value_scope_original_before_inference"] = original_scope
    return df


def _has_single_numeric_outcome(row: pd.Series) -> bool:
    if str(row.get("reported_outcome_value_min", "")).strip() or str(row.get("reported_outcome_value_max", "")).strip():
        return False
    value = _clean_numeric_text(row.get("reported_outcome_value", ""))
    return _is_single_numeric_value(value)


def _has_outcome_range_value(row: pd.Series) -> bool:
    if str(row.get("reported_outcome_value_min", "")).strip() or str(row.get("reported_outcome_value_max", "")).strip():
        return True
    value = _clean_numeric_text(row.get("reported_outcome_value", ""))
    if re.search(r"\d\s*(?:-|to|/)\s*\d", value, re.IGNORECASE):
        return True
    quote = _clean_numeric_text(row.get("evidence_quote", ""))
    if re.search(r"\b(?:range|ranged|between|from)\b", quote, re.IGNORECASE) and re.search(
        r"\d(?:\.\d+)?(?:\s*(?:x|×)\s*10\^?[+-]?\d+)?\s*(?:-|to)\s*"
        r"\d(?:\.\d+)?(?:\s*(?:x|×)\s*10\^?[+-]?\d+)?",
        quote,
        re.IGNORECASE,
    ):
        return True
    return False


def _is_clear_removal_outcome_type(row: pd.Series) -> bool:
    values = " ".join([
        str(row.get("normalized_outcome_type", "")),
        str(row.get("outcome_type", "")),
        str(row.get("outcome_group", "")),
    ]).lower()
    return bool(re.search(r"\b(removal_efficiency|log_reduction|reduction|removal)\b", values))


def _is_specific_outcome_target(row: pd.Series) -> bool:
    target = str(row.get("target_name", "")).strip()
    normalized = str(row.get("normalized_target_name", "")).strip()
    target_type = str(row.get("target_type", "")).strip().lower()
    combined_target = " ".join([target, normalized, target_type])

    if not target or str(row.get("normalized_target_name_mapped", "")).strip() != "Yes":
        return False
    if AGGREGATE_TARGET_RE.search(combined_target):
        return False
    if MULTI_GENE_TARGET_RE.search(target) or MULTI_GENE_TARGET_RE.search(normalized):
        return False
    return True


def infer_legacy_outcome_value_scope(df: pd.DataFrame) -> pd.DataFrame:
    """
    Infer value_scope for legacy outcome rows that predate the v3 prompt.

    Outcome rows often contain author-reported per-gene removal values even
    when the evidence sentence mentions several genes. The target/value/type
    fields therefore drive the target-specific inference, while aggregate
    target labels and numeric ranges remain caution-layer rows.
    """
    df = df.copy()
    if "value_scope" not in df.columns:
        df["value_scope"] = ""

    original_scope = df["value_scope"].astype(str).fillna("").str.strip()
    inferred_scope = []
    origins = []
    notes = []

    for _, row in df.iterrows():
        current = str(row.get("value_scope", "")).strip()
        legacy_blank = (
            current == ""
            and str(row.get("matrix_label_backfill_confidence", "")).strip()
            == "not_applicable_existing_legacy"
        )

        if not legacy_blank:
            inferred_scope.append(current)
            if current in {"target_specific", "group_level_value", "group_level_range", "unclear"}:
                origins.append("vision_prompt_original")
            elif current == "not_applicable_legacy_only":
                origins.append("legacy_not_applicable_existing")
            elif current:
                origins.append("existing_nonblank")
            else:
                origins.append("missing_value_scope")
            notes.append("")
            continue

        has_range = _has_outcome_range_value(row)
        specific_target = _is_specific_outcome_target(row)
        clear_removal = _is_clear_removal_outcome_type(row)
        single_numeric = _has_single_numeric_outcome(row)
        target_text = " ".join([
            str(row.get("target_name", "")),
            str(row.get("normalized_target_name", "")),
            str(row.get("target_type", "")),
        ])
        aggregate_or_multi_target = bool(
            AGGREGATE_TARGET_RE.search(target_text)
            or MULTI_GENE_TARGET_RE.search(str(row.get("target_name", "")))
            or MULTI_GENE_TARGET_RE.search(str(row.get("normalized_target_name", "")))
        )

        if has_range or aggregate_or_multi_target:
            inferred_scope.append("group_level_inferred_legacy")
            origins.append("rule_inferred_legacy")
            reason = "range_value" if has_range else "aggregate_or_multi_gene_target"
            notes.append(reason)
        elif single_numeric and specific_target and clear_removal:
            inferred_scope.append("target_specific_inferred_legacy")
            origins.append("rule_inferred_legacy")
            notes.append("single_numeric_specific_gene_clear_removal_outcome")
        else:
            inferred_scope.append("")
            origins.append("legacy_blank_unresolved")
            missing = []
            if not single_numeric:
                missing.append("not_single_numeric")
            if not specific_target:
                missing.append("not_specific_mapped_gene")
            if not clear_removal:
                missing.append("not_clear_removal_outcome_type")
            notes.append(";".join(missing))

    df["value_scope"] = inferred_scope
    df["value_scope_origin"] = origins
    df["value_scope_inference_note"] = notes
    df["value_scope_original_before_inference"] = original_scope
    return df


def _direction_text(row: pd.Series) -> str:
    fields = [
        "evidence_quote",
        "interpretation",
        "pairing_basis",
        "raw_reported_outcome_unit",
        "reported_outcome_unit",
    ]
    return " ".join(str(row.get(field, "")) for field in fields if str(row.get(field, "")).strip()).lower()


def _direction_numeric_value(row: pd.Series) -> float | None:
    value = _clean_numeric_text(row.get("reported_outcome_value", ""))
    if not value or not _is_single_numeric_value(value):
        return None
    try:
        return float(re.sub(r"^[<>=~ ]+", "", value))
    except ValueError:
        return None


def _extract_before_after_values(text: str) -> tuple[float, float] | None:
    if re.search(r"\b(range|ranged|between|required for|upper bound|lower bound)\b", text, re.IGNORECASE):
        return None
    patterns = [
        r"exact printed values\s+([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?)\s+(?:to|->|â†’)\s+([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?)",
        r"\bfrom\s+([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?)\s+(?:[^.;,]{0,40}?)\bto\s+([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?)",
        r"\bdecreased\s+from\s+([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?)\s+(?:[^.;,]{0,40}?)\bto\s+([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?)",
        r"\bincreased\s+from\s+([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?)\s+(?:[^.;,]{0,40}?)\bto\s+([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1)), float(match.group(2))
            except ValueError:
                return None
    return None


def infer_directional_change_outcome(row: pd.Series) -> tuple[str, str, str, str]:
    """
    Resolve v3 directional-change aliases into removal/enrichment/ambiguous.

    The rule intentionally avoids sign-only classification. Numeric signs are
    used only with a convention cue such as "removal efficiency" or "log
    reduction", where a negative value means negative removal.
    """
    if str(row.get("outcome_group", "")).strip() != "directional_change_needs_review":
        return "not_applicable", "", "", ""

    text = _direction_text(row)
    raw_unit = " ".join([
        str(row.get("raw_reported_outcome_unit", "")),
        str(row.get("reported_outcome_unit", "")),
    ]).lower()
    value = _direction_numeric_value(row)

    if re.search(r"\b(spearman|pearson|correlation|correlat(?:es|ed|ion)|associated with|association coefficient)\b", text, re.IGNORECASE):
        return "direction_ambiguous", "ambiguous_left_blank", "association_not_directional_change", "association/correlation statistic is not a removal or enrichment outcome"

    no_change_cue = bool(re.search(
        r"\b(no significant|not significant|not significantly|unchanged|stable|no clear)\b",
        text,
        re.IGNORECASE,
    ))
    if no_change_cue and not re.search(r"\b(removal efficiency|percent removal|% removal|log reduction|lrv)\b", text):
        return "direction_ambiguous", "ambiguous_left_blank", "no_change_or_uncertain_direction", "no reliable decrease/increase direction"

    enrichment_specific = [
        r"\bincreased?\s+(?:from|by|in|to|after)\b",
        r"\bincreased?\s+\d",
        r"\bincreased?\s+(?:level|abundance|amount|copy|copies|concentration)\b",
        r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+(?:\.\d+)?)\s*[- ]?(?:fold|times)\s+(?:increased?|higher|as high)\b",
        r"\bincrease rather than removal\b",
        r"\bfold\s+increase\b",
        r"\btimes\s+higher\b",
        r"\btimes\s+as\s+high\b",
        r"\b(?:was|were|is|are)?\s*higher\s+(?:than|in|after|from)\b",
        r"\belevated\b",
        r"\benriched\b|\benrichment\b",
        r"\bpercent\s+increase\b|%\s*increase\b",
        r"\blog\s+change\b.*\bincrease\b",
    ]
    removal_specific = [
        r"\bremoval efficiency\b",
        r"\bpercent\s+removal\b|%\s*removal\b",
        r"\bpercent\s+reduction\b|%\s*reduction\b",
        r"\blog(?:10)?\s+reduction\b|\blrv\b",
        r"\breduced?\s+(?:from|by|in|after|during)\b",
        r"\breduced?\s+\w+\s+(?:by|in|after|during)\b",
        r"\breduction\s+(?:of|during|after|by|in)\b",
        r"\breductions?\b",
        r"\bdecreased?\s+(?:from|by|in|after|during)\b",
        r"\bfold\s+decrease\b|\bfold\s+reduction\b",
        r"\btimes\s+lower\b|\bfold\s+lower\b|\blower\s+than\b",
        r"\blowered\s+(?:from|by|in|after|during)\b",
        r"\beliminated\b|\bremoved\b|\bdepletion\b|\bdeclined\b",
    ]

    enrichment_hits = [pattern for pattern in enrichment_specific if re.search(pattern, text, re.IGNORECASE)]
    removal_hits = [pattern for pattern in removal_specific if re.search(pattern, text, re.IGNORECASE)]

    if enrichment_hits and not removal_hits:
        return "direction_resolved_enrichment", "high_keyword", "explicit_enrichment_keyword", enrichment_hits[0]
    if removal_hits and not enrichment_hits:
        if value is not None and value < 0 and re.search(r"\b(removal efficiency|percent removal|% removal|percent reduction|% reduction|log reduction|lrv)\b", text):
            return "direction_resolved_enrichment", "medium_convention", "negative_removal_metric", "negative value with removal/reduction convention"
        return "direction_resolved_removal", "high_keyword", "explicit_removal_keyword", removal_hits[0]

    if enrichment_hits and removal_hits:
        if re.search(r"\bincrease rather than removal\b|\bincreased?\b[^.;]{0,80}\brather than removal\b", text, re.IGNORECASE):
            return "direction_resolved_enrichment", "high_keyword", "explicit_enrichment_over_removal", "increase rather than removal"
        if value is not None and value < 0 and re.search(r"\b(removal efficiency|percent removal|% removal|percent reduction|% reduction|log reduction|lrv)\b", text):
            return "direction_resolved_enrichment", "medium_convention", "negative_removal_metric", "negative value with removal/reduction convention"
        return "direction_ambiguous", "ambiguous_left_blank", "conflicting_direction_keywords", "both removal and enrichment cues present"

    before_after = _extract_before_after_values(text)
    if before_after is not None:
        before, after = before_after
        if after < before:
            return "direction_resolved_removal", "medium_before_after", "before_after_numeric_decrease", f"{before} to {after}"
        if after > before:
            return "direction_resolved_enrichment", "medium_before_after", "before_after_numeric_increase", f"{before} to {after}"

    if value is not None and value < 0 and re.search(r"\b(removal efficiency|percent removal|% removal|percent reduction|% reduction|log reduction|lrv)\b", raw_unit):
        return "direction_resolved_enrichment", "medium_convention", "negative_removal_metric", "negative value with removal/reduction unit"

    return "direction_ambiguous", "ambiguous_left_blank", "no_reliable_direction_signal", "no explicit direction keyword or safe before-after comparison"


def add_directional_change_resolution(df: pd.DataFrame) -> pd.DataFrame:
    """Add direction-resolution columns for directional_change_needs_review rows."""
    df = df.copy()
    labels = []
    confidences = []
    signals = []
    notes = []
    for _, row in df.iterrows():
        label, confidence, signal, note = infer_directional_change_outcome(row)
        labels.append(label)
        confidences.append(confidence)
        signals.append(signal)
        notes.append(note)
    df["direction_inference_label"] = labels
    df["direction_inference_confidence"] = confidences
    df["direction_inference_signal"] = signals
    df["direction_inference_note"] = notes
    return df


def add_processing_stream(df: pd.DataFrame, value_scope_col: str = "value_scope") -> pd.DataFrame:
    """
    Add processing_stream from value_scope without dropping rows.

    target_specific is split into a high-confidence stream when it comes from
    the v3 prompt, while rule-inferred legacy target-specific rows are kept in
    a separate quantitative stream for sensitivity analysis.
    """
    df = df.copy()
    caution = {
        "group_level_value",
        "group_level_range",
        "group_level_inferred_legacy",
        "unclear",
    }

    def stream(value: str) -> str:
        v = str(value).strip()
        if v == "target_specific":
            return "quantitative_core_high_confidence"
        if v == "target_specific_inferred_legacy":
            return "quantitative_core_inferred"
        if v in caution:
            return "qualitative_caution"
        return "needs_value_scope_review"

    if value_scope_col not in df.columns:
        df["processing_stream"] = "needs_value_scope_review"
    else:
        df["processing_stream"] = df[value_scope_col].apply(stream)
    return df


# ── Output guard ──────────────────────────────────────────────────────────────

def check_overwrite(path: Path, overwrite: bool, logger: logging.Logger) -> bool:
    """Return True if OK to write; exit if not."""
    import sys
    if path.exists() and not overwrite:
        logger.error(f"Output exists: {path}. Use --overwrite to replace.")
        sys.exit(1)
    return True


# ── Save output ───────────────────────────────────────────────────────────────

def save_output(df: pd.DataFrame, path: Path, logger: logging.Logger) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    logger.info(f"Saved: {path.name} ({len(df)} rows)")
