"""NLP toolkit: language detection, translation and spellcheck (Streamlit UI)."""

from typing import Any

import langcodes
import nltk
import streamlit as st
from deep_translator import GoogleTranslator
from langdetect import LangDetectException, detect
from nltk.tokenize import wordpunct_tokenize
from nltk.tokenize.treebank import TreebankWordDetokenizer
from spellchecker import SpellChecker

# --------------------------------------------------------------------------
# NLTK data bootstrap
# --------------------------------------------------------------------------


def _ensure_nltk_data() -> None:
    """Ensure required NLTK tokenizer resources are present; download quietly if missing."""
    for resource in ("punkt_tab", "punkt"):
        try:
            nltk.data.find(f"tokenizers/{resource}")
        except LookupError:
            try:
                nltk.download(resource, quiet=True)
            except Exception:
                pass


_ensure_nltk_data()

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

TARGET_LANGS: dict[str, str] = {
    "vi": "Tiếng Việt",
    "en": "English",
    "fr": "Français",
    "es": "Español",
    "de": "Deutsch",
    "ja": "日本語",
    "ko": "한국어",
    "zh-CN": "中文 (简体)",
}

SPELL_LANGS: set[str] = {"en", "es", "fr", "de", "pt", "ru", "ar", "eu", "lv", "nl", "it"}

# --------------------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------------------


def detect_language(raw: str) -> str:
    """Detect the ISO 639-1 language code of raw text.

    Returns '' if raw has fewer than 3 characters, or if langdetect cannot
    determine a language.
    """
    if raw is None:
        return ""
    text = raw.strip()
    if len(text) < 3:
        return ""
    try:
        return detect(text)
    except LangDetectException:
        return ""


def language_name(code: str) -> str:
    """Return a human-readable display name for an ISO language code."""
    if not code:
        return "Không xác định"
    try:
        return langcodes.Language.get(code).display_name()
    except Exception:
        return code.upper()


@st.cache_resource
def get_spellchecker(code: str) -> SpellChecker:
    """Return a cached SpellChecker instance for the given language code."""
    return SpellChecker(language=code)


def _match_case(original: str, correction: str) -> str:
    """Reapply original's casing pattern onto correction."""
    if original.isupper() and len(original) > 1:
        return correction.upper()
    if original[0:1].isupper():
        return correction[0:1].upper() + correction[1:]
    return correction


def fix_typos(text: str, code: str) -> str:
    """Correct misspelled tokens in text using pyspellchecker.

    Tokenizes with wordpunct_tokenize, corrects only alphabetic tokens,
    preserves original casing, and reassembles with
    TreebankWordDetokenizer to keep punctuation spacing natural.
    """
    checker = get_spellchecker(code)
    tokens = wordpunct_tokenize(text)
    corrected_tokens: list[str] = []

    for tok in tokens:
        if tok.isalpha():
            correction = checker.correction(tok.lower())
            if correction is None:
                corrected_tokens.append(tok)
            else:
                corrected_tokens.append(_match_case(tok, correction))
        else:
            corrected_tokens.append(tok)

    return TreebankWordDetokenizer().detokenize(corrected_tokens)


def run_translation(text: str, target_code: str) -> dict[str, Any]:
    """Detect source language and translate text to target_code."""
    if text is None or len(text.strip()) < 3:
        return {"ok": False, "msg": "Vui lòng nhập ít nhất 3 ký tự."}

    source_code = detect_language(text)
    if not source_code:
        return {"ok": False, "msg": "Không thể xác định ngôn ngữ nguồn. Vui lòng nhập văn bản rõ ràng hơn."}

    if source_code == target_code:
        return {"ok": False, "msg": f"Văn bản đã ở ngôn ngữ đích ({language_name(target_code)})."}

    try:
        translated = GoogleTranslator(source=source_code, target=target_code).translate(text)
    except Exception as exc:
        return {"ok": False, "msg": f"Lỗi khi dịch (kiểm tra kết nối internet): {exc}"}

    if not translated:
        return {"ok": False, "msg": "Dịch vụ dịch không trả về kết quả."}

    return {
        "ok": True,
        "msg": "",
        "translated": translated,
        "source_code": source_code,
        "source_name": language_name(source_code),
    }


def run_spellcheck(text: str) -> dict[str, Any]:
    """Detect language and correct spelling if the language is supported."""
    if text is None or len(text.strip()) < 3:
        return {"ok": False, "msg": "Vui lòng nhập ít nhất 3 ký tự."}

    source_code = detect_language(text)
    if not source_code:
        return {"ok": False, "msg": "Không thể xác định ngôn ngữ. Vui lòng nhập văn bản rõ ràng hơn."}

    if source_code not in SPELL_LANGS:
        return {"ok": False, "msg": f"Ngôn ngữ '{language_name(source_code)}' chưa được hỗ trợ sửa chính tả."}

    try:
        corrected = fix_typos(text, source_code)
    except Exception as exc:
        return {"ok": False, "msg": f"Lỗi khi sửa chính tả: {exc}"}

    return {
        "ok": True,
        "msg": "",
        "corrected": corrected,
        "source_code": source_code,
        "source_name": language_name(source_code),
        "changed": corrected != text,
    }


# --------------------------------------------------------------------------
# Streamlit UI
# --------------------------------------------------------------------------

st.set_page_config(page_title="NLP Toolkit", page_icon="🌐", layout="centered")
st.title("Kiểm tra ngôn ngữ, dịch văn bản & sửa lỗi chính tả")

if "res_t" not in st.session_state:
    st.session_state.res_t = None
if "res_s" not in st.session_state:
    st.session_state.res_s = None

tab_translate, tab_spell = st.tabs(["Dịch văn bản", "Sửa lỗi chính tả"])

with tab_translate:
    with st.form("form_translate"):
        text_t = st.text_area("Nhập văn bản cần dịch", key="input_t", height=150)
        target_code = st.selectbox(
            "Ngôn ngữ đích",
            options=list(TARGET_LANGS.keys()),
            format_func=lambda c: TARGET_LANGS[c],
            key="target_lang_select",
        )
        submitted_t = st.form_submit_button("Dịch")

    if submitted_t:
        st.session_state.res_t = run_translation(text_t, target_code)

    result_t = st.session_state.res_t
    if result_t is not None:
        if result_t["ok"]:
            st.caption(f"Ngôn ngữ nguồn phát hiện: {result_t['source_name']} ({result_t['source_code']})")
            st.success(result_t["translated"])
        else:
            st.warning(result_t["msg"])

with tab_spell:
    with st.form("form_spell"):
        text_s = st.text_area("Nhập văn bản cần kiểm tra chính tả", key="input_s", height=150)
        submitted_s = st.form_submit_button("Sửa lỗi chính tả")

    if submitted_s:
        st.session_state.res_s = run_spellcheck(text_s)

    result_s = st.session_state.res_s
    if result_s is not None:
        if result_s["ok"]:
            st.caption(f"Ngôn ngữ phát hiện: {result_s['source_name']} ({result_s['source_code']})")
            if result_s["changed"]:
                st.success(result_s["corrected"])
            else:
                st.info("Không tìm thấy lỗi chính tả nào. " + result_s["corrected"])
        else:
            st.warning(result_s["msg"])
