# CLAUDE.md - Project 1: NLP Application Using Streamlit

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Mục tiêu 
Xây dựng web sử dụng streamlit cho phép người dùng thực hiện hai tác vụ:
kiểm tra ngôn ngữ, sau đó dịch văn bản và sửa lỗi chính tả

## Tech Stack
- **Python** >= 3.10
- **Streamlit** (giao dien web, chay bang `streamlit run app.py`)
- **langdetect** — phat hien ngon ngu nguon
- **deep-translator** (`GoogleTranslator`) — dich may, can internet
- **pyspellchecker** (`SpellChecker`) — sua chinh ta, khong ho tro tieng Viet
- **nltk** — tokenize/detokenize (`wordpunct_tokenize`, `TreebankWordDetokenizer`)
- **langcodes** — doi ma ngon ngu sang ten doc duoc

## Kien truc

Mot file `app.py`, gom hai phan: helper functions (logic NLP) va UI (Streamlit).

Pipeline:
```
User input -> detect_language() -> [run_translation() | run_spellcheck()] -> Streamlit output
```

Cac ham bat buoc:
- `detect_language(raw) -> str` (tra '' neu < 3 ky tu hoac khong xac dinh)
- `language_name(code) -> str`
- `get_spellchecker(code) -> SpellChecker`  (decorate `@st.cache_resource`)
- `fix_typos(text, code) -> str`  (sua o muc token, giu hoa/thuong va dau cau)
- `run_translation(text, target_code) -> dict`
- `run_spellcheck(text) -> dict`

UI: hai tab `st.tabs(["Dich van ban", "Sua loi chinh ta"])`, moi tab dung `st.form` de gom input
va chi chay khi bam submit. Ket qua luu vao `st.session_state.res_t` / `st.session_state.res_s`
de khong mat khi rerun.

## Quy uoc code

- Dat tat ca cau hinh ngon ngu o dau file (`TARGET_LANGS`, `SPELL_LANGS`) duoi dang dict/set.
- Cac ham `run_*` tra ve dict co khoa `ok` (bool) + `msg` khi loi, de UI xu ly thong nhat.
- Dung `st.success` / `st.warning` / `st.info` / `st.caption` cho trang thai.
- Type hint cho moi ham public.


## Anti-pattern (tranh)

- Khong tao moi `SpellChecker` trong moi lan rerun — bat buoc cache bang `@st.cache_resource`.
- Khong dung `eval` o bat ky dau.
- Khong xoa dau cau khi sua chinh ta; phai detokenize lai dung.
- Khong goi pipeline nang ngoai `st.form` (tranh rerun lien tuc lam goi API lien tuc).

## Test thu cong

- Dich: "Bonjour, comment allez-vous?" -> sang Tieng Viet.
- Chinh ta: "Yesturday, I recieveed a mesage" -> "Yesterday, I received a message".
- Van ban < 3 ky tu -> hien canh bao, khong goi pipeline.
