import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="محاضرة: لغة R", page_icon="📊", layout="wide")

# ---------- RTL + style ----------
st.markdown(
    """
    <style>
    html, body, [class*="css"], .stMarkdown, .stRadio, .stSelectbox, .stTabs {
        direction: rtl; text-align: right; font-family: 'Segoe UI', Tahoma, sans-serif;
    }
    pre, code { direction: ltr !important; text-align: left !important; }
    .card {background:#f5f7fb; border-right:6px solid #276DC3; padding:14px 18px;
           border-radius:8px; margin-bottom:10px; color:#1a1a1a;}
    .card h4 {margin:0 0 6px 0; color:#276DC3;}
    @media (prefers-color-scheme: dark) {
        .card {background:#1e2530; color:#eee;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar navigation ----------
SECTIONS = [
    "🏠 الرئيسية",
    "1️⃣ التعريف بالبرنامج",
    "2️⃣ النشأة والمؤسسة (CRAN)",
    "3️⃣ مجالات الاختصاص",
    "4️⃣ نقاط القوة والضعف",
    "5️⃣ تثبيت البرنامج",
    "🧪 تجربة تفاعلية",
    "📝 اختبار قصير",
]
st.sidebar.title("📊 محاضرة R")
page = st.sidebar.radio("القائمة", SECTIONS)
st.sidebar.markdown("---")
st.sidebar.caption("المصدر الرسمي: https://cran.r-project.org")


def card(title, body):
    st.markdown(f'<div class="card"><h4>{title}</h4>{body}</div>', unsafe_allow_html=True)


# ====================================================================
if page == SECTIONS[0]:
    st.title("📊 لغة وبرنامج R")
    st.subheader("البيئة الحرة للحساب الإحصائي والتمثيل البياني")
    st.write("منصة تفاعلية لمحاضرة تعريفية بـ R: ماهيته، نشأته، اختصاصه، نقاط قوته وضعفه، وطريقة تثبيته.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("سنة البداية", "1993")
    c2.metric("إصدار 1.0.0", "2000")
    c3.metric("إنشاء CRAN", "1997")
    c4.metric("الرخصة", "GNU GPL")
    st.info("محاور المحاضرة موجودة في القائمة الجانبية. اختر محورًا للبدء.")

# ====================================================================
elif page == SECTIONS[1]:
    st.header("1️⃣ التعريف بالبرنامج")
    st.write(
        "**R** لغة برمجة وبيئة برمجية مفتوحة المصدر، موجهة أساسًا للحساب الإحصائي، "
        "تحليل البيانات، والتمثيل البياني. هي مجانية وتعمل على Windows وmacOS وLinux."
    )
    col1, col2 = st.columns(2)
    with col1:
        card("لغة برمجة", "لغة مفسَّرة (interpreted) تدعم البرمجة الدالّية والكائنية، وتعتمد على المتجهات (vectorized).")
        card("بيئة متكاملة", "مفسّر للغة، أدوات رسم، نظام حزم، وتوثيق مدمج (<code>?mean</code>).")
    with col2:
        card("مفتوحة المصدر", "رخصة GNU GPL: حرية الاستخدام والدراسة والتعديل والتوزيع.")
        card("قابلة للتوسعة", "آلاف الحزم الإضافية (packages) تُنزَّل من CRAN بأمر واحد.")
    st.subheader("أول خطوات في R")
    st.code(
        """# عمليات حسابية
x <- c(12, 15, 9, 20, 18)
mean(x)      # المتوسط
sd(x)        # الانحراف المعياري
summary(x)   # ملخص إحصائي

# رسم بياني
hist(x, main = "مثال", col = "steelblue")""",
        language="r",
    )

# ====================================================================
elif page == SECTIONS[2]:
    st.header("2️⃣ النشأة والمؤسسة المعتمدة (CRAN)")
    st.markdown("**المرجع:** [cran.r-project.org](https://cran.r-project.org)")

    events = pd.DataFrame(
        {
            "year": [1976, 1993, 1995, 1997, 2000, 2002],
            "event": [
                "لغة S في مختبرات Bell (جون تشامبرز وزملاؤه)",
                "بداية R على يد روس إيهاكا وروبرت جنتلمان – جامعة أوكلاند (نيوزيلندا)",
                "إصدار R برخصة GNU GPL (مجاني ومفتوح)",
                "تأسيس R Core Team وانطلاق شبكة CRAN",
                "صدور الإصدار المستقر R 1.0.0",
                "تأسيس R Foundation (منظمة غير ربحية، فيينا – النمسا)",
            ],
        }
    )
    st.subheader("الخط الزمني")
    sel = st.select_slider("حرّك لاستعراض المحطات", options=events["year"].tolist(), value=1993)
    row = events[events["year"] == sel].iloc[0]
    card(f"{row['year']}", row["event"])

    fig = go.Figure(
        go.Scatter(
            x=events["year"], y=[0] * len(events), mode="markers+text",
            text=events["year"].astype(str), textposition="top center",
            marker=dict(size=[24 if y == sel else 12 for y in events["year"]],
                        color=["#276DC3" if y == sel else "#9bb7dd" for y in events["year"]]),
            hovertext=events["event"], hoverinfo="text",
        )
    )
    fig.update_yaxes(visible=False, range=[-1, 1])
    fig.update_layout(height=180, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("من يعتمد R؟ ثلاث جهات مترابطة")
    c1, c2, c3 = st.columns(3)
    with c1:
        card("R Core Team", "فريق صغير من المطوّرين يملك صلاحية تعديل الشيفرة المصدرية للنواة.")
    with c2:
        card("R Foundation", "منظمة غير ربحية تدعم تطوير R وتحمي حقوقه وتمثّل المجتمع قانونيًا.")
    with c3:
        card("CRAN", "Comprehensive R Archive Network: شبكة مرايا (mirrors) حول العالم تستضيف R وحزمه وتوثيقه.")

    st.subheader("ماذا نجد في موقع cran.r-project.org؟")
    st.table(
        pd.DataFrame(
            {
                "القسم": ["Download R for Windows / macOS / Linux", "Packages", "Task Views", "Manuals / FAQs", "Mirrors"],
                "الفائدة": [
                    "تنزيل المثبّت الرسمي حسب نظام التشغيل",
                    "قائمة الحزم المتاحة وتوثيقها",
                    "تصنيف الحزم حسب المجال (إحصاء، تعلّم آلي، جينوميات...)",
                    "أدلة رسمية للمبتدئين والمطورين",
                    "اختيار أقرب خادم لتسريع التحميل",
                ],
            }
        )
    )
    st.caption("تفقّد رقم أحدث إصدار وعدد الحزم من الصفحة الرئيسية للموقع لأنها تتغير باستمرار.")

# ====================================================================
elif page == SECTIONS[3]:
    st.header("3️⃣ الاختصاص الذي يميل إليه R")
    st.write("يُعد R لغة **الإحصاء وعلم البيانات** بامتياز. اختر مجالًا لمعرفة أدواته:")

    fields = {
        "📈 الإحصاء والاقتصاد القياسي": ("lm(), glm(), t.test(), survival, lme4, forecast",
                                       "الانحدار، الاختبارات، السلاسل الزمنية، النماذج المختلطة."),
        "🧬 المعلوماتية الحيوية": ("Bioconductor, DESeq2, limma",
                                "تحليل بيانات الجينوم والتعبير الجيني (مشروع Bioconductor مستقل مبني على R)."),
        "📊 التمثيل البياني": ("ggplot2, plotly, lattice",
                             "رسوم بجودة نشر علمي مبنية على 'قواعد الرسم' (Grammar of Graphics)."),
        "🤖 التعلم الآلي": ("caret, tidymodels, randomForest, xgboost",
                          "بناء النماذج التنبؤية وتقييمها."),
        "🌐 التطبيقات والتقارير": ("shiny, rmarkdown, Quarto, flexdashboard",
                                "لوحات تفاعلية وتقارير قابلة للتكرار (reproducible research)."),
        "🏥 الصحة العامة والأبحاث": ("epiR, survival, meta",
                                   "الوبائيات، التحليل التلوي، التجارب السريرية."),
    }
    choice = st.selectbox("المجال", list(fields.keys()))
    pk, desc = fields[choice]
    card(choice, desc)
    st.markdown("**أهم الحزم:**")
    st.code(pk, language="text")

    st.subheader("مثال: رسم باستخدام ggplot2")
    st.code(
        """library(ggplot2)
ggplot(mtcars, aes(wt, mpg, color = factor(cyl))) +
  geom_point(size = 3) +
  geom_smooth(method = "lm", se = FALSE) +
  labs(title = "الاستهلاك مقابل الوزن")""",
        language="r",
    )

# ====================================================================
elif page == SECTIONS[4]:
    st.header("4️⃣ نقاط القوة والضعف")
    st.caption("التقييم أدناه تقديري لأغراض الشرح وليس قياسًا علميًا. عدّل الأوزان حسب رأيك في النقاش.")

    default = {
        "الأدوات الإحصائية": 10, "التمثيل البياني": 9, "المجتمع والحزم": 9,
        "التكلفة (مجاني)": 10, "سهولة التعلم": 5, "السرعة والذاكرة": 5,
        "تطوير تطبيقات الإنتاج": 5,
    }
    with st.expander("⚙️ عدّل التقييم (من 0 إلى 10)"):
        scores = {k: st.slider(k, 0, 10, v) for k, v in default.items()}
    cats = list(scores.keys())
    vals = list(scores.values())
    fig = go.Figure(go.Scatterpolar(r=vals + vals[:1], theta=cats + cats[:1], fill="toself", name="R"))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, 10])), showlegend=False, height=440)
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.success("✅ نقاط القوة")
        st.markdown(
            """
- مجاني ومفتوح المصدر بلا رسوم ترخيص.
- مكتبة إحصائية هائلة، وغالبًا تظهر الطرق الحديثة في R أولًا.
- رسوم بيانية عالية الجودة (ggplot2).
- بحث قابل للتكرار (R Markdown / Quarto).
- مجتمع أكاديمي واسع وتوثيق وفير.
- تعدد المنصات (Windows, macOS, Linux).
- تكامل مع Python وC++ وSQL.
"""
        )
    with c2:
        st.error("⚠️ نقاط الضعف")
        st.markdown(
            """
- منحنى تعلم حاد لغير المبرمجين وصياغة غير متسقة أحيانًا.
- استهلاك الذاكرة: البيانات تُحمَّل غالبًا في الذاكرة (RAM).
- أبطأ من اللغات المترجمة للحسابات الثقيلة دون حزم محسّنة.
- جودة الحزم متفاوتة وبعضها غير مصان جيدًا.
- أقل حضورًا من Python في هندسة البرمجيات والتعلم العميق.
- واجهة النظام الأساسية بسيطة (تُعوَّض بـ RStudio/Positron).
"""
        )

# ====================================================================
elif page == SECTIONS[5]:
    st.header("5️⃣ تثبيت البرنامج")
    st.markdown("**الرابط الرسمي:** [cran.r-project.org](https://cran.r-project.org)")
    os_choice = st.radio("نظام التشغيل", ["Windows", "macOS", "Linux (Ubuntu/Debian)"], horizontal=True)

    if os_choice == "Windows":
        st.markdown(
            """
1. افتح https://cran.r-project.org ثم اضغط **Download R for Windows**.
2. اختر **base** ثم **Download R-x.y.z for Windows**.
3. شغّل الملف `.exe` واتبع المعالج (اللغة، مجلد التثبيت، المكونات).
4. (اختياري) ثبّت **Rtools** من نفس الصفحة إذا أردت بناء حزم من المصدر.
"""
        )
    elif os_choice == "macOS":
        st.markdown(
            """
1. من الموقع اضغط **Download R for macOS**.
2. نزّل ملف `.pkg` المناسب لمعالجك (Apple Silicon أو Intel).
3. شغّل الملف واتبع خطوات التثبيت.
4. (اختياري) ثبّت XQuartz و Xcode Command Line Tools لبعض الحزم.
"""
        )
    else:
        st.markdown("1. اختر **Download R for Linux** ثم توزيعتك. مثال لـ Ubuntu/Debian (للحصول على نسخة أحدث راجع تعليمات CRAN لإضافة المستودع):")
        st.code("sudo apt update\nsudo apt install r-base r-base-dev", language="bash")

    st.subheader("ثم ثبّت واجهة مريحة: RStudio / Posit")
    st.write("RStudio واجهة تطوير مجانية (Desktop) من شركة Posit، وتُثبَّت **بعد** R من موقع posit.co.")

    st.subheader("التحقق من التثبيت وتنزيل أول حزمة")
    st.code(
        """R.version.string               # عرض رقم الإصدار
install.packages("ggplot2")     # تنزيل حزمة من CRAN
library(ggplot2)                # تحميلها في الجلسة
sessionInfo()                   # معلومات البيئة""",
        language="r",
    )
    st.checkbox("✔️ ثبّتُّ R")
    st.checkbox("✔️ ثبّتُّ RStudio")
    st.checkbox("✔️ نزّلتُ أول حزمة")

# ====================================================================
elif page == SECTIONS[6]:
    st.header("🧪 تجربة تفاعلية: ماذا يفعل lm() في R؟")
    st.write("نولّد بيانات ونطابق عليها خطًا مستقيمًا بطريقة المربعات الصغرى، وهي نفس فكرة الدالة `lm()`.")
    c1, c2, c3 = st.columns(3)
    n = c1.slider("حجم العينة", 10, 500, 100)
    slope = c2.slider("الميل الحقيقي", -5.0, 5.0, 2.0, 0.5)
    noise = c3.slider("مستوى الضجيج", 0.0, 10.0, 3.0, 0.5)

    rng = np.random.default_rng(42)
    x = rng.uniform(0, 10, n)
    y = 1 + slope * x + rng.normal(0, noise, n)
    b, a = np.polyfit(x, y, 1)
    r2 = np.corrcoef(x, y)[0, 1] ** 2

    xs = np.linspace(0, 10, 50)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="markers", name="بيانات"))
    fig.add_trace(go.Scatter(x=xs, y=a + b * xs, mode="lines", name="الخط المقدَّر"))
    fig.update_layout(height=420)
    st.plotly_chart(fig, use_container_width=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("الميل المقدَّر", f"{b:.2f}")
    m2.metric("الثابت", f"{a:.2f}")
    m3.metric("R²", f"{r2:.2f}")
    st.code("fit <- lm(y ~ x, data = df)\nsummary(fit)", language="r")
    st.caption("هذه المحاكاة بلغة Python لتوضيح الفكرة داخل المنصة، أما الشيفرة أعلاه فبلغة R.")

# ====================================================================
else:
    st.header("📝 اختبار قصير")
    questions = [
        ("من مبتكرا لغة R؟", ["Ross Ihaka و Robert Gentleman", "Guido van Rossum", "Linus Torvalds"], 0),
        ("ما معنى CRAN؟", ["Comprehensive R Archive Network", "Central R Analysis Node", "Computer R Application Network"], 0),
        ("أي أمر يُنزِّل حزمة من CRAN؟", ["library()", "install.packages()", "source()"], 1),
        ("أي حزمة تُستخدم للرسم البياني؟", ["ggplot2", "survival", "shiny"], 0),
        ("أي من التالي نقطة ضعف في R؟", ["مجاني", "تحميل البيانات غالبًا في الذاكرة", "حزم إحصائية كثيرة"], 1),
    ]
    score = 0
    answered = 0
    for i, (q, opts, correct) in enumerate(questions):
        ans = st.radio(f"{i + 1}. {q}", opts, index=None, key=f"q{i}")
        if ans is not None:
            answered += 1
            if opts.index(ans) == correct:
                score += 1
    if st.button("عرض النتيجة"):
        if answered < len(questions):
            st.warning("أجب عن جميع الأسئلة أولًا.")
        else:
            st.success(f"نتيجتك: {score} / {len(questions)}")
            if score == len(questions):
                st.balloons()
