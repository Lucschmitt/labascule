"""
Fetcher Légifrance via l'API PISTE (OAuth2).
Récupère le texte intégral d'une loi, ordonnance ou décret
à partir de son URL Légifrance ou de son identifiant JORF.

Credentials dans .env :
  PISTE_CLIENT_ID=...
  PISTE_CLIENT_SECRET=...
"""

import os
import re
import urllib.request
import urllib.parse
import urllib.error
import json


OAUTH_URL = "https://sandbox-oauth.piste.gouv.fr/api/oauth/token"
API_BASE  = "https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app"


def _get_token() -> str:
    """Obtient un token OAuth2 client_credentials."""
    client_id     = os.getenv("PISTE_CLIENT_ID")
    client_secret = os.getenv("PISTE_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise EnvironmentError(
            "PISTE_CLIENT_ID et PISTE_CLIENT_SECRET doivent être définis dans .env"
        )

    data = urllib.parse.urlencode({
        "grant_type":    "client_credentials",
        "client_id":     client_id,
        "client_secret": client_secret,
        "scope":         "openid",
        "audience":      "https://api.piste.gouv.fr",
    }).encode()

    req = urllib.request.Request(OAUTH_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("Accept", "application/json")

    with urllib.request.urlopen(req, timeout=15) as resp:
        payload = json.loads(resp.read())

    token = payload.get("access_token")
    if not token:
        raise RuntimeError(f"Token OAuth non reçu : {payload}")
    return token


def _api_post(endpoint: str, body: dict, token: str) -> dict:
    """POST authentifié vers l'API PISTE."""
    url  = f"{API_BASE}{endpoint}"
    data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type",  "application/json")
    req.add_header("Accept",        "application/json")

    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def _extract_jorf_id(url: str) -> str | None:
    """
    Extrait l'identifiant JORF depuis une URL Légifrance.
    Ex : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049040245
         → JORFTEXT000049040245
    """
    m = re.search(r"JORFTEXT\d+", url)
    return m.group(0) if m else None


def _extract_loda_id(url: str) -> str | None:
    """
    Extrait un identifiant LODA/LEGI depuis une URL.
    Ex : https://www.legifrance.gouv.fr/loda/id/LEGIARTI...
    """
    m = re.search(r"(LEGIARTI\d+|LEGITEXT\d+|JORFTEXT\d+)", url)
    return m.group(1) if m else None


def fetch_from_url(url: str) -> tuple[str, dict]:
    """
    Récupère le texte intégral d'un document Légifrance.

    Returns:
        (texte_brut, metadonnees) — texte prêt pour l'Agent 1,
        métadonnées pour préremplir la fiche.
    """
    token = _get_token()

    jorf_id = _extract_jorf_id(url)
    if jorf_id:
        return _fetch_jorf(jorf_id, token, url)

    raise ValueError(
        f"Impossible d'extraire un identifiant Légifrance depuis : {url}\n"
        "Formats supportés : /jorf/id/JORFTEXT..."
    )


def _fetch_jorf(jorf_id: str, token: str, url_origine: str) -> tuple[str, dict]:
    """Récupère un texte JORF par son identifiant."""
    body = {"id": jorf_id}
    data = _api_post("/consult/jorf", body, token)

    # Extraction du texte et des métadonnées
    texte_parts = []
    meta = {}

    # Titre
    titre = data.get("titre") or data.get("titrefull") or ""
    if titre:
        texte_parts.append(titre)
        meta["reference"] = titre

    # Nature / date
    nature = data.get("nature", "")
    date_texte = data.get("dateTexte") or data.get("dateParution") or ""
    meta["type"] = nature.lower() if nature else "loi"
    meta["date_publication"] = date_texte[:10] if date_texte else None
    meta["url_source"] = url_origine
    meta["institution"] = data.get("signataires") or data.get("ministeres") or ""

    # Numéro NOR
    nor = data.get("nor") or ""
    if nor:
        meta["nor"] = nor

    # Articles
    articles = data.get("articles") or []
    for art in articles:
        num  = art.get("num") or art.get("id") or ""
        cont = art.get("content") or art.get("texte") or ""
        if cont:
            # Nettoie le HTML basique
            cont_clean = re.sub(r"<[^>]+>", " ", cont)
            cont_clean = re.sub(r"\s+", " ", cont_clean).strip()
            texte_parts.append(f"Article {num} : {cont_clean}")

    # Exposé des motifs si présent
    expose = data.get("exposeMotifs") or data.get("expose") or ""
    if expose:
        expose_clean = re.sub(r"<[^>]+>", " ", expose)
        expose_clean = re.sub(r"\s+", " ", expose_clean).strip()
        texte_parts.insert(1, f"EXPOSÉ DES MOTIFS :\n{expose_clean[:3000]}")

    texte_brut = "\n\n".join(texte_parts)

    if not texte_brut.strip():
        raise RuntimeError(
            f"L'API PISTE a retourné un document vide pour {jorf_id}.\n"
            f"Réponse brute : {json.dumps(data, ensure_ascii=False)[:500]}"
        )

    return texte_brut, meta


def fetch_raw(url: str) -> str:
    """
    Fallback : récupère le HTML brut d'une URL quelconque
    (pour les textes hors Légifrance).
    """
    headers = {
        "User-Agent": "LaBasculePipeline/0.1 (observatoire-democratique; contact@labascule.eu)"
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        content = resp.read()
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("latin-1")
