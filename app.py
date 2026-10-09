# -*- coding: utf-8 -*-
"""
Générateur de prompts photo réalistes anti-détection IA.
Logique pure, sans interface graphique (pour app iOS).
"""

import json
import os
import random


# ============================================================
# 1. CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

FICHIER_POSTURES = os.path.join(DATA_DIR, "postures.txt")
FICHIER_EXPRESSIONS = os.path.join(DATA_DIR, "expressions.txt")
FICHIER_CADRAGES = os.path.join(DATA_DIR, "cadrages.txt")
FICHIER_DECORS = os.path.join(DATA_DIR, "decors.txt")


# ============================================================
# 2. FALLBACKS
# ============================================================

FALLBACK_POSTURES = {
    "C": ["holding phone at arm's length with one arm extended, front camera"],
    "M": ["taking a quick mirror selfie holding phone at chest height"],
    "D": ["standing naturally with weight shifted to one hip, one hand in pocket"],
    "S": ["selfie with the phone held at arm's length, one arm fully extended"],
}

FALLBACK_EXPRESSIONS = [
    ("ALL", "looking directly at the lens with a calm and collected demeanor"),
    ("ALL", "looking sideways with a subtle moody aesthetic"),
    ("ALL", "gazing softly into the distance with a dreamy expression"),
]

FALLBACK_CADRAGES = {
    "C": ["front camera selfie at 30cm from face, 24mm equivalent lens, f/2.2, ISO 400, natural indoor window light"],
    "M": ["mirror selfie at 50cm from mirror, 26mm lens, f/2.2, ISO 400, natural daylight from a window"],
    "D": ["rear camera photo at 6 meters from subject, 100mm telephoto equivalent lens, f/2.8, ISO 200, natural daylight"],
    "S": ["selfie with arm fully extended at 60cm from face, 24mm lens, f/2.2, ISO 400, natural daylight"],
}

FALLBACK_DECORS = [
    ("ALL", "a cozy bedroom with an unmade bed, warm ambient light"),
    ("ALL", "a sunlit modern apartment bedroom with soft white linens"),
    ("ALL", "a bohemian style bedroom with macrame, plants, and fairy lights"),
]


# ============================================================
# 3. CHARGEMENT DES FICHIERS EXTERNES
# ============================================================

def _lire_lignes(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [l.strip() for l in f if l.strip() and not l.strip().startswith("#")]
    except (OSError, UnicodeDecodeError):
        return []


def charger_postures():
    lignes = _lire_lignes(FICHIER_POSTURES)
    if not lignes:
        return FALLBACK_POSTURES
    result = {"C": [], "M": [], "D": [], "S": []}
    for ligne in lignes:
        if "|" not in ligne:
            continue
        posture, balise = ligne.rsplit("|", 1)
        posture = posture.strip()
        balise = balise.strip().upper()
        for lettre in ["C", "M", "D", "S"]:
            if lettre in balise:
                result[lettre].append(posture)
    for k in result:
        if not result[k]:
            result[k] = FALLBACK_POSTURES.get(k, [])
    return result


def charger_expressions():
    lignes = _lire_lignes(FICHIER_EXPRESSIONS)
    if not lignes:
        lignes = [f"{b} | {e}" for b, e in FALLBACK_EXPRESSIONS]
    result = {"C": [], "M": [], "D": [], "S": [], "ALL": []}
    for ligne in lignes:
        balise = "ALL"
        texte = ligne
        if ligne.startswith("[") and "]" in ligne:
            idx = ligne.index("]")
            balise = ligne[1:idx].strip().upper()
            texte = ligne[idx + 1:].strip()
        elif "|" in ligne:
            texte, balise = ligne.rsplit("|", 1)
            texte = texte.strip()
            balise = balise.strip().upper()
        if "ALL" in balise:
            result["ALL"].append(texte)
        for lettre in ["C", "M", "D", "S"]:
            if lettre in balise:
                result[lettre].append(texte)
    for lettre in ["C", "M", "D", "S"]:
        result[lettre] = list(set(result[lettre] + result["ALL"]))
    return result


def charger_cadrages():
    lignes = _lire_lignes(FICHIER_CADRAGES)
    if not lignes:
        lignes = [f"{d} | {l}" for l, lst in FALLBACK_CADRAGES.items() for d in lst]
    result = {"C": [], "M": [], "D": [], "S": []}
    for ligne in lignes:
        balise = None
        texte = ligne
        if ligne.startswith("[") and "]" in ligne:
            idx = ligne.index("]")
            balise = ligne[1:idx].strip().upper()
            texte = ligne[idx + 1:].strip()
        elif "|" in ligne:
            texte, balise = ligne.rsplit("|", 1)
            texte = texte.strip()
            balise = balise.strip().upper()
        if not balise:
            continue
        for lettre in ["C", "M", "D", "S"]:
            if lettre in balise:
                result[lettre].append(texte)
    for k in result:
        if not result[k]:
            result[k] = FALLBACK_CADRAGES.get(k, [])
    return result


def charger_decors():
    lignes = _lire_lignes(FICHIER_DECORS)
    if not lignes:
        lignes = [f"{b} | {d}" for b, d in FALLBACK_DECORS]
    result = {"C": [], "M": [], "D": [], "S": [], "ALL": []}
    for ligne in lignes:
        balise = "ALL"
        texte = ligne
        if ligne.startswith("[") and "]" in ligne:
            idx = ligne.index("]")
            balise = ligne[1:idx].strip().upper()
            texte = ligne[idx + 1:].strip()
        elif "|" in ligne:
            texte, balise = ligne.rsplit("|", 1)
            texte = texte.strip()
            balise = balise.strip().upper()
        if "ALL" in balise:
            result["ALL"].append(texte)
        for lettre in ["C", "M", "D", "S"]:
            if lettre in balise:
                result[lettre].append(texte)
    for lettre in ["C", "M", "D", "S"]:
        result[lettre] = list(set(result[lettre] + result["ALL"]))
    return result


# ============================================================
# 4. LOGIQUE DE GÉNÉRATION
# ============================================================

CADRAGE_VERS_LETTRE = {
    "Miroir": "M",
    "CamAvant": "C",
    "Distance": "D",
    "BrasTendu": "S",
    "Aléatoire": "MIX",
}

POSTURE_CATEGORIES = ["Debout", "Assise", "Allongée", "Mur", "Miroir Actif", "Selfie Bras Tendu"]

MARGE_HAUTE = (
    "CRITICAL COMPOSITION RULE: Leave a large empty space above the "
    "subject's head. The top of the hair must be positioned at "
    "approximately 60-70% from the bottom of the frame, leaving 30-40% "
    "of empty space above. This empty space is intentional and must NOT "
    "be filled with anything. The subject's head must never touch the "
    "top edge of the frame."
)

IDENTITE_RENFORCEE = (
    "CRITICAL: The woman in the generated image must be IDENTICAL to the "
    "reference image. Copy her exact face shape, exact eye shape and color, "
    "exact nose shape, exact lip shape, exact eyebrow shape, exact freckle "
    "pattern on cheeks and nose. Do NOT beautify, do NOT enhance, do NOT "
    "change any feature."
)

ANTI_MAQUILLAGE = (
    "Completely bare face with absolutely zero makeup. No eyeliner, no "
    "mascara, no fake eyelashes, no lipstick, no lip gloss, no foundation, "
    "no powder, no drawn eyebrows, no blush. Her lips must be natural matte "
    "pink, not red, not glossy. Her eyes must have natural short lashes. "
    "Her eyebrows must be natural and unfilled. Her skin must show visible "
    "pores, natural freckles, and slight natural redness on the cheeks."
)

ANTI_DETECTION = (
    "The photo must look like a real unedited photo taken with an iPhone "
    "and pulled directly from a phone's camera roll. Slight ISO noise in "
    "shadow areas, subtle JPEG compression artifacts, natural indoor white "
    "balance. No beauty filter, no skin smoothing, no professional "
    "photography look, no studio lighting, no ring light."
)

FORMAT_VERS_TEXTE = {
    "9:16": "9:16 vertical portrait orientation",
    "3:4": "3:4 portrait orientation",
    "1:1": "1:1 square format",
    "4:5": "4:5 vertical portrait format",
    "16:9": "16:9 horizontal landscape format",
    "2:3": "2:3 traditional portrait format",
}


def generer_prompts(options_json):
    try:
        options = json.loads(options_json) if isinstance(options_json, str) else options_json
    except json.JSONDecodeError:
        return ["Erreur : options JSON invalides."]

    format_sortie = options.get("format", "3:4")
    cadrage_ui = options.get("cadrage", "Miroir")
    tenue = options.get("tenue", "").strip()
    postures_actives = options.get("postures", [])

    if not tenue:
        tenue = "a simple casual outfit"

    if cadrage_ui == "Aléatoire":
        lettres = ["C", "M", "D", "S"]
    else:
        lettres = [CADRAGE_VERS_LETTRE.get(cadrage_ui, "M")]

    postures_dict = charger_postures()
    expressions_dict = charger_expressions()
    cadrages_dict = charger_cadrages()
    decors_dict = charger_decors()

    prompts = []
    for i in range(4):
        lettre_courante = lettres[i % len(lettres)]

        pool_postures = []
        for cat in postures_actives:
            if cat in postures_dict:
                pool_postures.extend(postures_dict[cat])
        if not pool_postures:
            pool_postures = FALLBACK_POSTURES.get(lettre_courante, ["standing naturally"])

        pool_cadrages = cadrages_dict.get(lettre_courante, FALLBACK_CADRAGES.get(lettre_courante, [""]))
        pool_expressions = expressions_dict.get(lettre_courante, [e for _, e in FALLBACK_EXPRESSIONS])
        pool_decors = decors_dict.get(lettre_courante, [d for _, d in FALLBACK_DECORS])

        posture = random.choice(pool_postures)
        cadrage = random.choice(pool_cadrages)
        expression = random.choice(pool_expressions)
        decor = random.choice(pool_decors)

        format_texte = FORMAT_VERS_TEXTE.get(format_sortie, "3:4 portrait orientation")

        prompt = (
            f"A highly detailed, high-resolution photo taken on an iPhone. "
            f"Format: {format_texte}. Single image only.\n\n"
            f"{MARGE_HAUTE}\n\n"
            f"{IDENTITE_RENFORCEE}\n\n"
            f"{ANTI_MAQUILLAGE}\n\n"
            f"{cadrage},\n\n"
            f"featuring her with {expression}, showing her {posture},\n\n"
            f"wearing {tenue},\n\n"
            f"in {decor}.\n\n"
            f"{ANTI_DETECTION}"
        )
        prompts.append(prompt)

    return prompts


def generate_prompts(options_json):
    return generer_prompts(options_json)


def main(options_json):
    return generer_prompts(options_json)


if __name__ == "__main__":
    test = json.dumps({
        "format": "3:4",
        "cadrage": "Miroir",
        "tenue": "a ruby red velvet two-piece set",
        "postures": ["Mur", "Debout"],
    })
    for i, p in enumerate(generer_prompts(test)):
        print(f"=== PROMPT {i+1} ===\n{p}\n")
