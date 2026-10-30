
"""
SmartHire AI - Shared skill matching module.
Used by both the Streamlit application and evaluation scripts.
"""

import re


# Canonical skill names and their recognized aliases.
SKILL_ALIASES = {
    "machine learning": ["ml", "machine-learning"],
    "artificial intelligence": ["ai"],
    "natural language processing": ["nlp"],
    "c plus plus": ["c++"],
    "javascript": ["js", "java script"],
    "structured query language": ["sql"],
    "microsoft excel": ["excel", "ms excel"],
    "power bi": ["powerbi"],
    "amazon web services": ["aws"],
    "continuous integration/continuous delivery": ["ci/cd", "cicd"],
    "object oriented programming": ["oop", "object-oriented programming"],
    "scikit-learn": ["sklearn", "scikit learn"],
    "pytorch": ["torch"],
    "tensorflow": ["tf"],
    "natural language generation": ["nlg"],
    "large language models": ["llm", "llms", "large language model"],
    "retrieval augmented generation": [
        "rag",
        "retrieval-augmented generation",
    ],
    "version control": ["git", "version-control"],
    "user interface": ["ui"],
    "user experience": ["ux"],
    "microsoft azure": ["azure"],
    "google cloud platform": ["gcp", "google cloud"],
}


def normalize_text(text):
    """Normalize case, punctuation, ampersands, and whitespace."""
    text = (text or "").lower()
    text = text.replace("&", " and ")
    text = re.sub(r"[\u2010-\u2015]", "-", text)
    text = re.sub(r"[^a-z0-9+#./\-\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def skill_terms(skill):
    """Return the skill and its recognized aliases."""
    normalized_skill = normalize_text(skill)
    terms = [normalized_skill]

    for canonical, aliases in SKILL_ALIASES.items():
        group = [canonical] + aliases
        normalized_group = [
            normalize_text(item) for item in group
        ]

        if normalized_skill in normalized_group:
            terms.extend(normalized_group)

    # Keep original order and remove duplicates.
    return list(dict.fromkeys(term for term in terms if term))



def find_skill_evidence(resume_text, required_skills):
    """
    Return:
        matched: skills detected in the resume
        missing: skills not detected
        evidence: short text snippets supporting each match

    A degree title alone does not count as evidence of the
    Communication skill.
    """
    normalized_resume = normalize_text(resume_text)

    matched = []
    missing = []
    evidence = {}

    for skill in sorted(required_skills):
        found_match = None

        for term in skill_terms(skill):
            # Prevent partial-word matches.
            pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"

            for match in re.finditer(pattern, normalized_resume):
                # Exclude "Communication" when it appears as part
                # of an Electronics and Communication Engineering
                # degree title. Continue searching for other
                # occurrences that may demonstrate the skill.
                if normalize_text(skill) == "communication":
                    degree_pattern = (
                        r"\belectronics(?: and)? "
                        r"communication engineering\b"
                    )

                    is_degree_title = any(
                        degree_match.start() <= match.start()
                        and match.end() <= degree_match.end()
                        for degree_match in re.finditer(
                            degree_pattern, normalized_resume
                        )
                    )

                    if is_degree_title:
                        continue

                found_match = match
                break

            if found_match:
                break

        if found_match:
            matched.append(skill)

            start = max(0, found_match.start() - 75)
            end = min(
                len(normalized_resume),
                found_match.end() + 100,
            )

            evidence[skill] = normalized_resume[start:end].strip()
        else:
            missing.append(skill)

    return matched, missing, evidence


def calculate_weighted_score(matched, required, critical):
    """
    Critical skill = 2 points.
    Other required skill = 1 point.

    Returns:
        earned_points, total_points, score_percentage
    """
    required = set(required)
    critical = set(critical)
    matched = set(matched)

    if not critical.issubset(required):
        raise ValueError(
            "Every critical skill must also be a required skill."
        )

    if not matched.issubset(required):
        raise ValueError(
            "Matched skills must belong to the required skill list."
        )

    total_points = sum(
        2 if skill in critical else 1
        for skill in required
    )

    earned_points = sum(
        2 if skill in critical else 1
        for skill in matched
    )

    score = (
        round(earned_points / total_points * 100, 2)
        if total_points
        else 0.0
    )

    return earned_points, total_points, score

def classify_skill_evidence(skill, snippet):
    """
    Suggest an evidence category using conservative text rules.
    This is a heuristic, not a verified assessment of proficiency.
    """
    text = normalize_text(snippet)
    skill_normalized = normalize_text(skill)

    # Locate the skill within the excerpt.
    position = -1
    for term in skill_terms(skill):
        match = re.search(
            r"(?<!\w)" + re.escape(term) + r"(?!\w)",
            text,
        )
        if match:
            position = match.start()
            break

    if position < 0:
        return "Needs manual review"

    # Examine nearby wording, not the entire resume excerpt.
    start = max(0, position - 55)
    end = min(len(text), position + len(skill_normalized) + 55)
    context = text[start:end]

    project_cues = re.compile(
        r"\b(project|hackathon|capstone|implemented|"
        r"built|developed|created|designed|trained|"
        r"evaluated|deployed|analyzed|analysed)\b"
    )

    if project_cues.search(context):
        return "Possible project evidence"

    professional_cues = re.compile(
        r"\b(internship|intern|employment|work experience|"
        r"professional experience|at my job)\b"
    )

    if professional_cues.search(context):
        return "Possible professional evidence"

    return "Skill mentioned"

