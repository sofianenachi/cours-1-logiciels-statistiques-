# -*- coding: utf-8 -*-
"""
تطبيق Streamlit: شرح نموذج VAR خطوة بخطوة من خلال مثال تطبيقي
(بيانات فصلية 2000Q1 – 2024Q4 : IPI, CPI, UNEMP, INT_RATE)

التشغيل:
    pip install -r requirements.txt
    streamlit run app.py
"""
import io
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.stats.diagnostic import het_arch
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.vector_ar.vecm import coint_johansen

warnings.filterwarnings("ignore")

st.set_page_config(page_title="شرح نموذج VAR", page_icon="📈", layout="wide")

# ----------------------------------------------------------------------
# تنسيق عام: اتجاه من اليمين لليسار للنص العربي، والكود والجداول من اليسار
# ----------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
    direction: rtl; font-family: 'Cairo', sans-serif;
}
[data-testid="stMarkdownContainer"], [data-testid="stAlert"], [data-testid="stRadio"] label,
[data-testid="stExpander"] summary, .stSelectbox label, .stSlider label, .stCheckbox label {
    text-align: right;
}
pre, code, [data-testid="stCode"], [data-testid="stDataFrame"], [data-testid="stLatex"],
.katex-display { direction: ltr; text-align: left; }
h1, h2, h3 { font-weight: 700; }
</style>
""",
    unsafe_allow_html=True,
)

HERE = Path(__file__).parent
DEFAULT_CSV = HERE / "data_model_var.csv"

STEPS = [
    "0) مقدمة عن نموذج VAR",
    "1) استيراد البيانات",
    "2) التحليل الوصفي",
    "3) التحويلات (اللوغاريتم)",
    "4) اختبارات جذر الوحدة",
    "5) رتبة التكامل والسلاسل المستقرة",
    "6) التكامل المشترك (جوهانسن)",
    "7) اختيار عدد التأخيرات",
    "8) تقدير نموذج VAR",
    "9) استقرار النموذج و CUSUM",
    "10) اختبارات البواقي",
    "11) سببية جرانجر",
    "12) دوال الاستجابة النبضية (IRF)",
    "13) تفكيك التباين (FEVD)",
    "14) التنبؤ",
    "15) الخلاصة",
]

CRIT_LABELS = {"AIC": "aic", "SC / BIC": "bic", "HQ": "hqic", "FPE": "fpe"}


# ----------------------------------------------------------------------
# أدوات مساعدة
# ----------------------------------------------------------------------
def r_code(code: str):
    with st.expander("💻 الكود المقابل في R"):
        st.code(code.strip("\n"), language="r")


def verdict(ok: bool, good: str, bad: str):
    (st.success if ok else st.warning)(("✅ " + good) if ok else ("⚠️ " + bad))


def show_fig(fig):
    st.pyplot(fig)
    plt.close(fig)


def unit_root_tests(x) -> dict:
    x = pd.Series(x).dropna().values
    a = adfuller(x, regression="c", autolag="AIC", maxlag=8)
    k = kpss(x, regression="c", nlags="auto")
    return {
        "ADF (إحصاءة)": a[0],
        "ADF (p)": a[1],
        "ADF 5%": a[4]["5%"],
        "KPSS (إحصاءة)": k[0],
        "KPSS (p)": k[1],
    }


def diff_n(x: pd.Series, d: int) -> pd.Series:
    for _ in range(d):
        x = x.diff()
    return x


def auto_diff_order(x: pd.Series) -> int:
    for d in range(3):
        xd = diff_n(x, d).dropna()
        if adfuller(xd.values, regression="c", autolag="AIC", maxlag=8)[1] < 0.05:
            return d
    return 2


@st.cache_data
def read_csv_bytes(raw: bytes) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(raw), index_col=0)


def to_period_index(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    try:
        df.index = pd.PeriodIndex(df.index.astype(str), freq="Q")
    except Exception:
        df.index = pd.period_range("2000Q1", periods=len(df), freq="Q")
        st.sidebar.warning("تعذّر قراءة التواريخ؛ تم افتراض بداية 2000Q1.")
    return df


# ----------------------------------------------------------------------
# الشريط الجانبي: التنقل + الإعدادات
# ----------------------------------------------------------------------
st.sidebar.title("📈 نموذج VAR")
step = st.sidebar.radio("الخطوات", STEPS, label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.subheader("⚙️ الإعدادات")

uploaded = st.sidebar.file_uploader("ملف بياناتك (CSV) — اختياري", type="csv")
if uploaded is not None:
    raw_df = read_csv_bytes(uploaded.getvalue())
elif DEFAULT_CSV.exists():
    raw_df = read_csv_bytes(DEFAULT_CSV.read_bytes())
else:
    st.error("ضع الملف data_model_var.csv بجانب app.py أو ارفع ملفك من الشريط الجانبي.")
    st.stop()

raw_df = to_period_index(raw_df.select_dtypes("number"))
all_cols = list(raw_df.columns)
default_order = [c for c in ["IPI", "CPI", "UNEMP", "INT_RATE"] if c in all_cols] or all_cols

order = st.sidebar.multiselect(
    "ترتيب المتغيرات (مهم لـ IRF/Cholesky)", all_cols, default=default_order
)
if len(order) < 2:
    st.error("اختر متغيرين على الأقل.")
    st.stop()
log_default = [c for c in ["IPI", "CPI"] if c in order]
log_vars = st.sidebar.multiselect("متغيرات تُحوَّل إلى 100×log", order, default=log_default)

max_lags = st.sidebar.slider("أقصى عدد تأخيرات للاختيار", 2, 12, 8)
crit_label = st.sidebar.selectbox("معيار اختيار التأخيرات", list(CRIT_LABELS), index=0)
p_manual = st.sidebar.slider("عدد التأخيرات (0 = حسب المعيار)", 0, 8, 0)
irf_h = st.sidebar.slider("أفق IRF و FEVD (فصول)", 4, 24, 12)
fc_h = st.sidebar.slider("أفق التنبؤ (فصول)", 4, 16, 8)
mc_reps = st.sidebar.slider("عدد محاكاة حدود الثقة (IRF)", 100, 1000, 300, step=100)

# ----------------------------------------------------------------------
# خط المعالجة (Pipeline)
# ----------------------------------------------------------------------
try:
    lev = pd.DataFrame(index=raw_df.index)
    for v in order:
        if v in log_vars:
            lev["L" + v] = 100 * np.log(raw_df[v])
        else:
            lev[v] = raw_df[v]

    auto_d = {c: auto_diff_order(lev[c]) for c in lev.columns}
    with st.sidebar.expander("رتبة التفاضل لكل متغير (تعديل يدوي)"):
        d_vec = {}
        for c in lev.columns:
            choice = st.selectbox(
                f"{c} (تلقائي = {auto_d[c]})", ["تلقائي", 0, 1, 2], key=f"d_{c}"
            )
            d_vec[c] = auto_d[c] if choice == "تلقائي" else int(choice)

    stat_cols = {}
    for c in lev.columns:
        name = c if d_vec[c] == 0 else f"D{d_vec[c]}_{c}"
        stat_cols[name] = diff_n(lev[c], d_vec[c])
    Ystat = pd.DataFrame(stat_cols).dropna()
    names = list(Ystat.columns)
    k = len(names)

    sel = VAR(Ystat).select_order(maxlags=max_lags)
    ic_table = pd.DataFrame(sel.ics, index=range(0, max_lags + 1)).drop(index=0)
    ic_table.columns = [c.upper() for c in ic_table.columns]
    ic_pick = {kk: max(int(vv), 1) for kk, vv in sel.selected_orders.items()}
    p = p_manual if p_manual > 0 else ic_pick[CRIT_LABELS[crit_label]]

    model = VAR(Ystat)
    m = model.fit(p, trend="c")
    n_obs = m.nobs
    res = m.resid
except Exception as e:  # noqa
    st.error(f"تعذّر بناء النموذج بالإعدادات الحالية: {e}")
    st.stop()


# ======================================================================
# الصفحات
# ======================================================================
def page_intro():
    st.title("نموذج VAR خطوة بخطوة")
    st.markdown(
        """
**نموذج الانحدار الذاتي الشعاعي (Vector AutoRegression)** يعامل كل المتغيرات كمتغيرات *داخلية*،
بحيث تُفسَّر قيمة كل متغير بقيمه السابقة وبقيم المتغيرات الأخرى السابقة. صيغته العامة:
"""
    )
    st.latex(r"Y_t = c + A_1 Y_{t-1} + A_2 Y_{t-2} + \dots + A_p Y_{t-p} + \varepsilon_t")
    st.markdown(
        """
حيث \\(Y_t\\) شعاع المتغيرات (هنا 4 متغيرات)، و\\(p\\) عدد التأخيرات، و\\(\\varepsilon_t\\) شعاع الأخطاء.

**لماذا VAR؟**
- لا يحتاج لتحديد مسبق للمتغيرات الداخلية والخارجية.
- مناسب للتنبؤ ولدراسة الديناميكية بين المتغيرات (IRF و FEVD).
- يسمح باختبار السببية بمفهوم جرانجر.

**المثال المستعمل:** بيانات فصلية افتراضية لأربعة متغيرات اقتصادية:
"""
    )
    st.table(
        pd.DataFrame(
            {
                "المتغير": ["IPI", "CPI", "UNEMP", "INT_RATE"],
                "المعنى": [
                    "مؤشر الإنتاج الصناعي",
                    "مؤشر الأسعار عند الاستهلاك",
                    "معدل البطالة",
                    "سعر الفائدة",
                ],
            }
        )
    )
    st.markdown("**مخطط العمل (استعمل الشريط الجانبي للتنقل):**")
    st.markdown(
        """
1. فحص البيانات وتحويلها → 2. اختبار الاستقرارية (جذر الوحدة) → 3. تحديد رتبة التكامل
→ 4. التكامل المشترك (إن لزم، وإلا VECM) → 5. اختيار عدد التأخيرات → 6. التقدير
→ 7. اختبار الاستقرار وثبات المعاملات → 8. اختبارات البواقي → 9. السببية
→ 10. IRF و FEVD → 11. التنبؤ.
"""
    )
    st.info("جرّب تغيير الإعدادات من الشريط الجانبي (التحويلات، المعيار، الأفق...) وستتحدّث كل الصفحات.")


def page_data():
    st.header("1) استيراد البيانات")
    st.markdown(
        """
نقرأ الملف، ونتأكد من **عدد المشاهدات** و**غياب القيم المفقودة** و**التواتر الزمني** (فصلي = 4).
العمود الأول يحمل التواريخ مثل `2000Q1`.
"""
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("عدد المشاهدات", len(raw_df))
    c2.metric("البداية", str(raw_df.index[0]))
    c3.metric("النهاية", str(raw_df.index[-1]))
    st.dataframe(raw_df.round(4))
    na = int(raw_df.isna().sum().sum())
    verdict(na == 0, "لا توجد قيم مفقودة.", f"يوجد {na} قيمة مفقودة تحتاج معالجة.")
    r_code(
        """
df <- read.csv("data_model_var.csv", stringsAsFactors = FALSE)
names(df)[1] <- "date"
Y <- ts(df[, c("IPI","CPI","UNEMP","INT_RATE")], start = c(2000,1), frequency = 4)
colSums(is.na(df))
"""
    )


def page_desc():
    st.header("2) التحليل الوصفي")
    st.markdown("نبدأ بالرسوم والإحصاءات الوصفية: هل تتذبذب السلاسل حول متوسط ثابت؟ هل يوجد اتجاه عام أو قفزات؟")
    st.dataframe(raw_df.describe().T.round(3))
    fig, ax = plt.subplots(len(raw_df.columns), 1, figsize=(10, 2 * len(raw_df.columns)), sharex=True)
    for a, c in zip(np.atleast_1d(ax), raw_df.columns):
        a.plot(raw_df.index.to_timestamp(), raw_df[c], color="k", lw=1)
        a.axhline(raw_df[c].mean(), color="r", ls="--", lw=0.8)
        a.set_ylabel(c)
    fig.tight_layout()
    show_fig(fig)
    st.info(
        "الخط الأحمر المتقطع هو المتوسط. إذا كانت السلسلة تعود باستمرار إلى متوسطها دون اتجاه واضح "
        "فهذا مؤشر أولي على الاستقرارية، لكن لا يُغني عن الاختبارات الرسمية في الخطوة 4."
    )
    r_code("summary(Y)\nplot(Y, main = 'المتغيرات الأصلية')")


def page_transform():
    st.header("3) التحويلات")
    st.markdown(
        """
نأخذ **اللوغاريتم** للمؤشرات (IPI و CPI) لأن تغيراتها تصبح تقريباً نسباً مئوية وتستقر تباينها.
نضرب في 100 ليُقرأ الفرق بين قيمتين كنقاط مئوية تقريباً. أما **معدل البطالة** و**سعر الفائدة** فهما نسب أصلاً،
فنبقيهما كما هما.
"""
    )
    st.latex(r"LIPI_t = 100 \times \ln(IPI_t)")
    st.dataframe(lev.head(8).round(3))
    fig, ax = plt.subplots(len(lev.columns), 1, figsize=(10, 2 * len(lev.columns)), sharex=True)
    for a, c in zip(np.atleast_1d(ax), lev.columns):
        a.plot(lev.index.to_timestamp(), lev[c], color="navy", lw=1)
        a.set_ylabel(c)
    fig.tight_layout()
    show_fig(fig)
    st.caption(f"المتغيرات الموجودة الآن: {', '.join(lev.columns)}")
    r_code(
        """
Ylev <- ts.union(
  LIPI = 100*log(Y[,"IPI"]), LCPI = 100*log(Y[,"CPI"]),
  UNEMP = Y[,"UNEMP"], INT_RATE = Y[,"INT_RATE"])
"""
    )


def page_unit_root():
    st.header("4) اختبارات جذر الوحدة (الاستقرارية)")
    st.markdown(
        """
يشترط VAR (في صيغته القياسية) أن تكون السلاسل **مستقرة**. نستعمل اختبارين متكاملين:

| الاختبار | الفرضية الصفرية H0 | القرار "مستقرة" إذا |
|---|---|---|
| **ADF** | وجود جذر وحدة | p < 0.05 (أو الإحصاءة < القيمة الحرجة) |
| **KPSS** | السلسلة مستقرة | p > 0.05 |

التوافق بين الاختبارين يعزّز النتيجة. (قيم p لـ KPSS محصورة بين 0.01 و 0.10 في الجداول.)
"""
    )
    rows_l, rows_d = [], []
    for c in lev.columns:
        r = unit_root_tests(lev[c])
        r["القرار"] = "مستقرة" if (r["ADF (p)"] < 0.05 and r["KPSS (p)"] > 0.05) else (
            "مستقرة (ADF فقط)" if r["ADF (p)"] < 0.05 else "جذر وحدة")
        rows_l.append(pd.Series(r, name=c))
        rd = unit_root_tests(lev[c].diff())
        rd["القرار"] = "مستقرة" if rd["ADF (p)"] < 0.05 else "جذر وحدة"
        rows_d.append(pd.Series(rd, name=c))

    st.subheader("عند المستوى")
    t1 = pd.DataFrame(rows_l)
    st.dataframe(t1.round(3))
    st.subheader("عند الفروق الأولى")
    t2 = pd.DataFrame(rows_d)
    st.dataframe(t2.round(3))

    all_stat = all(t1["ADF (p)"] < 0.05)
    verdict(
        all_stat,
        "كل المتغيرات مستقرة عند المستوى (I(0)). نقدّر VAR على المستويات دون تفاضل.",
        "بعض المتغيرات ليست مستقرة عند المستوى؛ سيتم تفاضلها في الخطوة التالية.",
    )
    st.warning(
        "انتبه: نتائج الفروق الأولى تخرج دائماً 'مستقرة' تقريباً، وليست هي المرجع. "
        "المرجع هو نتيجة المستوى، وتفاضل سلسلة مستقرة أصلاً (over-differencing) يُدخل ارتباطاً ذاتياً سالباً مصطنعاً."
    )
    r_code(
        """
adf <- ur.df(x, type = "drift", selectlags = "AIC", lags = 8)
summary(adf)          # قارن tau2 بالقيمة الحرجة 5%
tseries::kpss.test(x, null = "Level")
tseries::pp.test(x)
"""
    )


def page_integration():
    st.header("5) رتبة التكامل والسلاسل المستقرة")
    st.markdown(
        "رتبة التكامل \\(d\\) هي عدد مرات التفاضل اللازمة للحصول على سلسلة مستقرة. "
        "نحدّدها تلقائياً (أول \\(d\\) تعطي ADF معنوياً)، ويمكنك فرضها يدوياً من الشريط الجانبي."
    )
    tbl = pd.DataFrame({"d (تلقائي)": auto_d, "d (المستعمل)": d_vec})
    st.dataframe(tbl)
    if all(v == 0 for v in d_vec.values()):
        st.success("كل المتغيرات I(0): السلاسل المستعملة في VAR هي نفسها السلاسل بالمستوى.")
    else:
        st.info("بعض المتغيرات تم تفاضلها؛ أسماؤها تبدأ بـ D1_ أو D2_.")
    st.markdown("**السلاسل النهائية المستعملة في النموذج:**")
    st.dataframe(Ystat.head(8).round(3))
    fig, ax = plt.subplots(k, 1, figsize=(10, 2 * k), sharex=True)
    for a, c in zip(np.atleast_1d(ax), names):
        a.plot(Ystat.index.to_timestamp(), Ystat[c], color="darkgreen", lw=1)
        a.axhline(Ystat[c].mean(), color="r", ls="--", lw=0.8)
        a.set_ylabel(c)
    fig.tight_layout()
    show_fig(fig)
    r_code(
        """
d_order <- sapply(colnames(Ylev), function(v) forecast::ndiffs(Ylev[,v], test="adf", alpha=0.05))
Ystat <- do.call(ts.intersect, lapply(colnames(Ylev), function(v)
          if (d_order[[v]]==0) Ylev[,v] else diff(Ylev[,v], differences=d_order[[v]])))
"""
    )


def page_johansen():
    st.header("6) التكامل المشترك (Johansen)")
    st.markdown(
        """
**متى نحتاجه؟** فقط إذا كان لدينا متغيران أو أكثر من الرتبة **I(1)**.
إذا وُجد تكامل مشترك (علاقة توازن طويلة الأجل) فالأفضل تقدير **VECM** لأن VAR في الفروق يضيّع معلومة المستوى.
"""
    )
    n_i1 = sum(1 for v in d_vec.values() if v == 1)
    if n_i1 < 2:
        st.success(
            f"عدد المتغيرات I(1) هو {n_i1} (< 2): **لا حاجة لاختبار التكامل المشترك** هنا، ونواصل بـ VAR."
        )
        show = st.checkbox("أريد رؤية الاختبار لأغراض تعليمية فقط (على كل المتغيرات)")
        if not show:
            r_code(
                """
Yi1 <- Ylev[, which(d_order == 1)]
jo <- ca.jo(Yi1, type = "trace", ecdet = "const", K = 2, spec = "transitory")
summary(jo)   # إذا r > 0 → VECM: vec2var(jo, r = 1)
"""
            )
            return
        cols = list(lev.columns)
    else:
        cols = [c for c in lev.columns if d_vec[c] == 1]
    jo = coint_johansen(lev[cols], det_order=0, k_ar_diff=max(p - 1, 1))
    tab = pd.DataFrame(
        {
            "H0": [f"r ≤ {i}" for i in range(len(cols))],
            "Trace": jo.lr1,
            "القيمة الحرجة 5%": jo.cvt[:, 1],
        }
    )
    tab["القرار"] = np.where(tab["Trace"] > tab["القيمة الحرجة 5%"], "رفض H0", "قبول H0")
    st.dataframe(tab.round(3))
    rank = 0
    for i in range(len(cols)):
        if jo.lr1[i] > jo.cvt[i, 1]:
            rank += 1
        else:
            break
    st.write(f"**رتبة التكامل المشترك المقدّرة r = {rank}**")
    st.caption(
        "تُقرأ الجداول بالتتابع: نرفض H0: r ≤ 0 ثم r ≤ 1... حتى نقبل لأول مرة. "
        "في بيانات مستقرة عند المستوى يكون الرفض (r = عدد المتغيرات) متوقعاً ولا يعني تكاملاً مشتركاً حقيقياً."
    )
    r_code(
        """
jo <- ca.jo(Yi1, type = "trace", ecdet = "const", K = K, spec = "transitory")
summary(jo)
# إذا r > 0:  vecm <- cajorls(jo, r = 1);  var_from_vecm <- vec2var(jo, r = 1)
"""
    )


def page_lags():
    st.header("7) اختيار عدد التأخيرات")
    st.markdown(
        """
نقدّر النموذج لعدة قيم من \\(p\\) ونختار القيمة التي **تُصغّر** معيار المعلومات:
**AIC** (يميل لتأخيرات أكثر)، **SC/BIC** و**HQ** (أكثر اقتصاداً)، **FPE**.
"""
    )
    st.dataframe(ic_table.round(4))
    c = st.columns(4)
    for col, (lab, key) in zip(c, CRIT_LABELS.items()):
        col.metric(lab, f"p = {ic_pick[key]}")
    fig, ax = plt.subplots(1, 3, figsize=(12, 3))
    for a, key in zip(ax, ["AIC", "BIC", "HQIC"]):
        a.plot(ic_table.index, ic_table[key], marker="o")
        a.set_title(key)
        a.set_xlabel("p")
    fig.tight_layout()
    show_fig(fig)
    st.info(f"عدد التأخيرات المستعمل في النموذج: **p = {p}**")
    if len(set(ic_pick.values())) == 1:
        st.success("المعايير الأربعة متفقة: اختيار واضح.")
    else:
        st.warning("المعايير مختلفة؛ مع عيّنة صغيرة يُفضَّل الأكثر اقتصاداً (SC/HQ) لتجنب كثرة المعاملات.")
    r_code(
        """
sel <- VARselect(Ystat, lag.max = 8, type = "const")
sel$selection
p_opt <- sel$selection[["AIC(n)"]]
"""
    )


def page_estimate():
    st.header("8) تقدير نموذج VAR")
    st.markdown(
        f"""
نقدّر النموذج **VAR({p})** مع حد ثابت بطريقة المربعات الصغرى لكل معادلة (OLS)، وهي طريقة فعّالة هنا
لأن كل المعادلات تحوي نفس المتغيرات التفسيرية. عدد المشاهدات المستعملة: **{n_obs}**.
"""
    )
    eq = st.selectbox("اختر المعادلة", names)
    coef = pd.DataFrame(
        {
            "المعامل": m.params[eq],
            "الخطأ المعياري": m.stderr[eq],
            "t": m.tvalues[eq],
            "p-value": m.pvalues[eq],
        }
    )
    coef["الدلالة"] = np.where(coef["p-value"] < 0.01, "***", np.where(coef["p-value"] < 0.05, "**",
                         np.where(coef["p-value"] < 0.1, "*", "")))
    st.dataframe(coef.round(4))

    y = m.endog[m.k_ar:, names.index(eq)]
    r2 = 1 - (res[eq].values ** 2).sum() / ((y - y.mean()) ** 2).sum()
    df_res = len(y) - m.params.shape[0]
    c1, c2 = st.columns(2)
    c1.metric("R²", f"{r2:.3f}")
    c2.metric("الانحراف المعياري للبواقي", f"{np.sqrt((res[eq] ** 2).sum() / df_res):.4f}")

    sig_self = [i for i in coef.index if i.startswith(f"L1.{eq}") and coef.loc[i, "p-value"] < 0.05]
    cross = [i for i in coef.index if i.startswith("L") and eq not in i and coef.loc[i, "p-value"] < 0.05]
    st.markdown("**قراءة النتيجة:**")
    st.markdown(
        f"- {'الاستمرارية الذاتية (التأخير الأول للمتغير نفسه) معنوية.' if sig_self else 'التأخير الذاتي الأول غير معنوي.'}\n"
        f"- عدد التأثيرات المتقاطعة المعنوية عند 5%: **{len(cross)}**."
    )
    st.markdown("**ارتباط البواقي بين المعادلات** (إذا كان ضعيفاً فترتيب Cholesky يؤثر قليلاً):")
    st.dataframe(pd.DataFrame(m.resid_corr, index=names, columns=names).round(3))
    st.caption("R² المنخفض شائع في سلاسل تتذبذب عشوائياً حول متوسطها؛ لا يعني بالضرورة أن النموذج سيّئ.")
    r_code(
        """
var_model <- VAR(Ystat, p = p_opt, type = "const")
summary(var_model)
"""
    )


def page_stability():
    st.header("9) استقرار النموذج وثبات المعاملات")
    st.markdown(
        """
**الاستقرار:** يكون VAR مستقراً إذا كانت **كل جذور المصفوفة المرافقة (modulus) أصغر من 1**
(أي داخل دائرة الوحدة). عندها تتلاشى الصدمات مع الزمن، وتكون IRF و FEVD ذات معنى.
"""
    )
    eig = 1 / m.roots
    mod = np.abs(eig)
    st.dataframe(pd.DataFrame({"الجذر": [f"{z.real:.4f} {z.imag:+.4f}i" for z in eig], "modulus": np.round(mod, 4)}))
    verdict(bool(mod.max() < 1), f"النموذج مستقر (أكبر modulus = {mod.max():.3f}).",
            f"النموذج غير مستقر (أكبر modulus = {mod.max():.3f}).")
    fig, a = plt.subplots(figsize=(4.2, 4.2))
    t = np.linspace(0, 2 * np.pi, 200)
    a.plot(np.cos(t), np.sin(t), "k", lw=1)
    a.scatter(eig.real, eig.imag, color="r", zorder=3)
    a.axhline(0, color="gray", lw=0.5); a.axvline(0, color="gray", lw=0.5)
    a.set_aspect("equal"); a.set_title("Inverse roots / unit circle")
    show_fig(fig)

    st.subheader("ثبات المعاملات: اختبار OLS-CUSUM")
    st.markdown(
        "نرسم المجموع التراكمي للبواقي (مقيّساً). **إذا بقي المسار داخل الحدّين الأحمرين (±1.358 عند 5%) "
        "فالمعاملات ثابتة عبر الزمن**، وإذا خرج منهما فهناك كسر هيكلي محتمل."
    )
    ncols = 2
    nrows = int(np.ceil(k / ncols))
    fig, ax = plt.subplots(nrows, ncols, figsize=(11, 3.2 * nrows))
    ax = np.atleast_1d(ax).ravel()
    all_in = True
    for a, v in zip(ax, names):
        e = res[v].values
        s = np.sqrt((e ** 2).sum() / (len(e) - m.params.shape[0]))
        proc = np.cumsum(e) / (s * np.sqrt(len(e)))
        a.plot(np.arange(1, len(e) + 1) / len(e), proc, "k")
        a.axhline(1.358, color="r", ls="--"); a.axhline(-1.358, color="r", ls="--")
        a.axhline(0, color="gray", lw=0.5); a.set_ylim(-1.9, 1.9)
        a.set_title(f"{v}  (max|S| = {np.abs(proc).max():.2f})")
        all_in &= bool(np.abs(proc).max() < 1.358)
    for a in ax[len(names):]:
        a.axis("off")
    fig.tight_layout()
    show_fig(fig)
    verdict(all_in, "لا دليل على عدم ثبات المعاملات في أي معادلة.",
            "المسار خرج من الحدود في معادلة واحدة على الأقل: احتمال كسر هيكلي.")
    r_code(
        """
roots(var_model)                      # كلها < 1
plot(stability(var_model, type = "OLS-CUSUM"))
# إذا ظهر خطأ figure margins too large: كبّر نافذة Plots أو استعمل pdf()/dev.new()
"""
    )


def page_resid():
    st.header("10) اختبارات البواقي")
    st.markdown(
        "النموذج الجيّد يعطي بواقي **بدون ارتباط ذاتي** و**تباينها ثابت** و**قريبة من التوزيع الطبيعي**. "
        "في هذه الاختبارات الفرضية الصفرية هي سلامة النموذج، لذلك نريد **p > 0.05**."
    )
    lags = st.slider("عدد تأخيرات اختبار الارتباط الذاتي", p + 1, 20, max(12, p + 1))
    rows = []
    w = m.test_whiteness(nlags=lags)
    rows.append(("الارتباط الذاتي (Portmanteau)", w.test_statistic, w.pvalue))
    nm = m.test_normality()
    rows.append(("التوزيع الطبيعي (Jarque-Bera متعدد)", nm.test_statistic, nm.pvalue))
    for v in names:
        a = het_arch(res[v].values, nlags=5)
        rows.append((f"ARCH ({v})", a[0], a[1]))
    tab = pd.DataFrame(rows, columns=["الاختبار", "الإحصاءة", "p-value"]).set_index("الاختبار")
    tab["النتيجة"] = np.where(tab["p-value"] > 0.05, "✅ مقبول", "⚠️ مرفوض")
    st.dataframe(tab.round(4))
    verdict(bool((tab["p-value"] > 0.05).all()), "كل الاختبارات مقبولة: النموذج سليم إحصائياً.",
            "بعض الاختبارات مرفوضة: فكّر في زيادة التأخيرات أو إضافة متغيرات/تعديل التحويلات.")

    st.subheader("رسوم تشخيصية للبواقي")
    v = st.selectbox("المتغير", names, key="resid_var")
    idx = res.index.to_timestamp()
    fig, ax = plt.subplots(1, 3, figsize=(14, 3.5))
    ax[0].plot(idx, res[v], color="k", lw=0.8); ax[0].axhline(0, color="r", lw=0.7)
    ax[0].set_title(f"Residuals: {v}")
    nl = min(16, len(res) // 2 - 1)
    plot_acf(res[v], lags=nl, ax=ax[1], title="ACF of residuals")
    plot_pacf(res[v], lags=nl, ax=ax[2], title="PACF of residuals", method="ywm")
    fig.tight_layout()
    show_fig(fig)
    st.caption("نريد أن تقع كل الأعمدة داخل الحدود الزرقاء (لا ارتباط ذاتي في البواقي).")
    r_code(
        """
serial.test(var_model, lags.pt = 12, type = "PT.asymptotic")
serial.test(var_model, lags.pt = 12, type = "BG")
normality.test(var_model, multivariate.only = TRUE)
arch.test(var_model, lags.multi = 5, multivariate.only = TRUE)
plot(var_model)
"""
    )


def page_granger():
    st.header("11) سببية جرانجر")
    st.markdown(
        """
نقول إن **X يسبّب Y بمفهوم جرانجر** إذا كانت القيم السابقة لـ X تُحسّن التنبؤ بـ Y
(اختبار F على معاملات تأخيرات X في معادلة Y). **H0: X لا يسبّب Y.**
هي سببية *تنبؤية* وليست سببية اقتصادية بالضرورة.
"""
    )
    mat = pd.DataFrame(np.nan, index=names, columns=names)
    for cause in names:
        for effect in names:
            if cause != effect:
                mat.loc[cause, effect] = m.test_causality(effect, cause, kind="f").pvalue
    st.markdown("**جدول p-values** (الصف = السبب، العمود = النتيجة):")
    st.dataframe(mat.round(4))
    sig = [(a, b, mat.loc[a, b]) for a in names for b in names if a != b and mat.loc[a, b] < 0.05]
    if sig:
        for a, b, pv in sig:
            st.success(f"**{a}** يسبّب **{b}** بمفهوم جرانجر (p = {pv:.3f}).")
    else:
        st.info("لا توجد علاقة سببية معنوية عند 5% بين أي زوج.")
    st.markdown("**اختبار جماعي:** هل تسبّب بقية المتغيرات معاً المتغير المحدد؟")
    rows = []
    for v in names:
        others = [x for x in names if x != v]
        pv = m.test_causality(v, others, kind="f").pvalue
        rows.append((v, pv, "نعم" if pv < 0.05 else "لا"))
    st.dataframe(pd.DataFrame(rows, columns=["المتغير التابع", "p-value", "معنوي 5%؟"]).set_index("المتغير التابع").round(4))
    r_code(
        """
for (v in colnames(Ystat)) print(causality(var_model, cause = v)[c("Granger","Instant")])
"""
    )


def page_irf():
    st.header("12) دوال الاستجابة النبضية (IRF)")
    st.markdown(
        """
تقيس IRF **أثر صدمة بحجم انحراف معياري واحد** في أحد المتغيرات على المسار المستقبلي لكل المتغيرات.
نستعمل تفكيك **Cholesky** (الصدمات متعامدة)، وهو يعتمد على **ترتيب المتغيرات**: المتغير الأول يؤثر لحظياً
في كل الباقي، والأخير لا يؤثر لحظياً في أحد. الخط الأزرق هو التقدير، والمنقّط حدود ثقة 95%.
"""
    )
    st.write("**ترتيب Cholesky الحالي:**  " + " → ".join(names))
    orth = st.checkbox("صدمات متعامدة (Cholesky)", value=True)
    np.random.seed(123)
    with st.spinner("جارٍ حساب حدود الثقة..."):
        irf = m.irf(irf_h)
        fig = irf.plot(orth=orth, stderr_type="mc", repl=mc_reps, signif=0.05)
        fig.set_size_inches(12, 2.4 * k)
    show_fig(fig)
    st.info(
        "العناوين تُقرأ هكذا: «A → B» = استجابة B لصدمة في A. إذا احتوت حدود الثقة الصفر فالأثر غير معنوي. "
        "الاستجابات الذاتية تتلاشى بسرعة إذا كان النموذج مستقراً."
    )
    r_code(
        """
irf_res <- irf(var_model, n.ahead = 12, ortho = TRUE, boot = TRUE, runs = 500, ci = 0.95)
plot(irf_res)
"""
    )


def page_fevd():
    st.header("13) تفكيك التباين (FEVD)")
    st.markdown(
        """
يُبيّن **نسبة تباين خطأ التنبؤ** لكل متغير التي تعود إلى صدمات كل متغير (بما فيها صدماته الذاتية)،
عند كل أفق. إذا فسّر المتغير نفسه معظم تباينه فهو *خارجي نسبياً* في النظام.
"""
    )
    fe = m.fevd(irf_h)
    h = st.slider("الأفق المعروض في الجدول", 1, irf_h, irf_h)
    tab = pd.DataFrame(fe.decomp[:, h - 1, :] * 100, index=names, columns=[f"صدمة {c}" for c in names])
    st.markdown(f"**النسب المئوية عند الأفق {h}:**")
    st.dataframe(tab.round(1))
    ncols = 2
    nrows = int(np.ceil(k / ncols))
    fig, ax = plt.subplots(nrows, ncols, figsize=(11, 3.2 * nrows))
    ax = np.atleast_1d(ax).ravel()
    for i, (a, v) in enumerate(zip(ax, names)):
        a.stackplot(range(1, irf_h + 1), fe.decomp[i].T * 100, labels=names)
        a.set_title(f"Variance decomposition of {v}")
        a.set_ylim(0, 100)
    ax[0].legend(loc="center right", fontsize=7)
    for a in ax[len(names):]:
        a.axis("off")
    fig.tight_layout()
    show_fig(fig)
    own = {v: tab.loc[v, f"صدمة {v}"] for v in names}
    st.info("نسبة التفسير الذاتي عند الأفق المختار: " + "، ".join(f"{v}: {x:.0f}%" for v, x in own.items()))
    r_code("fevd_res <- fevd(var_model, n.ahead = 12)\nplot(fevd_res)")


def page_forecast():
    st.header("14) التنبؤ")
    st.markdown(
        f"""
نتنبّأ **{fc_h} فصولاً** إلى الأمام انطلاقاً من آخر {p} مشاهدة، مع مجال ثقة 95%.
في نموذج مستقر **تتقارب التنبؤات تدريجياً نحو المتوسط غير الشرطي** وتتسع مجالات الثقة ثم تستقر.
"""
    )
    fc, lo, hi = m.forecast_interval(Ystat.values[-p:], fc_h, alpha=0.05)
    fidx = pd.period_range(Ystat.index[-1] + 1, periods=fc_h, freq="Q")
    ncols = 2
    nrows = int(np.ceil(k / ncols))
    fig, ax = plt.subplots(nrows, ncols, figsize=(11, 3.2 * nrows))
    ax = np.atleast_1d(ax).ravel()
    for j, (a, v) in enumerate(zip(ax, names)):
        hst = Ystat[v].iloc[-24:]
        a.plot(hst.index.to_timestamp(), hst.values, "k")
        a.plot(fidx.to_timestamp(), fc[:, j], "b")
        a.fill_between(fidx.to_timestamp(), lo[:, j], hi[:, j], color="b", alpha=0.2)
        a.set_title(f"Forecast {v} (95%)")
    for a in ax[len(names):]:
        a.axis("off")
    fig.tight_layout()
    show_fig(fig)

    out = pd.DataFrame(fc, index=fidx.astype(str), columns=names)
    st.markdown("**جدول التنبؤات (على مقياس السلاسل المستعملة في النموذج):**")
    st.dataframe(out.round(3))

    st.subheader("الرجوع إلى الوحدات الأصلية (تنبؤات نقطية)")
    orig = pd.DataFrame(index=fidx.astype(str))
    note = []
    for c in lev.columns:
        d = d_vec[c]
        nm = c if d == 0 else f"D{d}_{c}"
        if d == 0:
            vals = out[nm].values
        elif d == 1:
            vals = lev[c].iloc[-1] + np.cumsum(out[nm].values)
        else:
            note.append(c)
            continue
        if c.startswith("L") and c[1:] in log_vars:
            orig[c[1:]] = np.exp(vals / 100)
        else:
            orig[c] = vals
    st.dataframe(orig.round(3))
    if note:
        st.warning(f"لا يُعاد بناء المتغيرات المفاضلة مرتين: {', '.join(note)}.")
    r_code(
        """
fc <- predict(var_model, n.ahead = 8, ci = 0.95)
fanchart(fc)
# العودة للمستوى (d=1):  exp((last_level + cumsum(fc$fcst[[v]][,"fcst"]))/100)
"""
    )


def page_summary():
    st.header("15) الخلاصة")
    mod = np.abs(1 / m.roots).max()
    w = m.test_whiteness(nlags=max(12, p + 1)).pvalue
    nm = m.test_normality().pvalue
    arch_p = min(het_arch(res[v].values, nlags=5)[1] for v in names)
    gr = [(a, b) for a in names for b in names
          if a != b and m.test_causality(b, a, kind="f").pvalue < 0.05]
    summary = pd.DataFrame(
        {
            "الخطوة": [
                "الاستقرارية", "رتبة التكامل", "عدد التأخيرات", "استقرار النموذج",
                "ارتباط البواقي الذاتي", "طبيعية البواقي", "ARCH (أدنى p)", "سببية جرانجر (5%)",
            ],
            "النتيجة": [
                "كلها I(0)" if all(v == 0 for v in d_vec.values()) else "بعضها مفاضل",
                ", ".join(f"{c}: {d}" for c, d in d_vec.items()),
                f"p = {p} ({crit_label})",
                f"مستقر (max = {mod:.2f})" if mod < 1 else "غير مستقر",
                f"p = {w:.3f}",
                f"p = {nm:.3f}",
                f"p = {arch_p:.3f}",
                "؛ ".join(f"{a}→{b}" for a, b in gr) if gr else "لا توجد",
            ],
        }
    ).set_index("الخطوة")
    st.dataframe(summary)
    st.markdown(
        """
**ملاحظات ختامية**
- البيانات افتراضية، وغالباً مولَّدة كسلاسل AR(1) شبه مستقلة؛ لذلك تكون الاستجابات المتقاطعة ضعيفة
  والنموذج سليماً إحصائياً لكن محدود الدلالة الاقتصادية.
- في بيانات حقيقية: اختبر الكسور الهيكلية، وجرّب أكثر من ترتيب Cholesky، وقارن التنبؤات خارج العيّنة (out-of-sample).
- إذا كانت المتغيرات I(1) ومتكاملة تكاملاً مشتركاً فاستعمل **VECM** بدل VAR في الفروق.
"""
    )


PAGES = [page_intro, page_data, page_desc, page_transform, page_unit_root, page_integration,
         page_johansen, page_lags, page_estimate, page_stability, page_resid, page_granger,
         page_irf, page_fevd, page_forecast, page_summary]

PAGES[STEPS.index(step)]()
