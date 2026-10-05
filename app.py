# -*- coding: utf-8 -*-
"""
الدرس الأول: مفاهيم أساسية وتقديم البرمجيات الإحصائية
مقياس: البرمجيات الإحصائية المفتوحة — جامعة وهران 2 — قسم العلوم الاقتصادية
تشغيل محلي:  streamlit run app.py
"""

import io

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

# ──────────────────────────────────────────────────────────────
# إعدادات عامة
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="الدرس الأول — البرمجيات الإحصائية المفتوحة",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

INK = "#12303B"
PETROL = "#0E6377"
AMBER = "#E8A33D"
BRICK = "#C8553D"
MIST = "#9FB6C1"

COURSE = {
    "prof": "الأستاذ: ناشي سفيان",
    "univ": "جامعة وهران 2",
    "dept": "قسم العلوم الاقتصادية",
    "year": "2025 - 2026",
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

.stApp { font-family: 'Cairo', sans-serif; }
.stApp, [data-testid="stSidebar"], [data-testid="stMain"] {
    direction: rtl; text-align: right;
}
h1, h2, h3, h4, h5, h6, p, li, label, button, input, textarea {
    font-family: 'Cairo', sans-serif !important;
}
h1, h2, h3 { color: #12303B; font-weight: 800; }

/* عناصر يجب أن تبقى LTR */
[data-baseweb="slider"], code, pre, .stCode, .katex-display, .katex,
[data-testid="stCode"] { direction: ltr !important; text-align: left; }
[data-testid="stSlider"] label, [data-testid="stSlider"] p { direction: rtl; }

/* البطاقة الرئيسية للصفحة */
.hero {
    background: #12303B; color: #F5F8FA;
    padding: 1.4rem 1.6rem; border-radius: 6px;
    border-right: 8px solid #E8A33D; margin-bottom: 1.2rem;
}
.hero { direction: rtl; text-align: right; }
.hero h1 { color: #F5F8FA; margin: 0 0 .3rem 0; padding: 0; font-size: 1.9rem; text-align: right; }
.hero p  { color: #C9D8DF; margin: 0; font-size: 1.02rem; text-align: right; }

[data-testid="stSidebar"] { border-right: 1px solid #D3E0E6; }

.def-box {
    background: #E4EDF1; border-right: 5px solid #0E6377;
    padding: .9rem 1.1rem; border-radius: 4px; margin: .6rem 0 1rem 0;
    line-height: 1.9;
}
.formula-note { color: #4B6B78; font-size: .95rem; }

[data-testid="stMetric"] { text-align: right; }
.meta-line { color:#4B6B78; font-size:.95rem; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# دوال مساعدة
# ──────────────────────────────────────────────────────────────
def header(title: str, subtitle: str = ""):
    sub = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(f'<div class="hero"><h1>{title}</h1>{sub}</div>', unsafe_allow_html=True)


def definition(text: str):
    st.markdown(f'<div class="def-box">{text}</div>', unsafe_allow_html=True)


def show(fig, height=380, title=None):
    layout = dict(
        height=height,
        margin=dict(l=10, r=10, t=50 if title else 20, b=10),
        font=dict(family="Cairo, sans-serif", size=14, color=INK),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.18, x=1, xanchor="right"),
    )
    if title:
        layout["title"] = dict(text=title, x=1, xanchor="right")
    fig.update_layout(**layout)
    fig.update_xaxes(gridcolor="#DCE5EA", zeroline=False)
    fig.update_yaxes(gridcolor="#DCE5EA", zeroline=False)
    st.plotly_chart(fig, width="stretch")


def mini_quiz(key: str, items, options, title="تمرين تطبيقي"):
    """تمرين تصنيف: items = [(نص, الإجابة الصحيحة), ...]"""
    with st.form(key):
        st.markdown(f"**{title}**")
        answers = [
            st.radio(text, options, index=None, horizontal=True, key=f"{key}_{i}")
            for i, (text, _) in enumerate(items)
        ]
        submitted = st.form_submit_button("تحقّق من إجاباتي")
    if submitted:
        score = 0
        for (text, correct), ans in zip(items, answers):
            if ans is None:
                st.warning(f"لم تُجب عن: {text}")
            elif ans == correct:
                score += 1
                st.success(f"✔ {text} ← {correct}")
            else:
                st.error(f"✘ {text} ← الصحيح: {correct}")
        st.markdown(f"**النتيجة: {score} / {len(items)}**")


def new_seed(key: str):
    st.session_state[key] = st.session_state.get(key, 0) + 1


# ──────────────────────────────────────────────────────────────
# 0) الرئيسية
# ──────────────────────────────────────────────────────────────
def page_home():
    header(
        "الدرس الأول: مفاهيم أساسية وتقديم البرمجيات الإحصائية",
        f"{COURSE['prof']} — {COURSE['univ']} — {COURSE['dept']} — {COURSE['year']}",
    )
    st.markdown(
        "هذا الدرس التفاعلي يرافق ملف الدرس الأول. في كل محور ستجد **الفكرة** "
        "مختصرة ثم **تجربة** تغيّر فيها القيم بنفسك وتلاحظ النتيجة مباشرة."
    )
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown("#### محاور الدرس")
        st.markdown(
            """
1. **المجتمع الإحصائي**: المحدود وغير المحدود، وسحب عينة.
2. **الإحصاء الوصفي والإحصاء الاستدلالي**: مقاييس، فترات ثقة، اختبار فرضية.
3. **مدخل للاقتصاد القياسي**: الأهداف والمهام.
4. **النموذج القياسي**: الثابت والمعامل والحد العشوائي، وأنواع النماذج.
5. **البيانات**: مصادرها وأنواعها (زمنية، مقطعية، مجمّعة، بانل).
6. **تلخيص البيانات والبرمجيات الإحصائية**: EViews وSPSS وStata وR وGAUSS وPython.
7. **اختبار ختامي** لتقييم الفهم.
            """
        )
    with c2:
        with st.container(border=True):
            st.markdown("#### كيف تستعمل الدرس؟")
            st.markdown(
                "- تنقّل بين المحاور من القائمة الجانبية.\n"
                "- حرّك المنزلقات وانظر كيف تتغير الرسوم.\n"
                "- أجب عن التمارين قبل قراءة التصحيح.\n"
                "- في المحور السادس يمكنك رفع ملف CSV خاص بك."
            )


# ──────────────────────────────────────────────────────────────
# 1) المجتمع الإحصائي
# ──────────────────────────────────────────────────────────────
@st.cache_data
def make_workers(n=500):
    rng = np.random.default_rng(42)
    wages = np.clip(rng.normal(60000, 15000, n), 25000, None).round(-2)
    return wages


def page_population():
    header("1) المجتمع الإحصائي", "مجموعة الأفراد أو العناصر محل الدراسة")
    definition(
        "<b>المجتمع الإحصائي</b> هو مجموعة الأفراد محل الدراسة التي تشترك في خصائص معينة، "
        "وهو المجموعة التي تُختار منها العيّنات لدراسة خصائص محددة. "
        "ينقسم إلى نوعين: <b>مجتمع محدود</b> و<b>مجتمع غير محدود</b>."
    )

    t1, t2, t3 = st.tabs(["المجتمع المحدود", "المجتمع غير المحدود", "تجربة: سحب عيّنة"])

    with t1:
        st.markdown(
            "المجتمع المحدود يمكن **حصر** جميع أفراده أو عناصره. أمثلة:\n\n"
            "- **العاملون في مؤسسة معينة**: مؤسسة اقتصادية فيها 500 عامل.\n"
            "- **الطلبة في جامعة**: عدد المسجلين في جامعة معينة عدد يمكن حصره.\n"
            "- **المنتجات في مخزون مصنع**: مصنع لديه 500 وحدة من منتج معين."
        )
    with t2:
        st.markdown(
            "المجتمع غير المحدود لا يمكن حصر أفراده، عملياً أو نظرياً. أمثلة:\n\n"
            "- **عدد النجوم في السماء**.\n"
            "- **المستهلكون المحتملون لمنتج** على مستوى بلد كبير أو العالم.\n"
            "- **الأرقام العشوائية الممكنة**."
        )
        st.caption("النوعان يحدّدان طريقة جمع البيانات وأدوات التحليل المناسبة لكل حالة.")

    with t3:
        wages = make_workers()
        st.markdown(
            "لدينا مجتمع محدود: **500 عامل** في مؤسسة اقتصادية (كل نقطة = عامل). "
            "اختر حجم العيّنة وانظر كم يقترب متوسط العيّنة من متوسط المجتمع."
        )
        c1, c2 = st.columns(2)
        n = c1.slider("حجم العيّنة (n)", 5, 200, 30, 5)
        if "seed_pop" not in st.session_state:
            st.session_state.seed_pop = 0
        c2.write("")
        c2.button("اسحب عيّنة جديدة", on_click=new_seed, args=("seed_pop",))

        rng = np.random.default_rng(1000 + st.session_state.seed_pop)
        idx = rng.choice(len(wages), n, replace=False)
        mask = np.zeros(len(wages), dtype=bool)
        mask[idx] = True

        cols_n = 25
        xs = np.arange(len(wages)) % cols_n
        ys = np.arange(len(wages)) // cols_n
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=xs[~mask], y=ys[~mask], mode="markers", name="باقي المجتمع",
            marker=dict(size=9, color=MIST),
            hovertext=wages[~mask], hoverinfo="text"))
        fig.add_trace(go.Scatter(
            x=xs[mask], y=ys[mask], mode="markers", name="العيّنة المسحوبة",
            marker=dict(size=11, color=AMBER, line=dict(width=1, color=INK)),
            hovertext=wages[mask], hoverinfo="text"))
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False, autorange="reversed")
        show(fig, height=330)

        m1, m2, m3 = st.columns(3)
        m1.metric("متوسط المجتمع (μ)", f"{wages.mean():,.0f} دج")
        m2.metric("متوسط العيّنة (x̄)", f"{wages[mask].mean():,.0f} دج",
                  delta=f"{wages[mask].mean() - wages.mean():,.0f}", delta_color="off")
        m3.metric("نسبة المعاينة", f"{n / len(wages):.0%}")
        st.caption("الفرق بين x̄ وμ يسمى خطأ المعاينة؛ يتناقص عادةً كلما كبر حجم العيّنة.")

    st.divider()
    mini_quiz(
        "q_pop",
        [
            ("عمال مؤسسة اقتصادية يبلغ عددهم 500", "محدود"),
            ("عدد النجوم في السماء", "غير محدود"),
            ("وحدات منتج في مخزون مصنع", "محدود"),
            ("المستهلكون المحتملون لمنتج على مستوى العالم", "غير محدود"),
            ("الطلبة المسجلون في جامعة وهران 2", "محدود"),
        ],
        ["محدود", "غير محدود"],
        "صنّف المجتمعات التالية",
    )


# ──────────────────────────────────────────────────────────────
# 2) الإحصاء الوصفي والاستدلالي
# ──────────────────────────────────────────────────────────────
def page_desc_inf():
    header("2) الإحصاء الوصفي والإحصاء الاستدلالي",
           "وصف ما لدينا من بيانات، أو التعميم منه على مجتمع أكبر")
    t1, t2, t3, t4 = st.tabs(
        ["الإحصاء الوصفي", "الإحصاء الاستدلالي", "المقارنة", "الفرضيات الإحصائية"])

    # ---------- وصفي
    with t1:
        definition(
            "<b>الإحصاء الوصفي</b> فرع يهتم بوصف البيانات وتلخيصها ومعرفة أهم خصائصها وتوزيعها، "
            "باستعمال الجداول والرسوم البيانية ومقاييس النزعة المركزية (الوسط، الوسيط، المنوال) "
            "ومقاييس التشتت (التباين، الانحراف المعياري). لا يحاول التعميم على مجتمع أكبر."
        )
        st.markdown("**تجربة:** علامات طلبة في امتحان (من 20). غيّر المعطيات وراقب المقاييس.")
        c1, c2, c3 = st.columns(3)
        mu = c1.slider("متوسط العلامات", 5.0, 16.0, 10.5, 0.5)
        sd = c2.slider("تشتت العلامات (الانحراف المعياري)", 1.0, 5.0, 3.0, 0.5)
        n = c3.slider("عدد الطلبة", 10, 500, 60, 10)

        rng = np.random.default_rng(7)
        x = np.clip(np.round(rng.normal(mu, sd, n)), 0, 20)
        s = pd.Series(x)
        mode = s.mode()
        m = st.columns(6)
        m[0].metric("الوسط", f"{s.mean():.2f}")
        m[1].metric("الوسيط", f"{s.median():.1f}")
        m[2].metric("المنوال", f"{mode.min():.0f}")
        m[3].metric("التباين", f"{s.var(ddof=1):.2f}")
        m[4].metric("الانحراف المعياري", f"{s.std(ddof=1):.2f}")
        m[5].metric("المدى", f"{s.max() - s.min():.0f}")

        cA, cB = st.columns([3, 2])
        with cA:
            fig = go.Figure(go.Histogram(
                x=x, xbins=dict(start=-0.5, end=20.5, size=1),
                marker_color=PETROL, opacity=.85, name="التكرار"))
            fig.add_vline(x=s.mean(), line_color=AMBER, line_width=3,
                          annotation_text="الوسط", annotation_position="top")
            fig.add_vline(x=s.median(), line_color=BRICK, line_dash="dash", line_width=2,
                          annotation_text="الوسيط", annotation_position="bottom")
            fig.update_xaxes(title="العلامة", range=[-1, 21])
            fig.update_yaxes(title="عدد الطلبة")
            show(fig, 340, "المدرج التكراري")
        with cB:
            fig = go.Figure(go.Box(x=x, marker_color=PETROL, boxpoints="outliers", name=""))
            fig.update_xaxes(title="العلامة", range=[-1, 21])
            show(fig, 340, "الصندوق ذو الشاربين")
        with st.expander("الجدول التكراري"):
            freq = s.value_counts().sort_index().rename_axis("العلامة").reset_index(name="التكرار")
            freq["التكرار النسبي %"] = (freq["التكرار"] / n * 100).round(1)
            st.dataframe(freq, hide_index=True, width="stretch")
        st.markdown("**أمثلة:** حساب متوسط درجات الطلبة، جدول بعدد الطلبة في كل كلية، "
                    "رسم تطور أسعار النفط خلال العام الماضي.")

    # ---------- استدلالي
    with t2:
        definition(
            "<b>الإحصاء الاستدلالي</b> يستخدم بيانات عيّنة لمعرفة الخصائص العامة لمجتمع أكبر، "
            "ويعتمد على اختبار الفرضيات بهدف اتخاذ قرارات."
        )
        st.markdown(
            "**تجربة فترة الثقة:** مجتمع علاماته متوسطه الحقيقي μ = 10.5 وتشتته 3 "
            "(نحن نعرفه هنا، أما الباحث فلا). نسحب عدة عيّنات، ونبني من كل عيّنة فترة ثقة لـ μ. "
            "الفترة الحمراء أخطأت في التقاط μ."
        )
        c1, c2, c3 = st.columns(3)
        n = c1.slider("حجم كل عيّنة", 5, 200, 25, 5, key="ci_n")
        conf = c2.radio("مستوى الثقة", [90, 95, 99], index=1, horizontal=True,
                        format_func=lambda v: f"{v}%")
        k = c3.slider("عدد العيّنات", 10, 100, 50, 10)
        if "seed_ci" not in st.session_state:
            st.session_state.seed_ci = 0
        st.button("اسحب عيّنات جديدة", on_click=new_seed, args=("seed_ci",), key="btn_ci")

        mu_true, sigma = 10.5, 3.0
        rng = np.random.default_rng(500 + st.session_state.seed_ci)
        data = rng.normal(mu_true, sigma, (k, n))
        means = data.mean(axis=1)
        se = data.std(axis=1, ddof=1) / np.sqrt(n)
        tcrit = stats.t.ppf(0.5 + conf / 200, n - 1)
        lo, hi = means - tcrit * se, means + tcrit * se
        ok = (lo <= mu_true) & (mu_true <= hi)
        idx = np.arange(1, k + 1)

        fig = go.Figure()
        for flag, color, name in [(True, PETROL, "تحتوي على μ"), (False, BRICK, "لا تحتوي على μ")]:
            sel = ok == flag
            fig.add_trace(go.Scatter(
                x=means[sel], y=idx[sel], mode="markers", name=name,
                marker=dict(color=color, size=6),
                error_x=dict(type="data", symmetric=False,
                             array=(hi - means)[sel], arrayminus=(means - lo)[sel],
                             color=color, thickness=1.6, width=0)))
        fig.add_vline(x=mu_true, line_color=AMBER, line_width=3,
                      annotation_text="μ الحقيقي", annotation_position="top")
        fig.update_xaxes(title="متوسط العلامات")
        fig.update_yaxes(title="رقم العيّنة", autorange="reversed")
        show(fig, 420)
        a, b = st.columns(2)
        a.metric("فترات التقطت μ", f"{ok.sum()} من {k}")
        b.metric("نسبة التغطية الفعلية", f"{ok.mean():.0%}",
                 help=f"المتوقع على المدى الطويل ≈ {conf}%")
        st.caption("كلما ارتفع مستوى الثقة اتسعت الفترات؛ وكلما كبر حجم العيّنة ضاقت.")
        st.markdown("**أمثلة:** التنبؤ بنتائج انتخابات من استطلاع رأي عيّنة من الناخبين، "
                    "اختبار جدوى دواء جديد من تجربة سريرية على عيّنة من المرضى، "
                    "معرفة هل يوجد فرق بين متوسط أداء طلبة ثلاثة تخصصات.")

    # ---------- مقارنة
    with t3:
        df = pd.DataFrame({
            "الخاصية": ["الهدف", "النتائج", "الاستدلال", "البيانات"],
            "الإحصاء الوصفي": ["وصف البيانات وتلخيصها", "تلخيص البيانات", "لا", "بيانات العيّنة (أو المجتمع كله)"],
            "الإحصاء الاستدلالي": ["التعميم على مجتمع أكبر", "اختبارات الفرضيات", "نعم", "عيّنة من المجتمع"],
        })
        st.dataframe(df, hide_index=True, width="stretch")
        mini_quiz(
            "q_di",
            [
                ("حساب متوسط درجات طلبة قسم معين", "وصفي"),
                ("اختبار هل يختلف متوسط أداء ثلاثة تخصصات", "استدلالي"),
                ("رسم منحنى تطور أسعار النفط", "وصفي"),
                ("تقدير نتيجة انتخابات من عيّنة ناخبين", "استدلالي"),
            ],
            ["وصفي", "استدلالي"],
            "هل هذه العملية وصفية أم استدلالية؟",
        )

    # ---------- فرضيات
    with t4:
        definition(
            "<b>الفرضية الإحصائية</b> ادّعاء حول معلمة أو علاقة في المجتمع نختبره بالاعتماد على عيّنة. "
            "نضع فرضية العدم <b>H₀</b> (لا فرق / لا علاقة) والفرضية البديلة <b>H₁</b>، "
            "ثم نقرر: هل تقدّم العيّنة دليلاً كافياً لرفض H₀ عند مستوى معنوية α؟"
        )
        st.latex(r"H_0:\ \mu=\mu_0 \qquad H_1:\ \mu\neq\mu_0")
        st.markdown(
            "**تجربة:** هل متوسط علامات الطلبة يختلف عن القيمة المرجعية μ₀؟ "
            "المتوسط الحقيقي في المجتمع يحدده المنزلق (غير معروف للباحث)."
        )
        c1, c2, c3, c4 = st.columns(4)
        mu0 = c1.slider("القيمة المرجعية μ₀", 8.0, 12.0, 10.0, 0.5)
        mu_t = c2.slider("المتوسط الحقيقي μ", 8.0, 13.0, 11.0, 0.25)
        n = c3.slider("حجم العيّنة", 5, 200, 30, 5, key="h_n")
        alpha = c4.radio("مستوى المعنوية α", [0.01, 0.05, 0.10], index=1, horizontal=True)
        if "seed_h" not in st.session_state:
            st.session_state.seed_h = 0
        st.button("اسحب عيّنة جديدة", on_click=new_seed, args=("seed_h",), key="btn_h")

        rng = np.random.default_rng(900 + st.session_state.seed_h)
        sample = rng.normal(mu_t, 3.0, n)
        res = stats.ttest_1samp(sample, mu0)
        tstat, pval, dfree = float(res.statistic), float(res.pvalue), n - 1
        crit = stats.t.ppf(1 - alpha / 2, dfree)

        grid = np.linspace(-5, 5, 500)
        pdf = stats.t.pdf(grid, dfree)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=grid, y=pdf, mode="lines", line=dict(color=INK, width=2), name="توزيع t تحت H₀"))
        for side, name in [(grid <= -crit, "منطقة الرفض"), (grid >= crit, None)]:
            fig.add_trace(go.Scatter(x=grid[side], y=pdf[side], fill="tozeroy", mode="none",
                                     fillcolor="rgba(200,85,61,.45)", name=name or "",
                                     showlegend=name is not None))
        fig.add_vline(x=float(np.clip(tstat, -5, 5)), line_color=AMBER, line_width=3,
                      annotation_text=f"t = {tstat:.2f}")
        fig.update_xaxes(title="قيمة إحصائية الاختبار t")
        fig.update_yaxes(showticklabels=False)
        show(fig, 320)

        m = st.columns(4)
        m[0].metric("متوسط العيّنة", f"{sample.mean():.2f}")
        m[1].metric("إحصائية t", f"{tstat:.2f}")
        m[2].metric("القيمة الحرجة", f"±{crit:.2f}")
        m[3].metric("p-value", f"{pval:.4f}")
        if pval < alpha:
            st.error(f"p = {pval:.4f} < α = {alpha}: **نرفض H₀**؛ العيّنة تدل على أن μ ≠ {mu0}.")
        else:
            st.info(f"p = {pval:.4f} ≥ α = {alpha}: **لا نرفض H₀**؛ لا يوجد دليل كافٍ على أن μ ≠ {mu0}.")
        st.caption("جرّب: اجعل μ = μ₀ ثم اسحب عدة عيّنات (قد يظهر رفض خاطئ بنسبة ≈ α)؛ "
                   "ثم ابعد μ عن μ₀ وكبّر العيّنة لترى كيف تزداد قدرة الاختبار.")


# ──────────────────────────────────────────────────────────────
# 3) مدخل للاقتصاد القياسي
# ──────────────────────────────────────────────────────────────
def page_intro_econometrics():
    header("3) مدخل للاقتصاد القياسي", "اقتصاد + إحصاء + رياضيات + بيانات")
    definition(
        "<b>الاقتصاد القياسي</b> فرع من الاقتصاد يجمع بين الأساليب الإحصائية والنظرية الاقتصادية "
        "والنماذج الرياضية لتحليل الظواهر الاقتصادية وفهمها ووصفها والتنبؤ بها، اعتماداً على البيانات المتاحة."
    )

    st.markdown("### الأهداف الثلاثة")
    c1, c2, c3 = st.columns(3)
    with c1.container(border=True):
        st.markdown("#### 1. تحليل واختبار النظريات")
        st.write("التحقق من الفرضيات والنظريات الاقتصادية بالاختبارات وصياغة معادلات "
                 "توضّح القوة التفسيرية للنظرية المدروسة.")
    with c2.container(border=True):
        st.markdown("#### 2. اتخاذ القرارات ورسم السياسات")
        st.write("تقديرات كمية ذات دلالة اقتصادية تساعد رجال الأعمال والحكومات في وضع "
                 "السياسات الاقتصادية واتخاذ القرار.")
    with c3.container(border=True):
        st.markdown("#### 3. التنبؤ بالقيم الاقتصادية")
        st.write("استعمال نموذج مقدَّر ومختبَر لتوقّع سلوك المتغيرات مستقبلاً. مثال: توقّع "
                 "البطالة في ضوء نسبة التضخم التي تسمح بها الدولة.")

    st.markdown("### مهام الاقتصاد القياسي")
    steps = {
        "1. تحديد النموذج": "تمثيل العلاقة بين المتغيرات الاقتصادية في **نموذج رياضي عشوائي**، "
                            "بوضع فروض النظرية الاقتصادية في معادلة.",
        "2. تقدير المعاملات": "جمع الإحصاءات المناسبة بالدقة المطلوبة، ثم استعمال الأساليب "
                              "الإحصائية لتقدير معالم النموذج.",
        "3. اختبار النموذج": "هل يمثل النموذج الواقع فعلاً أم يلزم نموذج آخر؟ يعتمد ذلك على "
                             "**معايير اقتصادية** (انسجام إشارات وقيم المعاملات مع النظرية) "
                             "و**اختبارات إحصائية** لفروض النموذج، خاصة المتعلقة بالحد العشوائي.",
    }
    pick = st.radio("اختر مهمة:", list(steps), horizontal=True, label_visibility="collapsed")
    st.info(steps[pick])

    st.divider()
    mini_quiz(
        "q_goal",
        [
            ("باحث يريد معرفة هل ينطبق قانون الطلب على سلعة معينة", "اختبار النظريات"),
            ("وزارة المالية تريد معرفة أثر رفع الضريبة على الاستهلاك", "رسم السياسات"),
            ("مؤسسة تريد تقدير مبيعاتها للسنة القادمة", "التنبؤ"),
            ("التحقق من أن الميل الحدي للاستهلاك محصور بين 0 و1", "اختبار النظريات"),
        ],
        ["اختبار النظريات", "رسم السياسات", "التنبؤ"],
        "أي هدف من أهداف الاقتصاد القياسي تخدم الحالات التالية؟",
    )


# ──────────────────────────────────────────────────────────────
# 4) النموذج القياسي
# ──────────────────────────────────────────────────────────────
def page_model():
    header("4) النموذج القياسي", "تعبير رمزي عن العلاقة الاقتصادية مع حدّ عشوائي")
    definition(
        "<b>النموذج القياسي</b> نموذج اقتصادي يعبّر رمزياً عن طبيعة العلاقات الاقتصادية للظاهرة المدروسة "
        "باستخدام العوامل المؤثرة فيها، ويتضمن عاملاً غير محدد هو <b>الحد العشوائي</b>."
    )
    st.latex(r"y_i = \alpha\,X_i + b + U_i")

    t1, t2, t3, t4 = st.tabs(["عناصر النموذج", "ورشة: النموذج والحد العشوائي",
                              "أنواع النماذج", "مراحل بناء النموذج"])

    with t1:
        c1, c2, c3 = st.columns(3)
        with c1.container(border=True):
            st.markdown("**العنصر الثابت (b)**")
            st.write("قيمة المتغير التابع عندما يكون المتغير المستقل صفراً؛ "
                     "هو الجزء الذي يقطع عنده خط النموذج المحور العمودي.")
        with c2.container(border=True):
            st.markdown("**العنصر السلوكي (α)**")
            st.write("معامل الانحدار الملازم للمتغير المستقل، وهو ميل الخط: مقدار تغيّر "
                     "المتغير التابع عندما يتغير المستقل بوحدة واحدة. سُمّي سلوكياً لأنه يحدد سلوك الظاهرة.")
        with c3.container(border=True):
            st.markdown("**الحد العشوائي (Uᵢ)**")
            st.write("يضم أثر كل العوامل غير المدرجة في النموذج أو غير المعروفة. "
                     "يحوّل العلاقة الدقيقة إلى علاقة **احتمالية**.")
        st.caption("ملاحظة: في كثير من المراجع يُرمز للثابت بـ β₀ وللمعامل بـ β₁؛ المضمون واحد.")

    with t2:
        st.markdown("غيّر المعاملات وراقب: ماذا يحدث عندما يكون تشتت الحد العشوائي صفراً؟ وعندما يكبر؟")
        c1, c2, c3, c4 = st.columns(4)
        a = c1.slider("المعامل السلوكي α", -3.0, 3.0, 1.5, 0.1)
        b = c2.slider("الثابت b", -10.0, 20.0, 5.0, 0.5)
        sig = c3.slider("تشتت الحد العشوائي σ", 0.0, 10.0, 3.0, 0.5)
        n = c4.slider("عدد المشاهدات", 10, 200, 50, 10, key="m_n")
        resid = st.checkbox("إظهار البواقي (المسافات إلى خط الانحدار المقدَّر)")

        rng = np.random.default_rng(11)
        x = rng.uniform(0, 10, n)
        u = rng.normal(0, 1, n) * sig
        y = a * x + b + u
        a_hat, b_hat = np.polyfit(x, y, 1)
        fit = a_hat * x + b_hat
        sst = ((y - y.mean()) ** 2).sum()
        r2 = 1 - ((y - fit) ** 2).sum() / sst if sst > 0 else float("nan")

        grid = np.array([0, 10])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode="markers", name="المشاهدات",
                                 marker=dict(color=PETROL, size=8)))
        fig.add_trace(go.Scatter(x=grid, y=a * grid + b, mode="lines", name="العلاقة الحقيقية (بدون u)",
                                 line=dict(color=AMBER, width=3)))
        fig.add_trace(go.Scatter(x=grid, y=a_hat * grid + b_hat, mode="lines", name="الخط المقدَّر",
                                 line=dict(color=BRICK, width=2, dash="dash")))
        if resid:
            xs = np.ravel(np.column_stack([x, x, np.full(n, np.nan)]))
            ys = np.ravel(np.column_stack([y, fit, np.full(n, np.nan)]))
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name="البواقي",
                                     line=dict(color=MIST, width=1)))
        fig.update_xaxes(title="X (المتغير المستقل)")
        fig.update_yaxes(title="Y (المتغير التابع)")
        show(fig, 400)

        m = st.columns(4)
        m[0].metric("α الحقيقي ← المقدَّر", f"{a:.2f} ← {a_hat:.2f}")
        m[1].metric("b الحقيقي ← المقدَّر", f"{b:.2f} ← {b_hat:.2f}")
        m[2].metric("R²", "—" if np.isnan(r2) else f"{r2:.3f}")
        m[3].metric("σ للحد العشوائي", f"{sig:.1f}")
        if sig == 0:
            st.success("σ = 0: لا حد عشوائي، فالنقاط على خط واحد؛ علاقة **دقيقة** (غير واقعية في الاقتصاد).")
        else:
            st.info("مع وجود الحد العشوائي تتبعثر النقاط حول الخط؛ علاقة **احتمالية**. "
                    "زيادة σ تُنقص R² وتُبعد التقدير عن القيم الحقيقية.")

    with t3:
        st.markdown("##### حسب الخطية")
        p = st.slider("قوة المتغير المستقل p في  y = b + a·xᵖ", 0.5, 3.0, 1.0, 0.1)
        xg = np.linspace(0, 10, 100)
        fig = go.Figure(go.Scatter(x=xg, y=2 + 0.5 * xg ** p, mode="lines",
                                   line=dict(color=PETROL, width=3)))
        fig.update_xaxes(title="X")
        fig.update_yaxes(title="Y")
        show(fig, 280)
        if p == 1:
            st.success("p = 1: **نموذج خطي** (قوة المتغير المستقل تساوي الواحد؛ العلاقة خط مستقيم).")
        else:
            st.warning(f"p = {p}: **نموذج غير خطي** (المتغير المستقل مرفوع إلى أس).")

        st.markdown("##### حسب الزمن")
        lam = st.slider("أثر التخلف الزمني λ  في  yₜ = β·xₜ + λ·yₜ₋₁", 0.0, 0.95, 0.6, 0.05)
        T, beta = 30, 1.0
        xt = np.where(np.arange(T) < 8, 0.0, 1.0)
        y_s = beta * xt
        y_d = np.zeros(T)
        for t in range(T):
            y_d[t] = beta * xt[t] + (lam * y_d[t - 1] if t > 0 else 0)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=np.arange(T), y=xt, mode="lines", name="x: زيادة دائمة بوحدة",
                                 line=dict(color=MIST, shape="hv", dash="dot")))
        fig.add_trace(go.Scatter(x=np.arange(T), y=y_s, mode="lines", name="نموذج ساكن (λ = 0)",
                                 line=dict(color=AMBER, width=3, shape="hv")))
        fig.add_trace(go.Scatter(x=np.arange(T), y=y_d, mode="lines+markers", name=f"نموذج حركي (λ = {lam})",
                                 line=dict(color=PETROL, width=3)))
        fig.update_xaxes(title="الزمن t")
        fig.update_yaxes(title="الأثر على y")
        show(fig, 320)
        st.caption("النموذج الساكن يتفاعل فوراً ولا يحمل ذاكرة؛ أما الحركي فيأخذ التخلف الزمني بالحسبان "
                   "فيتراكم الأثر تدريجياً (يستقر عند β/(1−λ)) وهو أقرب إلى الواقع.")

    with t4:
        st.markdown("المراحل المعتادة لبناء النموذج القياسي، انقر على كل مرحلة:")
        stages = [
            ("1. التوصيف (تحديد النموذج)",
             "صياغة النموذج الرياضي العشوائي انطلاقاً من النظرية الاقتصادية: تحديد المتغيرات والشكل الدالي وإشارات المعاملات المتوقعة."),
            ("2. جمع البيانات",
             "الحصول على الإحصاءات المناسبة بالدقة المطلوبة (سلاسل زمنية، مقطعية، بانل...)."),
            ("3. التقدير",
             "تقدير معالم النموذج بالأساليب الإحصائية المناسبة (وهنا يأتي دور البرمجيات الإحصائية)."),
            ("4. التقييم والاختبار",
             "اختبار الانسجام مع النظرية الاقتصادية ومع فروض النموذج، خاصة المتعلقة بالحد العشوائي؛ وإن لم ينجح يُعاد التوصيف."),
            ("5. الاستخدام",
             "التنبؤ وتحليل السياسات واتخاذ القرار."),
        ]
        for title, text in stages:
            with st.expander(title):
                st.write(text)
        st.caption("عدّل هذه المراحل في app.py لتطابق المخطط الوارد في ملف الدرس عندك.")


# ──────────────────────────────────────────────────────────────
# 5) البيانات
# ──────────────────────────────────────────────────────────────
def page_data():
    header("5) البيانات (Data)", "مجموعة من المشاهدات أو الملاحظات")
    definition(
        "<b>البيانات</b> مجموعة من المشاهدات أو الملاحظات: إما <b>كمّية</b> (الأعمار، الأوزان) "
        "أو <b>وصفية/نوعية</b> (لون البشرة، الجنس)."
    )
    t1, t2, t3, t4, t5 = st.tabs(
        ["المصادر", "السلسلة الزمنية", "البيانات المقطعية", "المجمّعة وبانل", "تمرين"])

    with t1:
        c1, c2 = st.columns(2)
        with c1.container(border=True):
            st.markdown("#### المصدر الأول: تاريخي")
            st.markdown("- السجلات المحفوظة\n- البيانات الواردة أو المنجزة\n- البيانات المنشورة من قبل الهيئات")
        with c2.container(border=True):
            st.markdown("#### المصدر الثاني: ميداني")
            st.markdown("- المقابلة الشخصية\n- الاستمارة (الاستبيان)")

    with t2:
        definition(
            "<b>بيانات السلسلة الزمنية (Time Series)</b>: مشاهدات يأخذها متغير في أوقات مختلفة، "
            "مثل معدل البطالة شهرياً، الناتج المحلي الإجمالي كل ثلاثة أشهر، ربح مؤسسة خلال خمس سنوات. "
            "للبيانات ترتيب طبيعي هو الترتيب الزمني."
        )
        st.markdown("التسلسلات الأكثر شيوعاً: **يومية، أسبوعية، شهرية، فصلية، سنوية**.")
        rng = np.random.default_rng(5)
        T = 60
        t = np.arange(T)
        y = 12 - 0.04 * t + 1.2 * np.sin(2 * np.pi * t / 12) + rng.normal(0, 0.35, T)
        dates = pd.date_range("2020-01-01", periods=T, freq="MS")
        shuffle = st.checkbox("أعِد ترتيب المشاهدات عشوائياً (إفساد الترتيب الزمني)")
        if shuffle:
            y_show = np.random.default_rng(99).permutation(y)
        else:
            y_show = y
        ac = np.corrcoef(y_show[:-1], y_show[1:])[0, 1]
        fig = go.Figure(go.Scatter(x=dates, y=y_show, mode="lines+markers",
                                   line=dict(color=BRICK if shuffle else PETROL, width=2),
                                   marker=dict(size=5)))
        fig.update_xaxes(title="الشهر")
        fig.update_yaxes(title="معدل البطالة % (بيانات توضيحية)")
        show(fig, 320)
        m1, m2 = st.columns(2)
        m1.metric("المتوسط", f"{y_show.mean():.2f}", help="لا يتغير بإعادة الترتيب")
        m2.metric("الارتباط بين مشاهدة وسابقتها", f"{ac:.2f}")
        if shuffle:
            st.warning("المتوسط لم يتغير لكن البنية الزمنية (الاتجاه والموسمية) ضاعت: "
                       "لا يمكن إعادة ترتيب المشاهدات الزمنية دون إفساد المعلومة التي تحملها.")
        else:
            st.caption("الزمن متغير جوهري في هذه البيانات. جرّب خيار إعادة الترتيب.")

    with t3:
        definition(
            "<b>البيانات المقطعية (Cross-Sectional)</b>: عدة متغيرات عند نقطة زمنية واحدة، "
            "تخص وحدات فردية كالشركات والمؤسسات والأشخاص، مثل استقصاء مجموعة من الطلبة."
        )
        c1, c2, c3 = st.columns(3)
        c1.markdown("**وحدات اقتصادية فردية**\n\n- الأفراد\n- الأسر\n- الشركات")
        c2.markdown("**وحدات جغرافية**\n\n- المدن والمناطق الحضرية\n- الولايات والمناطق\n- الدول")
        c3.markdown("**وحدات اقتصادية مجمّعة**\n\n- المهن\n- الصناعات")

        rng = np.random.default_rng(21)
        names = ["مؤسسة " + c for c in "أبجدهوزحطي"]
        cs = pd.DataFrame({
            "المؤسسة": names,
            "عدد العمال": rng.integers(20, 400, 10),
            "رقم الأعمال (مليون دج)": rng.integers(50, 900, 10),
            "القطاع": rng.choice(["صناعة", "خدمات", "تجارة"], 10),
        })
        c1, c2 = st.columns(2)
        col = c1.selectbox("رتّب حسب", cs.columns, index=1)
        asc = c2.radio("الاتجاه", ["تصاعدي", "تنازلي"], horizontal=True) == "تصاعدي"
        st.dataframe(cs.sort_values(col, ascending=asc), hide_index=True, width="stretch")
        st.metric("متوسط رقم الأعمال", f"{cs['رقم الأعمال (مليون دج)'].mean():.1f} مليون دج",
                  help="ثابت مهما كان الترتيب")
        st.success("لا يوجد ترتيب طبيعي للمشاهدات المقطعية: يمكن فرزها بأي طريقة دون تغيير "
                   "المعلومة التي تحملها العيّنة. وغالباً تُبنى على عيّنات عشوائية فتُفترض المشاهدات مستقلة إحصائياً.")

    with t4:
        definition(
            "<b>البيانات المدمجة (Hybrid)</b> تجمع السلسلة الزمنية والمقطعية، وهي نوعان: "
            "<b>المجمّعة المقطعية-الزمنية (Pooled)</b> و<b>بيانات بانل (Panel/Longitudinal)</b>."
        )
        kind = st.radio("اعرض:", ["بيانات مجمّعة (Pooled)", "بيانات بانل (Panel)"], horizontal=True)
        years = [2020, 2021, 2022, 2023, 2024]
        rng = np.random.default_rng(33)
        k = 6
        rows = []
        if kind.startswith("بيانات بانل"):
            base = rng.normal(60000, 12000, k)
            for i in range(k):
                for j, yr in enumerate(years):
                    rows.append((f"أسرة {i + 1}", yr, round(base[i] * 1.04 ** j + rng.normal(0, 2500), -2)))
        else:
            for j, yr in enumerate(years):
                for i in range(k):
                    rows.append((f"أسرة {j * k + i + 1}", yr, round(rng.normal(60000 * 1.04 ** j, 12000), -2)))
        df = pd.DataFrame(rows, columns=["الأسرة", "السنة", "الدخل (دج)"])

        c1, c2 = st.columns([2, 3])
        with c1:
            st.dataframe(df, hide_index=True, height=360, width="stretch")
            st.metric("عدد الأسر المختلفة", df["الأسرة"].nunique())
            st.metric("عدد المشاهدات", len(df))
        with c2:
            fig = go.Figure()
            if kind.startswith("بيانات بانل"):
                for fam, g in df.groupby("الأسرة"):
                    fig.add_trace(go.Scatter(x=g["السنة"], y=g["الدخل (دج)"], mode="lines+markers", name=fam))
                title = "تُتبَّع نفس الأسر عبر الزمن"
            else:
                fig.add_trace(go.Box(x=df["السنة"], y=df["الدخل (دج)"], marker_color=PETROL, name="الدخل"))
                title = "عيّنة مختلفة من الأسر في كل سنة"
            fig.update_xaxes(title="السنة", dtick=1)
            fig.update_yaxes(title="الدخل (دج)")
            show(fig, 400, title)

        if kind.startswith("بيانات بانل"):
            st.info("**بانل:** نفس الوحدات العرضية عبر الزمن، فنستطيع ضبط بعض الخصائص غير المرصودة "
                    "للأفراد أو الشركات أو الولايات وتحليل التأخيرات في سلوك كل وحدة.")
        else:
            st.info("**مجمّعة:** عيّنة مختلفة من الوحدات في كل فترة؛ تتيح حجم عيّنة أكبر وتحليل "
                    "ما إذا كانت العلاقات الاقتصادية قد تغيرت عبر الزمن.")

    with t5:
        mini_quiz(
            "q_vars",
            [
                ("العمر", "كمّي"), ("لون البشرة", "وصفي"), ("الوزن", "كمّي"),
                ("الجنس", "وصفي"), ("الدخل الشهري", "كمّي"),
            ],
            ["كمّي", "وصفي"],
            "صنّف المتغيرات",
        )
        mini_quiz(
            "q_struct",
            [
                ("معدلات البطالة الشهرية في بلد", "سلسلة زمنية"),
                ("استقصاء لـ 200 طالب هذا الأسبوع", "مقطعية"),
                ("دخل نفس الأسر في نفس المدن من 2020 إلى 2024", "بانل"),
                ("دخل أسر مختلفة في 2020 ثم أسر أخرى في 2021", "مجمّعة"),
            ],
            ["سلسلة زمنية", "مقطعية", "مجمّعة", "بانل"],
            "ما هيكل هذه البيانات؟",
        )


# ──────────────────────────────────────────────────────────────
# 6) البرمجيات الإحصائية وتلخيص البيانات
# ──────────────────────────────────────────────────────────────
SOFTWARE = [
    {"name": "R", "open": True, "kind": "لغة برمجة وبيئة إحصائية",
     "note": "مجانية ومفتوحة المصدر، آلاف الحزم الإحصائية، رسوم بيانية قوية."},
    {"name": "Python", "open": True, "kind": "لغة برمجة عامة",
     "note": "مجانية ومفتوحة المصدر، مكتبات مثل pandas وstatsmodels وscikit-learn."},
    {"name": "EViews", "open": False, "kind": "برنامج تجاري بواجهة رسومية",
     "note": "معروف في الاقتصاد القياسي والسلاسل الزمنية والتنبؤ."},
    {"name": "SPSS", "open": False, "kind": "برنامج تجاري بواجهة رسومية",
     "note": "منتشر في العلوم الاجتماعية، سهل الاستعمال بالنقر."},
    {"name": "Stata", "open": False, "kind": "برنامج تجاري",
     "note": "شائع في الاقتصاد القياسي وبيانات بانل."},
    {"name": "GAUSS", "open": False, "kind": "لغة مصفوفات تجارية",
     "note": "موجهة للحساب العددي والاقتصاد القياسي."},
]

CODE = {
    "R": ('r', "mean(df$x)\nsummary(lm(y ~ x, data = df))"),
    "Python": ('python',
               "import pandas as pd\nimport statsmodels.formula.api as smf\n\n"
               "df['x'].mean()\nsmf.ols('y ~ x', data=df).fit().summary()"),
    "Stata": ('stata', "summarize x\nregress y x"),
    "SPSS": ('text', "DESCRIPTIVES VARIABLES=x.\nREGRESSION /DEPENDENT y /METHOD=ENTER x."),
    "EViews": ('text', "x.stats\nls y c x"),
    "GAUSS": ('text', "mean(x);\ncall ols(\"\", y, x);"),
}


@st.cache_data
def make_students():
    rng = np.random.default_rng(2026)
    n = 150
    major = rng.choice(["اقتصاد", "تسيير", "تجارة"], n)
    shift = pd.Series(major).map({"اقتصاد": 0.8, "تسيير": 0.0, "تجارة": -0.6}).to_numpy()
    study = np.clip(rng.normal(8, 3, n), 0, 20).round(1)
    grade = np.clip(9.5 + shift + 0.25 * study + rng.normal(0, 2, n), 0, 20).round(2)
    return pd.DataFrame({
        "التخصص": major,
        "الجنس": rng.choice(["ذكر", "أنثى"], n),
        "العمر": rng.integers(19, 26, n),
        "ساعات المراجعة أسبوعياً": study,
        "المعدل": grade,
    })


def page_software():
    header("6) تلخيص البيانات والتعرف على البرمجيات الإحصائية",
           "تبويب البيانات، تمثيلها بيانياً، قياس العلاقة بين المتغيرات، واختبار دلالة الفروق")
    t1, t2, t3 = st.tabs(["البرمجيات", "نفس المهمة بلغات مختلفة", "جرّب تلخيص بيانات"])

    with t1:
        st.markdown(
            "**تلخيص البيانات** هو تبويبها وتمثيلها بيانياً وقياس العلاقة بين المتغيرات والكشف عن دلالة "
            "الفروق بين العيّنات. وأكثر الحزم الإحصائية شيوعاً:"
        )
        only_open = st.toggle("إظهار البرمجيات المفتوحة المصدر فقط (محور هذا المقياس)")
        items = [s for s in SOFTWARE if s["open"] or not only_open]
        cols = st.columns(3)
        for i, s in enumerate(items):
            with cols[i % 3].container(border=True):
                st.markdown(f"### {s['name']}")
                st.markdown(("🟢 **مفتوح المصدر ومجاني**" if s["open"] else "🟠 **تجاري (برخصة مدفوعة)**"))
                st.write(s["kind"])
                st.caption(s["note"])

    with t2:
        st.markdown("المهمة: **حساب متوسط متغير x ثم تقدير انحدار y على x**.")
        tabs = st.tabs(list(CODE))
        for tab, (name, (lang, code)) in zip(tabs, CODE.items()):
            with tab:
                st.code(code, language=lang)
        st.caption("الفكرة واحدة والصياغة تختلف: بعضها بالنقر وبعضها بالأوامر البرمجية. "
                   "تحقق من صياغة الأوامر في إصدار البرنامج الذي تستعمله.")

    with t3:
        src = st.radio("مصدر البيانات", ["بيانات تجريبية (طلبة)", "رفع ملف CSV"], horizontal=True)
        df = None
        if src.startswith("بيانات"):
            df = make_students()
            buf = io.StringIO()
            df.to_csv(buf, index=False)
            st.download_button("تنزيل البيانات التجريبية (CSV)", buf.getvalue().encode("utf-8-sig"),
                               "students_demo.csv", "text/csv")
        else:
            up = st.file_uploader("ارفع ملف CSV", type=["csv"])
            if up is not None:
                try:
                    df = pd.read_csv(up)
                except Exception as e:  # noqa: BLE001
                    st.error(f"تعذّرت قراءة الملف: {e}")
        if df is None or df.empty:
            st.info("ارفع ملفاً لبدء التلخيص.")
            return

        st.dataframe(df.head(20), hide_index=True, width="stretch")
        st.caption(f"{len(df)} صفاً × {df.shape[1]} أعمدة")
        var = st.selectbox("اختر متغيراً لتلخيصه", df.columns)
        s = df[var]
        if pd.api.types.is_numeric_dtype(s):
            d = s.describe()
            m = st.columns(5)
            m[0].metric("العدد", f"{int(d['count'])}")
            m[1].metric("الوسط", f"{d['mean']:.2f}")
            m[2].metric("الوسيط", f"{d['50%']:.2f}")
            m[3].metric("الانحراف المعياري", f"{d['std']:.2f}")
            m[4].metric("المدى", f"{d['max'] - d['min']:.2f}")
            c1, c2 = st.columns(2)
            with c1:
                fig = go.Figure(go.Histogram(x=s, marker_color=PETROL))
                show(fig, 300, "التوزيع")
            with c2:
                fig = go.Figure(go.Box(y=s, marker_color=PETROL, name=""))
                show(fig, 300, "الصندوق ذو الشاربين")
        else:
            freq = s.value_counts().rename_axis(var).reset_index(name="التكرار")
            freq["النسبة %"] = (freq["التكرار"] / freq["التكرار"].sum() * 100).round(1)
            c1, c2 = st.columns(2)
            c1.dataframe(freq, hide_index=True, width="stretch")
            with c2:
                fig = go.Figure(go.Bar(x=freq[var].astype(str), y=freq["التكرار"], marker_color=PETROL))
                show(fig, 300, "التكرارات")

        if src.startswith("بيانات"):
            st.markdown("##### هل يوجد فرق بين متوسط معدلات التخصصات الثلاثة؟")
            groups = {g: v["المعدل"].to_numpy() for g, v in df.groupby("التخصص")}
            fig = go.Figure()
            for g, v in groups.items():
                fig.add_trace(go.Box(y=v, name=g, boxmean=True))
            fig.update_yaxes(title="المعدل")
            show(fig, 320)
            f, p = stats.f_oneway(*groups.values())
            c1, c2 = st.columns(2)
            c1.metric("إحصائية F (تحليل التباين)", f"{f:.2f}")
            c2.metric("p-value", f"{p:.4f}")
            st.caption("هذا مثال على الإحصاء الاستدلالي: الاختبار يجيب هل الفروق الملاحظة بين المتوسطات "
                       "كبيرة بما يكفي لتعميمها على المجتمع، أم يمكن أن تكون مجرد صدفة معاينة.")


# ──────────────────────────────────────────────────────────────
# 7) اختبار ختامي
# ──────────────────────────────────────────────────────────────
QUIZ = [
    ("المجتمع الإحصائي هو:",
     ["مجموعة الأفراد محل الدراسة التي تشترك في خصائص معينة", "جزء صغير يُختار للدراسة", "جدول للبيانات", "برنامج إحصائي"],
     0, "العيّنة جزء من المجتمع، أما المجتمع فهو الكل محل الدراسة."),
    ("عدد الطلبة المسجلين في جامعة معينة مثال على:",
     ["مجتمع غير محدود", "مجتمع محدود", "سلسلة زمنية", "حد عشوائي"],
     1, "يمكن حصر العدد، فالمجتمع محدود."),
    ("الوسط والوسيط والانحراف المعياري تنتمي إلى:",
     ["الإحصاء الاستدلالي", "الإحصاء الوصفي", "الاقتصاد القياسي فقط", "اختبار الفرضيات"],
     1, "هي مقاييس لوصف البيانات وتلخيصها."),
    ("التعميم من عيّنة إلى مجتمع أكبر باختبارات الفرضيات هو دور:",
     ["الإحصاء الوصفي", "الإحصاء الاستدلالي", "الجداول التكرارية", "الرسوم البيانية"],
     1, "هذا هو جوهر الإحصاء الاستدلالي."),
    ("أي مما يلي ليس من أهداف الاقتصاد القياسي؟",
     ["اختبار النظريات الاقتصادية", "رسم السياسات واتخاذ القرار", "التنبؤ بالقيم الاقتصادية", "حصر عدد أفراد المجتمع"],
     3, "الأهداف الثلاثة: اختبار النظريات، رسم السياسات، التنبؤ."),
    ("في النموذج yᵢ = αXᵢ + b + Uᵢ، الحد Uᵢ يمثل:",
     ["الميل", "الثابت", "أثر العوامل غير المدرجة أو غير المعروفة", "المتغير المستقل"],
     2, "هو الحد العشوائي الذي يجعل العلاقة احتمالية."),
    ("النموذج الذي فيه المتغير المستقل مرفوع للقوة 2 هو:",
     ["خطي", "غير خطي", "ساكن", "مقطعي"],
     1, "الخطي تكون قوة متغيراته المستقلة مساوية للواحد."),
    ("معدلات البطالة الشهرية تشكّل:",
     ["بيانات مقطعية", "سلسلة زمنية", "بيانات بانل", "بيانات وصفية فقط"],
     1, "مشاهدات لنفس المتغير في أوقات مختلفة."),
    ("تتبّع نفس الأسر في نفس المدن من 2020 إلى 2024 يعطي:",
     ["بيانات مجمّعة", "بيانات مقطعية", "بيانات بانل", "سلسلة زمنية لمتغير واحد"],
     2, "في بانل تُتبَّع نفس الوحدات عبر الزمن، بخلاف المجمّعة."),
    ("أي البرمجيات التالية مفتوحة المصدر ومجانية؟",
     ["SPSS", "Stata", "EViews", "R"],
     3, "R (وكذلك Python) مفتوحة المصدر."),
]


def page_quiz():
    header("7) اختبار ختامي", f"{len(QUIZ)} أسئلة لقياس فهمك للدرس")
    with st.form("final_quiz"):
        answers = []
        for i, (q, opts, _, _) in enumerate(QUIZ):
            answers.append(st.radio(f"{i + 1}. {q}", opts, index=None, key=f"fq_{i}"))
            st.write("")
        done = st.form_submit_button("تصحيح الاختبار")
    if done:
        score = sum(1 for a, (_, o, c, _) in zip(answers, QUIZ) if a == o[c])
        st.markdown(f"## نتيجتك: {score} / {len(QUIZ)}")
        st.progress(score / len(QUIZ))
        for i, (a, (q, opts, c, why)) in enumerate(zip(answers, QUIZ)):
            if a is None:
                st.warning(f"{i + 1}. لم تجب. الجواب: **{opts[c]}** — {why}")
            elif a == opts[c]:
                st.success(f"{i + 1}. صحيح: **{opts[c]}** — {why}")
            else:
                st.error(f"{i + 1}. إجابتك: {a}. الصحيح: **{opts[c]}** — {why}")


# ──────────────────────────────────────────────────────────────
# التنقل
# ──────────────────────────────────────────────────────────────
PAGES = {
    "الرئيسية": page_home,
    "1) المجتمع الإحصائي": page_population,
    "2) الإحصاء الوصفي والاستدلالي": page_desc_inf,
    "3) مدخل للاقتصاد القياسي": page_intro_econometrics,
    "4) النموذج القياسي": page_model,
    "5) البيانات": page_data,
    "6) البرمجيات وتلخيص البيانات": page_software,
    "7) اختبار ختامي": page_quiz,
}
LABELS = list(PAGES)
st.session_state.setdefault("nav", LABELS[0])


def step_page(delta: int):
    i = LABELS.index(st.session_state.nav) + delta
    st.session_state.nav = LABELS[max(0, min(len(LABELS) - 1, i))]


with st.sidebar:
    st.markdown("### 📊 البرمجيات الإحصائية المفتوحة")
    st.markdown(f"<div class='meta-line'>{COURSE['prof']}<br>{COURSE['univ']} — {COURSE['dept']}<br>"
                f"{COURSE['year']}</div>", unsafe_allow_html=True)
    st.divider()
    st.radio("محاور الدرس الأول", LABELS, key="nav")

PAGES[st.session_state.nav]()

st.divider()
cur = LABELS.index(st.session_state.nav)
c_prev, _, c_next = st.columns([1, 3, 1])
if cur > 0:
    c_prev.button("→ السابق", on_click=step_page, args=(-1,), width="stretch")
if cur < len(LABELS) - 1:
    c_next.button("التالي ←", on_click=step_page, args=(1,), width="stretch")
