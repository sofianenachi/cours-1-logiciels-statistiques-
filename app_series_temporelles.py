# -*- coding: utf-8 -*-
"""
منصة تفاعلية لتدريس السلاسل الزمنية
التشغيل:
1) افتح Terminal أو CMD داخل مجلد الملف
2) ثبّت المكتبات:
   pip install streamlit numpy pandas matplotlib plotly statsmodels
3) شغّل:
   streamlit run app_series_temporelles.py
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.seasonal import seasonal_decompose

st.set_page_config(
    page_title="منصة السلاسل الزمنية",
    page_icon="📈",
    layout="wide",
)

# ---------- تنسيق الواجهة ----------
st.markdown("""
<style>
html, body, [class*="css"] { direction: rtl; text-align: right; }
.block-container { padding-top: 1.5rem; }
h1, h2, h3 { text-align: right; }
</style>
""", unsafe_allow_html=True)

st.title("📈 منصة تفاعلية: السلاسل الزمنية والاستقرارية")
st.markdown(
    "مورد تعليمي تفاعلي لطلبة الاقتصاد والإحصاء: مكونات السلسلة الزمنية، "
    "محاكاة السلاسل، مفهوم الاستقرارية، اختبارات الكشف عنها، وأمثلة تطبيقية."
)

with st.sidebar:
    st.header("إعدادات المحاكاة")
    n_obs = st.slider("عدد المشاهدات", 60, 500, 180, 10)
    seed = st.number_input("بذرة التوليد (لإعادة نفس النتائج)", min_value=0, max_value=99999, value=42)
    st.caption("غيّر الإعدادات ثم انتقل بين أقسام المنصة.")

rng = np.random.default_rng(int(seed))


def make_series(kind, n, seed_value, noise=1.0, trend=0.03, season_amp=8.0, phi=0.65):
    """توليد سلاسل تعليمية اصطناعية."""
    r = np.random.default_rng(int(seed_value))
    t = np.arange(n)
    eps = r.normal(0, noise, n)

    if kind == "مستقرة حول متوسط":
        y = 50 + eps
    elif kind == "اتجاهية":
        y = 20 + trend * t + eps
    elif kind == "موسمية":
        y = 50 + season_amp * np.sin(2 * np.pi * t / 12) + eps
    elif kind == "اتجاهية وموسمية":
        y = 20 + trend * t + season_amp * np.sin(2 * np.pi * t / 12) + eps
    elif kind == "مسار عشوائي":
        y = np.cumsum(eps)
    elif kind == "AR(1)":
        y = np.zeros(n)
        for i in range(1, n):
            y[i] = phi * y[i - 1] + eps[i]
        y += 50
    else:
        y = eps
    return pd.Series(y, index=pd.RangeIndex(1, n + 1, name="الزمن"), name="القيمة")


def plot_series(series, title="السلسلة الزمنية"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=series.index, y=series.values, mode="lines",
        name="القيمة", line=dict(width=2)
    ))
    fig.update_layout(
        title=title, xaxis_title="الزمن", yaxis_title="القيمة",
        template="plotly_white", height=420,
        margin=dict(l=20, r=20, t=60, b=30)
    )
    return fig


def stationarity_tests(series):
    x = pd.Series(series).dropna().astype(float)
    adf_result = adfuller(x, autolag="AIC")
    try:
        kpss_result = kpss(x, regression="c", nlags="auto")
        kpss_stat, kpss_p = kpss_result[0], kpss_result[1]
        kpss_error = None
    except Exception as exc:
        kpss_stat, kpss_p, kpss_error = np.nan, np.nan, str(exc)

    return {
        "adf_stat": adf_result[0],
        "adf_p": adf_result[1],
        "adf_lags": adf_result[2],
        "adf_n": adf_result[3],
        "adf_crit": adf_result[4],
        "kpss_stat": kpss_stat,
        "kpss_p": kpss_p,
        "kpss_error": kpss_error,
    }


def show_tests(series):
    res = stationarity_tests(series)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("اختبار ديكي–فولر الموسع (ADF)")
        st.write("**فرضية العدم H₀:** السلسلة تحتوي على جذر وحدة، أي أنها غير مستقرة.")
        st.metric("إحصائية ADF", f"{res['adf_stat']:.4f}")
        st.metric("القيمة الاحتمالية p-value", f"{res['adf_p']:.4f}")
        if res["adf_p"] < 0.05:
            st.success("عند مستوى 5%: نرفض H₀؛ توجد أدلة على الاستقرارية.")
        else:
            st.warning("عند مستوى 5%: لا نرفض H₀؛ لا توجد أدلة كافية على الاستقرارية.")
        st.caption("قيم ADF الحرجة:")
        st.json({k: round(v, 4) for k, v in res["adf_crit"].items()})
    with c2:
        st.subheader("اختبار KPSS")
        st.write("**فرضية العدم H₀:** السلسلة مستقرة حول متوسط ثابت.")
        if np.isnan(res["kpss_p"]):
            st.warning("تعذر حساب KPSS لهذه السلسلة: " + str(res["kpss_error"]))
        else:
            st.metric("إحصائية KPSS", f"{res['kpss_stat']:.4f}")
            st.metric("القيمة الاحتمالية p-value", f"{res['kpss_p']:.4f}")
            if res["kpss_p"] < 0.05:
                st.warning("عند مستوى 5%: نرفض H₀؛ توجد أدلة ضد الاستقرارية.")
            else:
                st.success("عند مستوى 5%: لا نرفض H₀؛ النتائج متوافقة مع الاستقرارية.")
    st.info(
        "نصيحة منهجية: لا تعتمد على اختبار واحد فقط. تختلف فرضية العدم بين ADF وKPSS؛ "
        "اقرأ النتيجتين مع الرسم البياني والمعرفة الاقتصادية."
    )


tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1. مكونات السلسلة",
    "2. محاكاة السلاسل",
    "3. مفهوم الاستقرارية",
    "4. اختبارات الاستقرارية",
    "5. أمثلة تطبيقية",
])

# ---------- القسم 1 ----------
with tab1:
    st.header("مكونات السلسلة الزمنية")
    st.write(
        "يمكن تحليل السلسلة الزمنية إلى أربعة مكونات تعليمية أساسية، "
        "مع ملاحظة أن وجودها جميعًا ليس شرطًا في كل سلسلة."
    )
    st.markdown("""
    - **الاتجاه العام (Trend, T):** حركة طويلة الأجل صاعدة أو هابطة.
    - **الموسمية (Seasonality, S):** نمط يتكرر خلال فترة ثابتة، مثل أشهر السنة.
    - **الدورية (Cycle, C):** تقلبات متوسطة أو طويلة الأجل لا يلزم أن يكون طولها ثابتًا.
    - **العنصر العشوائي (Irregular, I):** صدمات وتقلبات غير منتظمة لا تفسرها المكونات الأخرى.

    **النموذج الجمعي:** \\(Y_t = T_t + S_t + C_t + I_t\\)  
    **النموذج الضربي:** \\(Y_t = T_t \\times S_t \\times C_t \\times I_t\\)

    يستخدم النموذج الجمعي عندما تكون سعة التقلبات الموسمية تقريبًا ثابتة، والضربي عندما تتغير السعة مع مستوى السلسلة.
    """)
    kind = st.selectbox(
        "اختر سلسلة لعرض مكوناتها",
        ["اتجاهية وموسمية", "اتجاهية", "موسمية", "مستقرة حول متوسط", "مسار عشوائي"],
        key="components_kind"
    )
    demo = make_series(kind, n_obs, seed, noise=2.0, trend=0.15, season_amp=8.0)
    st.plotly_chart(plot_series(demo, f"مثال: {kind}"), use_container_width=True)
    if st.button("محاولة تفكيك السلسلة إلى اتجاه وموسمية وبواقي", key="decompose"):
        if len(demo) < 24:
            st.warning("اختر 24 مشاهدة على الأقل للحصول على تفكيك موسمي تعليمي.")
        else:
            try:
                decomposition = seasonal_decompose(demo, model="additive", period=12, extrapolate_trend="freq")
                fig = make_subplots(
                    rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.06,
                    subplot_titles=("السلسلة الأصلية", "الاتجاه", "الموسمية", "البواقي")
                )
                for row, values, name in [
                    (1, demo, "الأصلية"),
                    (2, decomposition.trend, "الاتجاه"),
                    (3, decomposition.seasonal, "الموسمية"),
                    (4, decomposition.resid, "البواقي"),
                ]:
                    fig.add_trace(go.Scatter(x=values.index, y=values.values, mode="lines", name=name), row=row, col=1)
                fig.update_layout(height=760, template="plotly_white", showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
                st.caption("هذا التفكيك يفترض موسمية دورها 12؛ غيّر الفترة وفق طبيعة بياناتك.")
            except Exception as exc:
                st.error(f"تعذر التفكيك: {exc}")

# ---------- القسم 2 ----------
with tab2:
    st.header("محاكاة سلاسل زمنية")
    st.write("غيّر نوع السلسلة ومعلماتها ولاحظ كيف يتغير سلوكها.")
    sim_kind = st.selectbox(
        "نوع السلسلة",
        ["مستقرة حول متوسط", "اتجاهية", "موسمية", "اتجاهية وموسمية", "مسار عشوائي", "AR(1)"],
        key="simulation_kind"
    )
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        sigma = st.slider("انحراف الضوضاء المعيارية", 0.1, 10.0, 2.0, 0.1)
    with col_b:
        trend_rate = st.slider("معامل الاتجاه", -0.2, 0.5, 0.08, 0.01)
    with col_c:
        phi = st.slider("معامل AR(1) — φ", -0.95, 0.95, 0.65, 0.05)
    simulated = make_series(
        sim_kind, n_obs, seed, noise=sigma, trend=trend_rate, season_amp=8.0, phi=phi
    )
    st.plotly_chart(plot_series(simulated, f"محاكاة: {sim_kind}"), use_container_width=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("المتوسط العيني", f"{simulated.mean():.3f}")
    m2.metric("الانحراف المعياري العيني", f"{simulated.std():.3f}")
    m3.metric("عدد المشاهدات", len(simulated))
    st.download_button(
        "تنزيل السلسلة المحاكاة بصيغة CSV",
        data=simulated.rename("Y").to_csv(index_label="t").encode("utf-8-sig"),
        file_name="simulated_time_series.csv",
        mime="text/csv"
    )
    st.markdown("""
    **تجربة مقترحة:** قارن بين «مستقرة حول متوسط» و«مسار عشوائي».  
    هل يبدو المتوسط ثابتًا؟ هل يتغير التشتت؟ هل تعود السلسلة إلى مستوى قريب من متوسطها؟
    """)

# ---------- القسم 3 ----------
with tab3:
    st.header("مفهوم الاستقرارية")
    st.markdown("""
    تكون السلسلة **مستقرة بالمعنى الضعيف (Weak / Covariance Stationarity)** إذا تحققت الشروط الآتية:

    1. \\(E(Y_t)=\\mu\\): المتوسط ثابت ولا يعتمد على الزمن.
    2. \\(Var(Y_t)=\\sigma^2\\): التباين ثابت ومحدود.
    3. \\(Cov(Y_t,Y_{t-k})=\\gamma_k\\): التغاير يعتمد على الفجوة الزمنية \\(k\\)، لا على الزمن \\(t\\) نفسه.

    **لماذا تهمنا الاستقرارية؟** كثير من نماذج السلاسل الزمنية تفترض استقرارية السلسلة أو بواقي النموذج. وقد يؤدي الانحدار بين سلاسل غير مستقرة إلى نتائج زائفة ما لم توجد علاقة تكامل مشترك مناسبة.

    **طرق شائعة لمعالجة عدم الاستقرارية:**
    - إزالة الاتجاه أو الموسمية عندما يكون ذلك مبررًا اقتصاديًا.
    - أخذ الفرق الأول: \\(\\Delta Y_t = Y_t - Y_{t-1}\\).
    - التحويل اللوغاريتمي عند وجود نمو مضاعف أو تباين يزداد مع المستوى.
    - فحص وجود كسر هيكلي أو تغير في النظام الاقتصادي قبل اتخاذ القرار.
    """)
    compare_kind = st.selectbox(
        "اختر سلسلة لفحصها بصريًا",
        ["مستقرة حول متوسط", "اتجاهية", "مسار عشوائي", "موسمية"],
        key="stationarity_visual"
    )
    s = make_series(compare_kind, n_obs, seed, noise=2.0, trend=0.15, season_amp=8.0)
    st.plotly_chart(plot_series(s, f"الفحص البصري: {compare_kind}"), use_container_width=True)
    st.markdown("**ملاحظة:** الرسم وحده لا يكفي للحكم النهائي؛ استخدم الاختبارات مع التحليل الاقتصادي.")

# ---------- القسم 4 ----------
with tab4:
    st.header("اختبارات الكشف عن الاستقرارية")
    st.markdown("""
    - **ADF (Augmented Dickey–Fuller):** فرضية العدم هي وجود جذر وحدة. غالبًا ما تشير قيمة p صغيرة (مثل أقل من 0.05) إلى رفض فرضية العدم.
    - **KPSS:** فرضية العدم هي الاستقرارية حول متوسط أو اتجاه بحسب المواصفة. في هذا التطبيق نستخدم الاستقرارية حول متوسط ثابت.
    - **اختبارات إضافية يمكن دراستها:** Phillips–Perron (PP)، Zivot–Andrews للكسر الهيكلي، واختبارات الجذر الموسمي عند الحاجة.

    **تنبيه:** نتيجة الاختبار حساسة لطول الإبطاء، ووجود ثابت أو اتجاه، وحجم العينة، والكسور الهيكلية.
    """)
    test_kind = st.selectbox(
        "اختر السلسلة التي تريد اختبارها",
        ["مستقرة حول متوسط", "اتجاهية", "موسمية", "اتجاهية وموسمية", "مسار عشوائي", "AR(1)"],
        key="test_kind"
    )
    test_series = make_series(test_kind, n_obs, seed, noise=2.0, trend=0.15, season_amp=8.0, phi=0.65)
    st.plotly_chart(plot_series(test_series, f"السلسلة المختارة للاختبار: {test_kind}"), use_container_width=True)
    show_tests(test_series)
    if st.checkbox("اختبار الفرق الأول للسلسلة نفسها"):
        differenced = test_series.diff().dropna()
        st.plotly_chart(plot_series(differenced, "الفرق الأول ΔY"), use_container_width=True)
        show_tests(differenced)

# ---------- القسم 5 ----------
with tab5:
    st.header("أمثلة تطبيقية في الاقتصاد")
    st.write(
        "الأمثلة التالية اصطناعية لأغراض التدريس، وليست بيانات رسمية. "
        "يمكن استبدالها لاحقًا ببيانات الناتج المحلي أو التضخم أو البطالة أو سعر الصرف."
    )
    example = st.selectbox(
        "اختر المثال",
        [
            "التضخم: سلسلة مستقرة حول متوسط",
            "الناتج المحلي: اتجاه صاعد",
            "سعر الصرف: مسار عشوائي تقريبي",
            "المبيعات الشهرية: اتجاه وموسمية",
        ]
    )
    r = np.random.default_rng(int(seed) + 100)
    t = np.arange(n_obs)
    if example == "التضخم: سلسلة مستقرة حول متوسط":
        y = 4.0 + r.normal(0, 0.8, n_obs)
        unit = "%"
    elif example == "الناتج المحلي: اتجاه صاعد":
        y = 100 + 0.7 * t + r.normal(0, 5, n_obs)
        unit = "مؤشر افتراضي"
    elif example == "سعر الصرف: مسار عشوائي تقريبي":
        y = 130 + np.cumsum(r.normal(0.05, 0.7, n_obs))
        unit = "وحدة نقدية افتراضية"
    else:
        y = 100 + 0.25 * t + 15 * np.sin(2 * np.pi * t / 12) + r.normal(0, 4, n_obs)
        unit = "مؤشر مبيعات افتراضي"
    example_series = pd.Series(y, index=pd.RangeIndex(1, n_obs + 1, name="الزمن"), name="القيمة")
    st.plotly_chart(plot_series(example_series, example), use_container_width=True)
    st.caption(f"وحدة القياس: {unit}")
    st.subheader("الاختبارات الإحصائية")
    show_tests(example_series)
    st.subheader("تطبيق الفرق الأول")
    diff_series = example_series.diff().dropna()
    st.plotly_chart(plot_series(diff_series, "الفرق الأول للمثال المختار"), use_container_width=True)
    show_tests(diff_series)

st.divider()
st.markdown("""
**أسئلة للمناقشة داخل المحاضرة**
1. ما الفرق بين الاتجاه والموسمية والدورية؟
2. لماذا لا يكفي أن يكون المتوسط العيني ثابتًا للحكم بالاستقرارية؟
3. ما الفرق بين فرضية العدم في ADF وKPSS؟
4. متى يكون أخذ الفرق الأول مناسبًا، ومتى قد يؤدي إلى الإفراط في التفريق؟
5. كيف يمكن أن تؤثر الأزمة الاقتصادية أو الكسر الهيكلي في نتائج اختبارات الاستقرارية؟
""")
st.caption("إعداد تعليمي قابل للتطوير — تحقق من مواصفات الاختبارات وخصائص بياناتك قبل الاستنتاج البحثي.")
