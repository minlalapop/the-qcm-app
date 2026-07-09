from collections import Counter

from app.schemas.learning import QualityMetricSource, QuestionFeedbackSource


RULE_CATALOG = {
    "distracteurs_trop_faciles": "Generer des distracteurs plausibles, proches conceptuellement de la bonne reponse, et eviter les propositions evidemment fausses.",
    "question_ambigue": "Formuler une question claire, avec un seul objectif cognitif et sans double negation ni formulation vague.",
    "reponse_incorrecte": "Verifier qu'une seule option est correcte et que la justification confirme explicitement cette option.",
    "question_incorrecte": "Ne poser que des questions strictement justifiees par les sources selectionnees.",
    "difficulte_mal_adaptee": "Adapter le niveau de detail, le vocabulaire et les pieges au niveau de difficulte demande.",
    "correction_enseignant": "Tenir compte des corrections validees par les enseignants comme exemples de style attendu.",
}


PREFERENCE_CATALOG = {
    "distracteurs_plausibles": "Prefere des distracteurs plausibles plutot que des reponses manifestement fausses.",
    "justification_obligatoire": "Prefere une justification courte mais obligatoire pour chaque question.",
    "une_seule_bonne_reponse": "Prefere exactement une seule bonne reponse par question.",
    "eviter_ambiguite": "Prefere des formulations non ambigues et directement evaluables.",
}


def count_feedback_issues(feedbacks: list[QuestionFeedbackSource]) -> Counter:
    counter: Counter = Counter()
    for feedback in feedbacks:
        for issue_type in feedback.issue_types:
            counter[issue_type] += 1
        if feedback.question_is_correct is False:
            counter["question_incorrecte"] += 1
        if feedback.correct_answer_is_valid is False:
            counter["reponse_incorrecte"] += 1
        if feedback.distractors_quality == "too_easy":
            counter["distracteurs_trop_faciles"] += 1
        if feedback.is_ambiguous:
            counter["question_ambigue"] += 1
        if feedback.difficulty_fit in {"too_easy", "too_hard", "wrong_level"}:
            counter["difficulte_mal_adaptee"] += 1
        if feedback.corrected_question_text or feedback.corrected_answers:
            counter["correction_enseignant"] += 1
    return counter


def recommendations_from_issues(issue_counts: Counter, feedback_count: int) -> list[dict]:
    if feedback_count <= 0:
        return []

    recommendations = []
    for issue_key, support_count in issue_counts.most_common():
        rule_text = RULE_CATALOG.get(issue_key)
        if not rule_text:
            continue
        confidence = min(1.0, max(0.1, support_count / feedback_count))
        recommendations.append(
            {
                "rule_key": issue_key,
                "rule_text": rule_text,
                "support_count": support_count,
                "confidence": round(confidence, 4),
            }
        )
    return recommendations


def infer_preferences(feedbacks: list[QuestionFeedbackSource]) -> list[dict]:
    issue_counts = count_feedback_issues(feedbacks)
    preferences = []

    if issue_counts["distracteurs_trop_faciles"]:
        preferences.append(("distracteurs_plausibles", issue_counts["distracteurs_trop_faciles"]))
    if issue_counts["reponse_incorrecte"]:
        preferences.append(("une_seule_bonne_reponse", issue_counts["reponse_incorrecte"]))
    if issue_counts["question_ambigue"]:
        preferences.append(("eviter_ambiguite", issue_counts["question_ambigue"]))
    if feedbacks:
        preferences.append(("justification_obligatoire", len(feedbacks)))

    return [
        {
            "preference_key": key,
            "preference_text": PREFERENCE_CATALOG[key],
            "evidence_count": count,
            "weight": round(min(1.0, count / max(1, len(feedbacks))), 4),
        }
        for key, count in preferences
    ]


def build_quality_trends(metrics: QualityMetricSource) -> dict:
    return {
        "average_rating": metrics.average_rating,
        "quality_score": metrics.quality_score,
        "difficulty_score": metrics.difficulty_score,
        "hallucination_score": metrics.hallucination_score,
        "incorrect_questions_count": metrics.incorrect_questions_count,
        "incorrect_answers_count": metrics.incorrect_answers_count,
        "ambiguous_questions_count": metrics.ambiguous_questions_count,
        "weak_distractors_count": metrics.weak_distractors_count,
        "hallucination_reports_count": metrics.hallucination_reports_count,
    }
