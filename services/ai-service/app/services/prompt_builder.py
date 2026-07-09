from app.schemas.ai import GenerateMindMapRequest, GenerateQCMRequest, GenerateSummaryRequest, LLMMessage
from app.services.context_builder import build_context_block


SYSTEM_PROMPT = """Tu es un assistant pedagogique expert.
Tu dois repondre uniquement a partir du contexte fourni.
Si une information n'est pas presente dans les sources, ne l'invente pas.
Les citations doivent utiliser les numeros de page fournis. Les chunk_id servent seulement en interne."""


def build_qcm_messages(payload: GenerateQCMRequest, context_chunks) -> list[LLMMessage]:
    context = build_context_block(context_chunks)
    user_prompt = f"""Genere un QCM a partir du contexte.

Contraintes:
- nombre de questions: {payload.number_of_questions}
- options par question: {payload.number_of_options}
- difficulte: {payload.difficulty}
- une seule bonne reponse par question
- distracteurs plausibles, pas absurdes
- justification obligatoire
- source obligatoire avec page et chunk_id
- eviter les formulations ambigues
- JSON strict uniquement: double quotes, virgules entre tous les champs, pas de commentaire, pas de Markdown
- si tu risques de manquer de place, genere moins de texte dans les explications mais garde un JSON complet et valide

Instructions supplementaires:
{payload.extra_instructions or "Aucune"}

Contexte:
{context}

Retourne uniquement un JSON valide avec cette forme:
{{
  "questions": [
    {{
      "question": "...",
      "difficulty": "...",
      "options": [
        {{"label": "A", "text": "...", "is_correct": true}},
        {{"label": "B", "text": "...", "is_correct": false}}
      ],
      "explanation": "...",
      "source": {{"page": 1, "chunk_id": "...", "citation": "..."}}
    }}
  ]
}}
Important: retourne uniquement l'objet JSON. Aucun texte avant ou apres."""
    return [LLMMessage(role="system", content=SYSTEM_PROMPT), LLMMessage(role="user", content=user_prompt)]


def build_summary_messages(payload: GenerateSummaryRequest, context_chunks) -> list[LLMMessage]:
    context = build_context_block(context_chunks)
    user_prompt = f"""Produis un resume pedagogique clair et directement utilisable par un enseignant.

Contraintes:
- style: {payload.style}
- maximum sections: {payload.max_sections}
- chaque section doit avoir un titre explicite
- chaque contenu doit contenir 2 a 3 phrases completes
- resume concis mais coherent: pas de fragments isoles, pas de puces vides, pas de phrase coupee
- organiser les idees par notions importantes, pas par ordre aleatoire du texte
- citer les pages importantes dans sources
- ne pas ajouter d'informations hors contexte
- ne jamais afficher de chunk_id dans le texte
- ne jamais ecrire le mot "Summary" hors du JSON
- si tu risques de manquer de place, reduis le detail au lieu de couper le JSON

Instructions supplementaires:
{payload.extra_instructions or "Aucune"}

Contexte:
{context}

Retourne uniquement un JSON valide:
{{
  "title": "...",
  "sections": [
    {{"heading": "...", "content": "...", "sources": [{{"page": 1}}]}}
  ],
  "key_points": ["...", "..."]
}}
Important: aucune virgule finale, aucun commentaire, aucune ligne hors JSON, aucun Markdown."""
    return [LLMMessage(role="system", content=SYSTEM_PROMPT), LLMMessage(role="user", content=user_prompt)]


def build_mindmap_messages(payload: GenerateMindMapRequest, context_chunks) -> list[LLMMessage]:
    context = build_context_block(context_chunks)
    if payload.output_format == "json":
        output_contract = """Retourne uniquement un JSON valide:
{
  "root": "Sujet principal",
  "nodes": [
    {"id": "n1", "label": "...", "parent_id": null, "source": {"page": 1, "chunk_id": "..."}}
  ]
}"""
    else:
        output_contract = """Retourne uniquement du Mermaid valide, sans bloc Markdown:
mindmap
  root((Sujet principal))
    Branche
      Sous-branche"""

    user_prompt = f"""Construis une mindmap pedagogique riche a partir du contexte.

Contraintes:
- format: {payload.output_format}
- structure hierarchique claire avec un sujet central, 5 a 9 branches principales si le contexte le permet
- chaque branche principale doit avoir 2 a 5 sous-branches utiles
- concepts courts mais explicites
- privilegier les notions importantes, definitions, fonctions, classifications, risques, exemples et relations cause-effet
- eviter une carte plate avec une seule branche
- ne pas recopier des phrases longues du cours
- pas d'informations hors contexte

Instructions supplementaires:
{payload.extra_instructions or "Aucune"}

Contexte:
{context}

{output_contract}"""
    return [LLMMessage(role="system", content=SYSTEM_PROMPT), LLMMessage(role="user", content=user_prompt)]
