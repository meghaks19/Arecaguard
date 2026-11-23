"""ArecaGuard - Streamlit app. Run with:  streamlit run app.py"""
from __future__ import annotations
import base64
import uuid
from pathlib import Path

import cv2
import pandas as pd
import streamlit as st

import config
from core import database as db
from core import predictor
from core.i18n import t
from core.knowledge import DISEASES, SEVERITY_LABEL
from core.preprocess import load_image, quality_warnings

st.set_page_config(page_title="ArecaGuard", page_icon="🌴", layout="centered")
db.init_db()

# Large, touch-friendly text and buttons for use outdoors on a phone.
st.markdown(
    """
    <style>
    html, body, [class*="css"] { font-size: 19px; }
    .stButton > button { width: 100%; padding: 0.9rem 1rem; font-size: 1.15rem; font-weight: 600; }
    .result-card { border-radius: 14px; padding: 1.1rem 1.3rem; margin: 0.5rem 0 1rem 0; }
    .sev-none   { background:#e8f5e9; border-left:8px solid #2e7d32; }
    .sev-low    { background:#fffde7; border-left:8px solid #f9a825; }
    .sev-medium { background:#fff3e0; border-left:8px solid #ef6c00; }
    .sev-high   { background:#ffebee; border-left:8px solid #c62828; }
    .result-card h2 { margin: 0 0 0.2rem 0; color:#1b1b1b; }
    .result-card p  { color:#1b1b1b; margin:0.2rem 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

ss = st.session_state
ss.setdefault("user", None)
ss.setdefault("lang", "en")
ss.setdefault("view", "login")
ss.setdefault("last", None)


# ------------------------------------------------------------------ sidebar
def sidebar():
    if ss.user is None:
        return None
    with st.sidebar:
        choice = st.radio(
            "Language / ಭಾಷೆ", ["English", "ಕನ್ನಡ"],
            index=0 if ss.lang == "en" else 1, horizontal=True,
        )
        ss.lang = "en" if choice == "English" else "kn"
        lang = ss.lang
        st.title("🌴 " + t("app_title", lang))
        st.caption(t("tagline", lang))
        if ss.user is None:
            return None
        st.write(f"👤 {ss.user['name']}")
        pages = [
            ("check", t("nav_check", lang)),
            ("history", t("nav_history", lang)),
            ("guide", t("nav_guide", lang)),
            ("help", t("nav_help", lang)),
        ]
        if ss.user["role"] == "admin":
            pages.append(("admin", t("nav_admin", lang)))
        key = st.radio("menu", [p[0] for p in pages],
                       format_func=dict(pages).get, label_visibility="collapsed")
        if st.button(t("logout", lang)):
            ss.user = None
            ss.last = None
            st.rerun()
        return key


# ------------------------------------------------------------------ login
def _b64_file(name: str) -> str:
    try:
        return base64.b64encode((config.BASE_DIR / "assets" / name).read_bytes()).decode()
    except OSError:
        return ""


def _svg_url(inner: str, stroke: str = "#1b6e22") -> str:
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        f'stroke="{stroke}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{inner}</svg>'
    )
    return "url(data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode() + ")"


ICON_MAIL = _svg_url('<rect x="2.5" y="5" width="19" height="14" rx="2.5"/><path d="M3 7l9 6.5L21 7"/>')
ICON_LOCK = _svg_url('<rect x="5" y="10.5" width="14" height="10" rx="2.5"/><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5"/><circle cx="12" cy="15.5" r="1.2" fill="#1b6e22"/>')
ICON_USER = _svg_url('<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/>')
ICON_LOGIN = _svg_url('<path d="M3 12h11M10 7l5 5-5 5"/><path d="M15 4h3.5A2.5 2.5 0 0 1 21 6.5v11a2.5 2.5 0 0 1-2.5 2.5H15"/>', "#ffffff")


def login_css():
    bg = _b64_file("login_bg.jpg")
    bg_rule = f"url(data:image/jpeg;base64,{bg}) center / cover no-repeat fixed" if bg else "#2e7d32"
    st.markdown(
        f"""<style>
        .stApp, [data-testid="stAppViewContainer"] {{ background: {bg_rule} !important; }}
        [data-testid="stHeader"] {{ background: transparent !important; }}
        [data-testid="stToolbar"], [data-testid="stSidebar"], [data-testid="collapsedControl"],
        [data-testid="stDecoration"], footer {{ display: none !important; }}

        .block-container, [data-testid="stMainBlockContainer"] {{
            max-width: 720px !important; margin: 3vh auto !important;
            padding: 1.4rem 3.3rem 1.2rem 3.3rem !important;
            background: #fcfefb !important; border-radius: 38px;
            box-shadow: 0 14px 44px rgba(0, 55, 10, .28);
        }}
        .login-logo {{ text-align: center; margin: 0; line-height: 0; }}
        .login-logo img {{ width: 100%; max-width: 580px; }}
        .login-title {{ text-align: center; color: #0f6b1c; font-weight: 800; font-size: 2.7rem;
                        margin: .1rem 0 .9rem 0; padding: 0; line-height: 1.15; }}

        /* text boxes */
        [data-testid="stTextInput"] [data-baseweb="input"] {{
            background-color: #fff !important; border: 1.5px solid #cfd9d3 !important;
            border-radius: 16px !important; min-height: 64px;
            box-shadow: 0 2px 7px rgba(0,0,0,.07);
            background-repeat: no-repeat; background-position: 20px center; background-size: 30px;
        }}
        [data-testid="stTextInput"] [data-baseweb="input"] > div {{ background: transparent !important; }}
        [data-testid="stTextInput"] input {{ padding-left: 68px !important; font-size: 1.25rem !important; color: #243; }}
        [data-testid="stTextInput"] input::placeholder {{ color: #8a948e; }}
        .st-key-in_email [data-baseweb="input"], .st-key-r_email [data-baseweb="input"] {{ background-image: {ICON_MAIL}; }}
        .st-key-in_pass  [data-baseweb="input"], .st-key-r_pass  [data-baseweb="input"] {{ background-image: {ICON_LOCK}; }}
        .st-key-r_name   [data-baseweb="input"] {{ background-image: {ICON_USER}; }}

        /* remember me */
        [data-testid="stCheckbox"] p {{ font-size: 1.15rem; font-weight: 500; color: #1c2b20; }}

        /* main green button */
        .st-key-do_login button, .st-key-do_register button {{
            width: 100% !important; min-height: 64px; border: none !important; border-radius: 999px !important;
            background: linear-gradient(180deg, #1f7d16 0%, #0e5d12 100%) !important;
            box-shadow: 0 5px 12px rgba(10, 80, 15, .35);
        }}
        .st-key-do_login button p, .st-key-do_register button p {{
            color: #fff !important; font-size: 1.5rem !important; font-weight: 700 !important;
        }}
        .st-key-do_login button p::before, .st-key-do_register button p::before {{
            content: ""; display: inline-block; width: 30px; height: 30px; margin-right: 14px;
            vertical-align: -7px; background: {ICON_LOGIN} no-repeat center / contain;
        }}

        /* text-link buttons */
        .st-key-forgot button, .st-key-go_register button, .st-key-go_login button {{
            background: transparent !important; border: none !important; box-shadow: none !important;
            padding: 0 !important; min-height: 0 !important; width: auto !important;
        }}
        .st-key-forgot button p, .st-key-go_register button p, .st-key-go_login button p {{
            color: #12701c !important; text-decoration: underline; font-weight: 700; font-size: 1.15rem;
        }}
        .st-key-forgot {{ display: flex; justify-content: flex-end; }}
        .bottom-left {{ text-align: right; font-size: 1.15rem; color: #1c2b20; padding-top: .15rem; font-weight: 500; }}
        .st-key-langbox [role="radiogroup"] {{ justify-content: center; }}
        .st-key-langbox p {{ font-size: .95rem !important; }}
        </style>""",
        unsafe_allow_html=True,
    )


def _logo_header(title: str):
    logo = _b64_file("logo.png")
    if logo:
        st.markdown(
            f'<div class="login-logo"><img src="data:image/png;base64,{logo}" alt="ArecaGuard"></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown("## 🌴 ArecaGuard")
    st.markdown(f'<h1 class="login-title">{title}</h1>', unsafe_allow_html=True)


def _lang_switch():
    pick = st.radio(
        "Language / ಭಾಷೆ", ["English", "ಕನ್ನಡ"], index=0 if ss.lang == "en" else 1,
        horizontal=True, label_visibility="collapsed", key="lang_radio",
    )
    new = "en" if pick == "English" else "kn"
    if new != ss.lang:
        ss.lang = new
        st.rerun()


def _do_login():
    user = db.authenticate(ss.get("in_email", ""), ss.get("in_pass", ""))
    if user:
        ss.user = user
        ss.login_error = False
        ss.show_forgot = False
    else:
        ss.login_error = True


def _do_register():
    name, email, pw = ss.get("r_name", "").strip(), ss.get("r_email", "").strip().lower(), ss.get("r_pass", "")
    if not name or "@" not in email or "." not in email.split("@")[-1] or len(pw) < 6:
        ss.reg_msg = ("warn", "fill_fields")
    elif db.register_user(email, name, email, pw):
        ss.reg_msg = None
        ss.flash = "registered"
        ss.view = "login"
    else:
        ss.reg_msg = ("error", "user_exists")


def _switch_view(view: str):
    ss.view = view
    ss.login_error = False
    ss.reg_msg = None


def login_page():
    lang = ss.lang
    login_css()
    if ss.view == "register":
        _logo_header(t("register", lang))
        st.text_input("n", key="r_name", placeholder=t("name", lang), label_visibility="collapsed")
        st.text_input("e", key="r_email", placeholder=t("ph_email", lang), label_visibility="collapsed")
        st.text_input("p", key="r_pass", type="password", placeholder=t("ph_password", lang),
                      label_visibility="collapsed")
        if ss.get("reg_msg"):
            kind, key = ss.reg_msg
            (st.warning if kind == "warn" else st.error)(t(key, lang))
        st.button(t("create_account", lang), key="do_register", on_click=_do_register)
        c1, c2 = st.columns(2)
        c1.markdown(f'<div class="bottom-left">{t("have_account", lang)}</div>', unsafe_allow_html=True)
        with c2:
            st.button(t("login_title", lang), key="go_login", on_click=_switch_view, args=("login",))
    else:
        _logo_header(t("login_title", lang))
        if ss.get("flash"):
            st.success(t(ss.flash, lang))
        st.text_input("e", key="in_email", placeholder=t("ph_email", lang), label_visibility="collapsed")
        st.text_input("p", key="in_pass", type="password", placeholder=t("ph_password", lang),
                      label_visibility="collapsed", on_change=_do_login)
        c1, c2 = st.columns(2)
        c1.checkbox(t("remember", lang), value=True, key="remember")
        with c2:
            if st.button(t("forgot", lang), key="forgot"):
                ss.show_forgot = not ss.get("show_forgot", False)
        if ss.get("show_forgot"):
            st.info(t("forgot_help", lang))
        if ss.get("login_error"):
            st.error(t("bad_login", lang))
        st.button(t("login_title", lang), key="do_login", on_click=_do_login)
        c1, c2 = st.columns(2)
        c1.markdown(f'<div class="bottom-left">{t("no_account", lang)}</div>', unsafe_allow_html=True)
        with c2:
            st.button(t("signup", lang), key="go_register", on_click=_switch_view, args=("register",))
    with st.container(key="langbox"):
        _lang_switch()


# ------------------------------------------------------------------ check
def show_result(pred, lang):
    d = db.get_disease(pred.disease_id, lang)
    sev = d["severity"]
    pct = round(pred.confidence * 100)

    if pred.is_demo:
        st.error(t("demo_banner", lang))

    st.markdown(
        f"""<div class="result-card sev-{sev}">
        <p>{t("result", lang)}</p>
        <h2>{d["name"]}</h2>
        <p><b>{SEVERITY_LABEL[sev][lang]}</b> &nbsp;·&nbsp; {t("plant_part", lang)}: {d["part"]}</p>
        </div>""",
        unsafe_allow_html=True,
    )

    st.write(f"**{t('confidence', lang)}: {pct}%**")
    st.progress(min(max(pred.confidence, 0.0), 1.0))
    if pred.confidence < config.LOW_CONFIDENCE:
        st.error(t("low_conf", lang))
    elif pred.confidence < config.HIGH_CONFIDENCE:
        st.warning(t("mid_conf", lang))

    # Only give treatment advice when the system is reasonably sure.
    if pred.confidence >= config.LOW_CONFIDENCE:
        st.subheader("🔎 " + t("symptoms", lang))
        st.write(d["symptoms"])
        st.subheader("✅ " + t("what_to_do", lang))
        st.write(d["recommendation"])
        st.subheader("🛡️ " + t("prevention", lang))
        st.write(d["prevention"])

    if len(pred.top) > 1:
        st.subheader(t("other_guesses", lang))
        for did, conf in pred.top[1:]:
            other = db.get_disease(did, lang)
            if other:
                st.write(f"- {other['name']}: {round(conf * 100)}%")

    st.info(t("disclaimer", lang))


def check_page():
    lang = ss.lang
    st.header(t("step1", lang))
    src = st.radio(
        "src", ["upload", "camera"], horizontal=True, label_visibility="collapsed",
        format_func=lambda k: ("📁 " if k == "upload" else "📷 ") + t(k, lang),
    )
    data = None
    if src == "upload":
        f = st.file_uploader(t("upload", lang), type=["jpg", "jpeg", "png"])
        data = f.getvalue() if f else None
    else:
        f = st.camera_input(t("camera", lang))
        data = f.getvalue() if f else None

    if not data:
        with st.expander("💡 " + t("tips_title", lang)):
            for tip in t("tips", lang):
                st.write("- " + tip)
        return

    img = load_image(data)
    if img is None:
        st.error("Could not read this image / ಈ ಚಿತ್ರವನ್ನು ಓದಲಾಗಲಿಲ್ಲ.")
        return
    st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), use_container_width=True)
    for w in quality_warnings(img):
        st.warning(t(w, lang))

    st.header(t("step2", lang))
    have_model = predictor.available()
    demo = False
    if not have_model:
        st.error(t("no_model", lang))
        demo = st.checkbox("Demo mode (sample output, not a real check)")
    if st.button("🔍 " + t("check_btn", lang), disabled=not (have_model or demo)):
        with st.spinner(t("analysing", lang)):
            try:
                pred = predictor.predict(img) if have_model else predictor.demo_prediction()
            except ValueError as exc:
                st.error(str(exc))
                return
        if not pred.is_demo:
            path = config.UPLOAD_DIR / f"{uuid.uuid4().hex}.jpg"
            cv2.imwrite(str(path), img)
            db.save_prediction(ss.user["user_id"], str(path), pred.disease_id, pred.confidence)
        ss.last = pred

    if ss.last is not None:
        show_result(ss.last, lang)


# ------------------------------------------------------------------ history
def history_page():
    lang = ss.lang
    st.header("🕑 " + t("nav_history", lang))
    rows = db.get_history(ss.user["user_id"], lang)
    if not rows:
        st.write(t("history_empty", lang))
        return
    df = pd.DataFrame(rows)
    st.dataframe(
        pd.DataFrame({
            t("date", lang): df["date"],
            t("result", lang): df["disease"],
            t("plant_part", lang): df["part"],
            t("confidence", lang): (df["confidence"] * 100).round().astype(int).astype(str) + "%",
        }),
        use_container_width=True, hide_index=True,
    )
    for r in rows[:5]:
        p = Path(r["image_path"])
        if p.exists():
            st.image(str(p), caption=f"{r['date']} - {r['disease']}", width=220)


# ------------------------------------------------------------------ guide / help
def guide_page():
    lang = ss.lang
    st.header("📖 " + t("nav_guide", lang))
    for did in DISEASES:
        d = db.get_disease(did, lang)
        with st.expander(f"{d['name']}  ·  {SEVERITY_LABEL[d['severity']][lang]}"):
            st.write(f"**{t('plant_part', lang)}:** {d['part']}")
            st.write(f"**{t('symptoms', lang)}:** {d['symptoms']}")
            st.write(f"**{t('what_to_do', lang)}:** {d['recommendation']}")
            st.write(f"**{t('prevention', lang)}:** {d['prevention']}")
    st.info(t("disclaimer", lang))


def help_page():
    lang = ss.lang
    st.header("📸 " + t("tips_title", lang))
    for i, tip in enumerate(t("tips", lang), 1):
        st.write(f"**{i}.** {tip}")


# ------------------------------------------------------------------ admin
def admin_page():
    lang = ss.lang
    st.header("⚙️ " + t("nav_admin", lang))
    tab_u, tab_d = st.tabs([t("manage_users", lang), t("manage_diseases", lang)])
    with tab_u:
        users = db.list_users()
        st.dataframe(pd.DataFrame(users), use_container_width=True, hide_index=True)
        farmers = {f"{u['username']} ({u['name']})": u["user_id"] for u in users if u["role"] != "admin"}
        if farmers:
            pick = st.selectbox(t("username", lang), list(farmers))
            if st.button(t("delete_user", lang)):
                db.delete_user(farmers[pick])
                st.rerun()
    with tab_d:
        did = st.selectbox("Disease", list(DISEASES), format_func=lambda k: DISEASES[k]["name"]["en"])
        raw = db.get_disease_raw(did)
        with st.form(f"edit_{did}"):
            new = {}
            for field in ("symptoms", "recommendation", "prevention"):
                for lg, label in (("en", "English"), ("kn", "ಕನ್ನಡ")):
                    new[(field, lg)] = st.text_area(f"{field} ({label})", raw[field].get(lg, ""), height=110)
            if st.form_submit_button(t("save", lang)):
                db.update_disease(
                    did,
                    {lg: new[("symptoms", lg)] for lg in ("en", "kn")},
                    {lg: new[("prevention", lg)] for lg in ("en", "kn")},
                    {lg: new[("recommendation", lg)] for lg in ("en", "kn")},
                )
                st.success(t("saved", lang))


# ------------------------------------------------------------------ router
page = sidebar()
if ss.user is None:
    login_page()
elif page == "check":
    check_page()
elif page == "history":
    history_page()
elif page == "guide":
    guide_page()
elif page == "help":
    help_page()
elif page == "admin":
    admin_page()
