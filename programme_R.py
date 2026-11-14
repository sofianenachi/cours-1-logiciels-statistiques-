import io
import re

import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="تعلّم لغة R", page_icon="📊", layout="wide")
st.markdown(
    """<style>
.block-container{direction:rtl;text-align:right}
[data-testid=stSidebar]{direction:rtl;text-align:right}
pre,code,textarea,input,.stCodeBlock{direction:ltr!important;text-align:left!important}
</style>""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------ بيانات الدرس
STUDENTS = pd.DataFrame(
    {
        "id": range(1, 11),
        "gender": list("FMFMFMFMFM"),
        "age": [22, 24, 23, 25, 22, 26, 24, 23, 25, 27],
        "height": [165, 178, 160, 182, 168, 175, 162, 180, 170, 185],
        "weight": [58, 75, 52, 80, 60, 72, 55, 78, 63, 82],
        "score": [14.5, 12, 16, 10.5, 15, 11, 17, 13.5, 12.5, 9.5],
    }
)
SCORE = "14.5, 12, 16, 10.5, 15, 11, 17, 13.5, 12.5, 9.5"


# ------------------------------------------------------------------ دوال مساعدة
def g(x):
    """تنسيق شبيه بـ R (7 أرقام معنوية)."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "NA"
    return f"{x:.7g}"


def rvec(vals):
    return "[1] " + " ".join(g(float(v)) for v in vals)


def parse_vec(text):
    out = []
    for t in re.split(r"[,\s;]+", text.strip()):
        if not t:
            continue
        out.append(np.nan if t == "NA" else float(t))
    return out


def r_summary(x):
    x = np.array(x, dtype=float)
    x = x[~np.isnan(x)]
    q = np.quantile(x, [0, 0.25, 0.5, 0.75, 1])  # type 7 = défaut de R
    vals = [q[0], q[1], q[2], x.mean(), q[3], q[4]]
    names = ["Min.", "1st Qu.", "Median", "Mean", "3rd Qu.", "Max."]
    return pd.DataFrame([[float(f"{v:.4g}") for v in vals]], columns=names, index=[""])


def r_str(df):
    lines = [f"'data.frame':\t{len(df)} obs. of  {df.shape[1]} variables:"]
    w = max(len(c) for c in df.columns)
    for c in df.columns:
        s = df[c]
        if pd.api.types.is_integer_dtype(s):
            t, vals = "int", [str(v) for v in s.head(10)]
            more = len(s) > 10
        elif pd.api.types.is_float_dtype(s):
            t, vals = "num", [g(v) for v in s.head(10)]
            more = len(s) > 10
        else:
            t, vals = "chr", [f'"{v}"' for v in s.head(4)]
            more = len(s) > 4
        lines.append(f" $ {c.ljust(w)}: {t}  {' '.join(vals)}{' ...' if more else ''}")
    return "\n".join(lines)


def num_cols(df):
    return list(df.select_dtypes("number").columns)


def cat_cols(df):
    return [c for c in df.columns if c not in num_cols(df)]


def get_df():
    return st.session_state.get("df", STUDENTS.copy())


def csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8")


def xlsx_bytes(df):
    buf = io.BytesIO()
    df.to_excel(buf, sheet_name="students", index=False)
    return buf.getvalue()


# ------------------------------------------------------------------ الصفحة الرئيسية
def home():
    st.title("📊 تعلّم لغة R — تطبيق تفاعلي")
    st.caption("مقياس: برمجيات إحصائية حرة — بناءً على المحاضرة 2 وسلسلة الأعمال الموجّهة FICHE TD 1")
    st.subheader("أهداف المحاضرة")
    st.markdown(
        """
- إنشاء **الكائنات** وتسميتها وفحصها (قيم، متجهات، عوامل، مصفوفات، قوائم)
- تطبيق الدوال الإحصائية: `mean()` و`summary()` و`var()` و`sd()`
- استيراد بيانات **CSV** و**Excel** والتحقق منها
- إنشاء **أطر البيانات** واستكشافها
- كتابة **سكربت R** منظم وتشغيله
"""
    )
    c = st.columns(4)
    c[0].metric("المحاور", 7)
    c[1].metric("تمارين TD", 7)
    c[2].metric("ملاحظات في بيانات الطلبة", len(STUDENTS))
    c[3].metric("متغيرات", STUDENTS.shape[1])
    st.info("اختر المحور من القائمة الجانبية. كل صفحة تعرض **كود R المكافئ** لما تفعله، ليسهل نقله إلى RStudio.")


# ------------------------------------------------------------------ المحور 1
def axis1():
    st.header("المحور 1 – الخطوات الأولى في بيئة عمل R")
    st.markdown(
        """
- **التعليقات** تبدأ بالرمز `#` وتتجاهل R كل ما بعده في السطر.
- **المساعدة**: `?mean` أو `help(mean)`.
- **الحزم**: `install.packages("name")` مرة واحدة، ثم `library(name)` في كل جلسة.
- **ساحة العمل**: `getwd()` لمعرفتها و`setwd("new path")` لتغييرها (أو استعمل New Project).
"""
    )
    st.subheader("مولّد أوامر الحزم")
    pkg = st.text_input("اسم الحزمة", "readxl")
    st.code(f'install.packages("{pkg}")   # مرة واحدة فقط\nlibrary({pkg})               # في بداية كل جلسة\n?{pkg}', "r")
    st.subheader("مولّد setwd")
    path = st.text_input("المسار", "C:/Users/student/R_course")
    st.code(f'getwd()\nsetwd("{path}")\nlist.files()', "r")
    st.caption("تذكير: استعمل `/` أو `\\\\` في المسارات على Windows، وليس `\\` المفردة.")


# ------------------------------------------------------------------ المحور 2
RESERVED = ["if", "else", "repeat", "while", "function", "for", "next", "break", "TRUE", "FALSE", "NULL", "Inf", "NaN", "NA", "in"]
COMMON = ["c", "mean", "data", "sum", "t", "df", "var", "sd", "median"]


def r_class(s):
    s = s.strip()
    if s in ("TRUE", "FALSE"):
        return "logical"
    if re.fullmatch(r"-?\d+L", s):
        return "integer"
    if re.fullmatch(r"-?\d+(\.\d+)?([eE][-+]?\d+)?", s):
        return "numeric"
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return "character"
    if s.startswith("factor("):
        return "factor"
    return None


def axis2():
    st.header("المحور 2 – إنشاء الكائنات وتعريفها")
    t1, t2, t3, t4 = st.tabs(["الإسناد والأنواع", "قواعد التسمية", "المتجهات", "البنى الخمس"])
    with t1:
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم الكائن", "x")
        val = c2.text_input("القيمة (جرّب 42L أو \"Amine\" أو TRUE)", "10")
        cl = r_class(val)
        if cl:
            st.code(f"{name} <- {val}\nclass({name})\n[1] \"{cl}\"", "r")
        else:
            st.error(f"Error: object '{val}' not found — النص يجب أن يكون بين علامتي اقتباس.")
        st.table(
            pd.DataFrame(
                {"النوع": ["Numeric", "Integer", "Character", "Logical", "Factor"],
                 "مثال": ["3.14", "42L", '"Amine"', "TRUE", 'factor(c("F","M"))'],
                 "class()": ["numeric", "integer", "character", "logical", "factor"]}
            )
        )
    with t2:
        nm = st.text_input("اختبر اسماً", "age1")
        ok = bool(re.fullmatch(r"[A-Za-z.][A-Za-z0-9._]*", nm)) and not re.match(r"\.\d", nm)
        if nm in RESERVED:
            st.error("❌ كلمة محجوزة في R.")
        elif not ok:
            st.error("❌ اسم غير صحيح: لا يجوز أن يبدأ برقم أو يحتوي رموزاً خاصة أو فراغات.")
        else:
            st.success("✅ اسم صحيح.")
            if nm in COMMON:
                st.warning("⚠️ يتطابق مع اسم دالة شائعة — يُفضّل تجنبه.")
            if nm != nm.lower():
                st.info("تذكير: R حساسة لحالة الأحرف، فـ `" + nm + "` و`" + nm.lower() + "` كائنان مختلفان. والمفضّل نمط snake_case.")
    with t3:
        v = st.text_input("المتجه c( … )", "22, 24, 23, 25, 22")
        try:
            a = np.array(parse_vec(v))
            code = f"ages <- c({v})\nlength(ages)\nclass(ages)"
            st.code(code + f"\n[1] {len(a)}\n[1] \"numeric\"", "r")
            i = st.slider("ages[i]", 1, len(a), min(2, len(a)))
            th = st.number_input("ages[ages > …]", value=float(np.median(a)))
            st.code(f"ages[{i}]\n{g(a[i-1])}\nages[ages > {g(th)}]\n{rvec(a[a > th])}\nages * 2\n{rvec(a * 2)}", "r")
        except ValueError:
            st.error("أدخل أرقاماً مفصولة بفواصل.")
    with t4:
        st.table(
            pd.DataFrame(
                {"البنية": ["Vector", "Factor", "Matrix", "List", "Data frame"],
                 "الوصف": ["بعد واحد، نوع واحد", "متجه فئوي له مستويات", "بعدان، نوع واحد", "كائنات من أي نوع", "جدول: أعمدة بأنواع مختلفة وبنفس الطول"],
                 "تنشأ بـ": ["c(), 1:10, seq()", "factor()", "matrix()", "list()", "data.frame(), read.csv()"]}
            )
        )
        r, c_ = st.columns(2)
        nr = r.slider("nrow", 1, 5, 2)
        nc = c_.slider("ncol", 1, 5, 3)
        st.code(f"m <- matrix(1:{nr*nc}, nrow = {nr}, ncol = {nc})", "r")
        st.dataframe(pd.DataFrame(np.arange(1, nr * nc + 1).reshape(nc, nr).T, index=[f"[{i},]" for i in range(1, nr + 1)], columns=[f"[,{j}]" for j in range(1, nc + 1)]))
        st.caption("R تملأ المصفوفة **بالأعمدة** أولاً.")


# ------------------------------------------------------------------ المحور 3
def axis3():
    st.header("المحور 3 – الدوال الأساسية والإحصاء الوصفي")
    txt = st.text_input("المتجه (اكتب NA لقيمة مفقودة)", SCORE)
    try:
        x = np.array(parse_vec(txt))
    except ValueError:
        st.error("أدخل أرقاماً مفصولة بفواصل.")
        return
    na_rm = st.toggle("na.rm = TRUE", value=True)
    has_na = bool(np.isnan(x).any())
    clean = x[~np.isnan(x)]
    if len(clean) < 2:
        st.warning("أدخل قيمتين على الأقل.")
        return

    def f(fn):
        return "NA" if (has_na and not na_rm) else g(float(fn(clean)))

    c = st.columns(4)
    c[0].metric("mean", f(np.mean))
    c[1].metric("median", f(np.median))
    c[2].metric("var (n−1)", f(lambda a: np.var(a, ddof=1)))
    c[3].metric("sd", f(lambda a: np.std(a, ddof=1)))
    arg = ", na.rm = TRUE" if na_rm else ""
    st.code(f"score <- c({txt})\nmean(score{arg})\nmedian(score{arg})\nvar(score{arg})\nsd(score{arg})\nsummary(score)", "r")
    if has_na and not na_rm:
        st.warning("وُجدت قيمة مفقودة: النتيجة NA ما لم تستعمل `na.rm = TRUE`.")
    st.subheader("summary()")
    st.dataframe(r_summary(x), width="stretch")
    with st.expander("🔍 التحقق من var() و sd() بالصيغة اليدوية"):
        n = len(clean)
        s2 = float(((clean - clean.mean()) ** 2).sum() / (n - 1))
        st.latex(r"s^2=\frac{\sum_{i=1}^{n}(x_i-\bar{x})^2}{n-1}\qquad s=\sqrt{s^2}")
        st.code(f"n <- length(score)\nsum((score - mean(score))^2) / (n - 1)\n[1] {g(s2)}\nsqrt(var(score))\n[1] {g(s2**0.5)}\nround(sd(score), 2)\n[1] {round(s2**0.5, 2)}", "r")
        st.caption("R تحسب التباين **العيني** بالمقام n − 1 وليس n.")
    st.subheader("دوال أخرى")
    st.dataframe(
        pd.DataFrame(
            {"الدالة": ["length", "sum", "min / max", "range", "quantile(x, 0.25)"],
             "النتيجة": [len(x), g(clean.sum()), f"{g(clean.min())} / {g(clean.max())}", f"{g(clean.min())} {g(clean.max())}", g(float(np.quantile(clean, 0.25)))]}
        ),
        hide_index=True,
    )


# ------------------------------------------------------------------ المحور 4
SEMI = "id;gender;age;height;weight;score\n1;F;22;165;58;14,5\n2;M;24;178;75;12\n3;F;23;160;52;16\n"


def axis4():
    st.header("المحور 4 – استيراد بيانات CSV و Excel")
    t1, t2 = st.tabs(["استيراد ملف", "مشكلة الفاصلة المنقوطة"])
    with t1:
        up = st.file_uploader("ارفع ملف CSV أو XLSX (أو اترك الفراغ لاستعمال بيانات الطلبة)", type=["csv", "xlsx"])
        c = st.columns(3)
        header = c[0].checkbox("header = TRUE", True)
        sep = c[1].selectbox("sep", [",", ";", "\t"], format_func=lambda s: {"\t": "\\t"}.get(s, s))
        dec = c[2].selectbox("dec", [".", ","])
        df = STUDENTS.copy()
        code = 'students <- read.csv("students.csv")'
        if up is not None:
            try:
                if up.name.endswith(".xlsx"):
                    xl = pd.ExcelFile(up)
                    sh = st.selectbox("الورقة (sheet)", xl.sheet_names)
                    df = xl.parse(sh)
                    code = f'library(readxl)\nexcel_sheets("{up.name}")\nstudents_xl <- read_excel("{up.name}", sheet = "{sh}")'
                else:
                    df = pd.read_csv(up, sep=sep, decimal=dec, header=0 if header else None)
                    code = f'students <- read.csv("{up.name}", header = {str(header).upper()}, sep = "{sep if sep != chr(9) else chr(92)+"t"}", dec = "{dec}")'
            except Exception as e:
                st.error(f"تعذّر الاستيراد: {e}")
        st.session_state["df"] = df
        st.code(code, "r")
        if df.shape[1] == 1:
            st.warning("كل البيانات في عمود واحد ← الفاصل خاطئ: جرّب `sep = \";\"` أو `read.csv2()`.")
        st.markdown("**head(students)**")
        st.dataframe(df.head(6), width="stretch")
        st.markdown("**str(students)**")
        st.code(r_str(df), "r")
        st.markdown("**التحقق من الاستيراد**")
        na = df.isna().sum()
        st.code(f"dim(students)\n[1] {len(df)} {df.shape[1]}\nanyNA(students)\n[1] {str(bool(na.sum())).upper()}\ncolSums(is.na(students))\n{na.to_string()}", "r")
        st.caption("✅ تُستعمل هذه البيانات في المحور 5.")
    with t2:
        st.markdown("Excel بإعدادات فرنسية/عربية يحفظ CSV بـ **فاصلة منقوطة** و**فاصلة عشرية**.")
        st.code(SEMI, "text")
        wrong = pd.read_csv(io.StringIO(SEMI), sep=",")
        st.markdown("`read.csv(\"file.csv\")` ← خطأ: عمود واحد")
        st.dataframe(wrong, width="stretch")
        right = pd.read_csv(io.StringIO(SEMI), sep=";", decimal=",")
        st.markdown("`read.csv2(\"file.csv\")` أو `read.csv(\"file.csv\", sep = \";\", dec = \",\")` ← صحيح")
        st.dataframe(right, width="stretch")
    with st.expander("CSV مقابل Excel"):
        st.markdown("`read_excel()` تُرجع **tibble** (أعمدتها الرقمية `<dbl>`)، بينما `read.csv()` تقرأ الأعداد الصحيحة `int`. استعمل `as.data.frame()` للحصول على إطار بيانات كلاسيكي.")


# ------------------------------------------------------------------ المحور 5
def axis5():
    st.header("المحور 5 – أطر البيانات")
    df = get_df()
    if "df" not in st.session_state:
        st.caption("تُستعمل بيانات الطلبة الافتراضية. يمكنك استيراد ملفك من المحور 4.")
    nums, cats = num_cols(df), cat_cols(df)
    t1, t2, t3, t4 = st.tabs(["الاستكشاف", "الانتقاء والتصفية", "متغير جديد (BMI)", "إحصاءات حسب الفئات"])
    with t1:
        st.code("dim(students); names(students)", "r")
        st.write("الأبعاد:", df.shape, "— الأسماء:", list(df.columns))
        n = st.slider("n", 1, len(df), min(3, len(df)))
        c = st.columns(2)
        c[0].markdown(f"`head(students, {n})`")
        c[0].dataframe(df.head(n))
        c[1].markdown(f"`tail(students, {n})`")
        c[1].dataframe(df.tail(n))
        st.markdown("`summary(students)`")
        st.dataframe(df.describe().T.rename(columns={"25%": "1st Qu.", "50%": "Median", "mean": "Mean"}), width="stretch")
    with t2:
        col = st.selectbox("العمود", df.columns)
        st.code(f"students${col}", "r")
        st.write(df[col].tolist())
        row = st.number_input("الصف", 1, len(df), 3)
        st.code(f'students[{row}, ]\nstudents[{row}, "{col}"]  # = {df.loc[row-1, col]}', "r")
        st.dataframe(df.iloc[[row - 1]])
        if nums:
            nc = st.selectbox("شرط على متغير رقمي", nums, index=nums.index("score") if "score" in nums else 0)
            op = st.selectbox("العملية", [">=", ">", "<=", "<", "==", "!="])
            lim = st.number_input("القيمة", value=float(df[nc].median()))
            mask = eval(f"df[nc] {op} lim")
            st.code(f"students[students${nc} {op} {g(lim)}, ]", "r")
            st.dataframe(df[mask])
            st.write(f"عدد الأسطر: **{int(mask.sum())}**")
    with t3:
        if {"weight", "height"} <= set(df.columns):
            d2 = df.copy()
            d2["bmi"] = (d2.weight / (d2.height / 100) ** 2).round(2)
            st.code("students$bmi <- round(students$weight / (students$height / 100)^2, 2)\nstudents$bmi", "r")
            st.code(rvec(d2.bmi), "r")
            st.dataframe(d2, width="stretch")
            st.caption(f"الآن: {len(d2)} obs. of {d2.shape[1]} variables")
        else:
            st.info("هذا الجدول لا يحتوي على الأعمدة weight و height.")
    with t4:
        if nums and cats:
            cg = st.selectbox("متغير الفئات", cats)
            vn = st.selectbox("المتغير الرقمي", nums, index=nums.index("score") if "score" in nums else 0)
            fn = st.selectbox("الدالة", ["mean", "sd", "median", "min", "max"])
            st.code(f"table(students${cg})\naggregate({vn} ~ {cg}, data = students, FUN = {fn})", "r")
            c = st.columns(2)
            c[0].dataframe(df[cg].value_counts().rename_axis(cg).reset_index(name="n"), hide_index=True)
            res = df.groupby(cg)[vn].agg(fn).reset_index()
            c[1].dataframe(res, hide_index=True)
            st.bar_chart(res, x=cg, y=vn)
        if len(nums) >= 2:
            a, b = st.columns(2)
            v1 = a.selectbox("x", nums, index=nums.index("height") if "height" in nums else 0)
            v2 = b.selectbox("y", nums, index=nums.index("weight") if "weight" in nums else 1)
            st.code(f"cor(students${v1}, students${v2})\n[1] {g(float(df[v1].corr(df[v2])))}", "r")
            st.scatter_chart(df, x=v1, y=v2)


# ------------------------------------------------------------------ المحور 6
def axis6():
    st.header("المحور 6 – كتابة سكربتات R وتشغيلها")
    c = st.columns(2)
    title = c[0].text_input("العنوان", "Mean BMI by gender")
    author = c[1].text_input("المؤلف", "(your name)")
    inp = c[0].text_input("ملف الإدخال", "students.csv")
    out = c[1].text_input("ملف الإخراج", "bmi_by_gender.csv")
    wd = st.text_input("مجلد العمل (اتركه فارغاً لاستعمال مشروع RStudio)", "")
    setup = f'setwd("{wd}")\n' if wd else ""
    script = f"""# ============================================================
# Title  : {title}
# Author : {author}
# Input  : {inp}
# Output : {out}
# ============================================================

# 1. Setup ---------------------------------------------------
rm(list = ls())
{setup}
# 2. Import --------------------------------------------------
students <- read.csv("{inp}")

# 3. Inspection ----------------------------------------------
str(students)
anyNA(students)

# 4. Analysis ------------------------------------------------
students$bmi <- round(students$weight / (students$height / 100)^2, 2)
bmi_by_gender <- aggregate(bmi ~ gender, data = students, FUN = mean)
bmi_by_gender$bmi <- round(bmi_by_gender$bmi, 2)
print(bmi_by_gender)

# 5. Export --------------------------------------------------
write.csv(bmi_by_gender, "{out}", row.names = FALSE)
"""
    st.code(script, "r")
    st.download_button("⬇️ تحميل السكربت .R", script, "analysis_students.R")
    d = STUDENTS.assign(bmi=(STUDENTS.weight / (STUDENTS.height / 100) ** 2).round(2))
    st.markdown("**ناتج `print(bmi_by_gender)`:**")
    st.dataframe(d.groupby("gender").bmi.mean().round(2).reset_index(), hide_index=True)
    st.subheader("طرق التشغيل")
    st.table(pd.DataFrame({"الإجراء": ["السطر الحالي/التحديد", "السكربت كاملاً", "من وحدة التحكم", "من الطرفية"],
                           "الطريقة": ["Ctrl+Enter", "Ctrl+Shift+Enter أو Source", 'source("lesson_script.R")', "Rscript lesson_script.R"]}))
    st.subheader("ممارسات جيدة")
    st.markdown("""
- علّق على غرض كل مقطع، لا على كل سطر.
- ابدأ من **بيئة نظيفة** وتأكد أن السكربت يعمل كاملاً.
- حمّل كل الحزم `library()` في **أعلى** السكربت.
- لا تعدّل ملف البيانات الأصلي: احفظ النتائج في ملفات جديدة.
- استعمل **المسارات النسبية** أو مشروع RStudio.
- `Ctrl+Shift+C` لتعليق الأسطر المحددة.
""")


# ------------------------------------------------------------------ TD
TD = [
    ("التمرين 1 – الكائنات والمتجهات",
     ["x=12 و y=5: المجموع، الجداء، القسمة، وباقي القسمة `%%`.",
      "temp <- c(18, 21, 19, 25, 23, 20, 22): الطول، العنصر الثالث، القيم > 20.",
      'ما صنف "R" و TRUE و temp؟'],
     "x <- 12; y <- 5\nx + y; x * y; x / y; x %% y\ntemp <- c(18, 21, 19, 25, 23, 20, 22)\nlength(temp)\ntemp[3]\ntemp[temp > 20]\nclass(\"R\"); class(TRUE); class(temp)",
     '17 | 60 | 2.4 | 2\n[1] 7\n[1] 19\n[1] 21 25 23 22\n"character" | "logical" | "numeric"',
     ("باقي قسمة 12 على 5 =", 2.0)),
    ("التمرين 2 – الإحصاء الوصفي",
     ["grades <- c(8, 12.5, 15, 9, 14, 16.5, 11, 13, 10, 18)",
      "المتوسط، الوسيط، التباين، الانحراف المعياري، summary().",
      "تحقق أن sd = sqrt(var).",
      "أضف NA واحسب المتوسط مع na.rm وبدونها."],
     "grades <- c(8, 12.5, 15, 9, 14, 16.5, 11, 13, 10, 18)\nmean(grades); median(grades); var(grades); sd(grades)\nsummary(grades)\nall.equal(sd(grades), sqrt(var(grades)))\ngrades2 <- c(grades, NA)\nmean(grades2)\nmean(grades2, na.rm = TRUE)",
     "12.7 | 12.75 | 10.62222 | 3.259175\n   Min. 1st Qu.  Median    Mean 3rd Qu.    Max.\n   8.00   10.25   12.75   12.70   14.75   18.00\nTRUE | NA | 12.7",
     ("تباين grades (قرّبه إلى رقمين عشريين) =", 10.62)),
    ("التمرين 3 – استيراد CSV",
     ["حدد مجلد العمل واستورد students.csv في students.", "اعرض أول 3 أسطر والأبعاد والبنية.", "كم متغيراً رقمياً؟ وأي متغير نصي؟"],
     'setwd("C:/Users/student/R_course")\nstudents <- read.csv("students.csv")\nhead(students, 3)\ndim(students)\nstr(students)',
     "[1] 10 6\nخمسة متغيرات رقمية (id, age, height, weight, score)؛ gender هو الوحيد النصي.",
     ("عدد المتغيرات الرقمية =", 5.0)),
    ("التمرين 4 – استيراد Excel",
     ["ثبّت readxl وحمّلها واعرض أوراق students.xlsx.", "استورد الورقة في students_xl وقارن صنفها بصنف students.", "حوّلها إلى data.frame كلاسيكي."],
     'install.packages("readxl"); library(readxl)\nexcel_sheets("students.xlsx")\nstudents_xl <- read_excel("students.xlsx", sheet = "students")\nclass(students); class(students_xl)\nstudents_xl <- as.data.frame(students_xl)\nclass(students_xl)',
     '"data.frame"\n"tbl_df" "tbl" "data.frame"\n"data.frame"', None),
    ("التمرين 5 – إنشاء إطار بيانات",
     ["climate بالأعمدة city, jan, jul لخمس مدن (Oran, Algiers, Constantine, Annaba, Tlemcen).", "أضف amplitude = jul − jan.", "المدن ذات المدى > 16، ثم متوسط المدى."],
     'climate <- data.frame(\n  city = c("Oran","Algiers","Constantine","Annaba","Tlemcen"),\n  jan = c(11,12,7,12,8), jul = c(26,27,25,27,26))\nclimate$amplitude <- climate$jul - climate$jan\nclimate[climate$amplitude > 16, ]\nmean(climate$amplitude)',
     "         city jan jul amplitude\n3 Constantine   7  25        18\n5     Tlemcen   8  26        18\n[1] 16.2",
     ("متوسط المدى =", 16.2)),
    ("التمرين 6 – استكشاف بيانات الطلبة",
     ["متوسط وانحراف age و height و weight.", "كم طالباً score ≥ 12؟ ومتوسط نقاطهم؟", "متوسط النقطة حسب الجنس، وارتباط age و score."],
     "mean(students$age); sd(students$age)\nsum(students$score >= 12)\nmean(students$score[students$score >= 12])\naggregate(score ~ gender, data = students, FUN = mean)\ncor(students$age, students$score)",
     "24.1 | 1.66333 ; 172.5 | 8.746428 ; 67.5 | 11.13802\n7 | 14.35714\nF 15.0 | M 11.3\n[1] -0.7604991\nالتفسير: ارتباط سالب (r ≈ −0.76) والعينة صغيرة (10) فالنتائج وصفية ولا تُعمَّم.",
     ("عدد الطلبة بنقطة ≥ 12 =", 7.0)),
    ("التمرين 7 – سكربت كامل",
     ["استورد students.csv وأنشئ bmi واحسب متوسطه حسب الجنس (رقمان عشريان).", "اطبع النتيجة واحفظها في bmi_by_gender.csv.", "أضف ترويسة وتعليقات وشغّله بزر Source."],
     "students <- read.csv(\"students.csv\")\nstudents$bmi <- round(students$weight / (students$height / 100)^2, 2)\nbmi_by_gender <- aggregate(bmi ~ gender, data = students, FUN = mean)\nbmi_by_gender$bmi <- round(bmi_by_gender$bmi, 2)\nprint(bmi_by_gender)\nwrite.csv(bmi_by_gender, \"bmi_by_gender.csv\", row.names = FALSE)",
     "  gender   bmi\n1      F 21.13\n2      M 23.87",
     ("متوسط BMI للإناث =", 21.13)),
]


def td():
    st.header("🧪 FICHE TD 1 – التمارين مع التصحيح")
    st.caption("حاول الحل في RStudio أولاً، ثم تحقق من إجابتك واطلع على الحل.")
    st.download_button("⬇️ students.csv", csv_bytes(STUDENTS), "students.csv")
    st.download_button("⬇️ students.xlsx", xlsx_bytes(STUDENTS), "students.xlsx")
    for i, (title, tasks, code, out, q) in enumerate(TD):
        with st.expander(title, expanded=(i == 0)):
            for t in tasks:
                st.markdown(f"- {t}")
            if q:
                a = st.number_input(q[0], value=None, key=f"q{i}", placeholder="اكتب إجابتك")
                if a is not None:
                    st.success("✅ صحيح!") if abs(a - q[1]) < 0.006 else st.error("❌ حاول مجدداً")
            if st.toggle("إظهار الحل", key=f"s{i}"):
                st.code(code, "r")
                st.code(out, "text")
    if st.button("حساب الأجوبة النموذجية بـ pandas للتحقق"):
        gr = pd.Series([8, 12.5, 15, 9, 14, 16.5, 11, 13, 10, 18])
        st.write({"mean": gr.mean(), "var": gr.var(), "sd": gr.std(),
                  "cor(age,score)": STUDENTS.age.corr(STUDENTS.score),
                  "mean BMI by gender": STUDENTS.assign(bmi=STUDENTS.weight / (STUDENTS.height / 100) ** 2).groupby("gender").bmi.mean().round(2).to_dict()})


# ------------------------------------------------------------------ الملاحق
ERRORS = [
    ("object 'x' not found", "خطأ إملائي أو في حالة الأحرف، أو لم يُنشأ الكائن", "تحقق من الكتابة؛ نفّذ السطر الذي ينشئه"),
    ("cannot open the connection / No such file", "اسم الملف أو مجلد العمل خاطئ", "getwd() و list.files() ثم صحّح المسار"),
    ('could not find function "read_excel"', "الحزمة غير محمَّلة", "library(readxl)"),
    ("there is no package called 'readxl'", "الحزمة غير مثبّتة", 'install.packages("readxl")'),
    ("unexpected symbol / unexpected ')'", "نقص فاصلة أو علامة اقتباس أو قوس", "أعد قراءة السطر وتحقق من أزواج الأقواس"),
    ("دالة تُرجع NA", "قيم مفقودة في البيانات", "أضف na.rm = TRUE"),
    ("كل البيانات في عمود واحد", "الفاصل خاطئ", 'sep = ";" أو read.csv2()'),
    ("أعداد مقروءة كنصوص", "فاصلة عشرية أو نص داخل العمود", 'dec = ","؛ وتحقق بـ str()'),
]
REF = [
    ("إسناد قيمة", "x <- 10"), ("إنشاء متجه", "c(1, 2, 3), 1:10, seq(0, 1, by = 0.1)"),
    ("المتوسط، التباين، الانحراف", "mean(x), var(x), sd(x)"), ("إحصاءات ملخِّصة", "summary(x)"),
    ("استيراد CSV", 'read.csv("file.csv") أو read.csv2("file.csv")'),
    ("استيراد Excel", 'library(readxl); read_excel("file.xlsx", sheet = 1)'),
    ("فحص إطار بيانات", "head(), str(), dim(), summary(), names()"), ("اختيار عمود", 'df$col أو df[, "col"]'),
    ("تصفية الأسطر", "df[df$col > 10, ]"), ("متغير جديد", "df$new <- df$a / df$b"),
    ("إحصاءات حسب الفئات", "aggregate(y ~ g, data = df, FUN = mean)"),
    ("تصدير CSV", 'write.csv(df, "out.csv", row.names = FALSE)'), ("تشغيل سكربت", 'source("script.R")'),
]


def appendix():
    st.header("الملاحق")
    t1, t2, t3 = st.tabs(["الأخطاء الشائعة", "مرجع سريع", "مجموعة البيانات"])
    with t1:
        q = st.text_input("🔎 ابحث في الأخطاء", "")
        rows = [r for r in ERRORS if q.lower() in " ".join(r).lower()]
        st.dataframe(pd.DataFrame(rows, columns=["الرسالة أو العَرَض", "السبب المحتمل", "الحل"]), hide_index=True, width="stretch")
    with t2:
        q = st.text_input("🔎 ابحث في المرجع", "")
        rows = [r for r in REF if q.lower() in " ".join(r).lower()]
        st.dataframe(pd.DataFrame(rows, columns=["المهمة", "الكود"]), hide_index=True, width="stretch")
    with t3:
        st.markdown("بيانات افتراضية لأغراض التدريس: `gender` (F أنثى، M ذكر)، الطول بالسنتيمتر، الوزن بالكيلوغرام، `score` من 20.")
        st.dataframe(STUDENTS, hide_index=True)


# ------------------------------------------------------------------ اختبار
QUIZ = [
    ("ما رمز الإسناد المتعارف عليه في R؟", ["<-", "==", ":=", "=>"], 0),
    ("أي اسم كائن غير صحيح؟", ["age1", "mean_score", "1age", "score.2"], 2),
    ("ناتج class(42L)؟", ["numeric", "integer", "character", "factor"], 1),
    ("بأي مقام تحسب var() التباين؟", ["n", "n + 1", "n − 1", "n − 2"], 2),
    ("ناتج mean(c(10, 12, NA, 14)) بدون na.rm؟", ["12", "NA", "0", "Error"], 1),
    ("أي دالة تقرأ ملفات .xlsx (حزمة readxl)؟", ["read.csv()", "read_excel()", "source()", "load()"], 1),
    ("ملف CSV كله في عمود واحد، ما الحل؟", ["حذف الملف", "تغيير sep إلى \";\" أو read.csv2()", "استعمال head()", "إعادة تشغيل R"], 1),
    ("أي دالة تحسب المتوسط حسب الفئات؟", ["aggregate()", "dim()", "names()", "rm()"], 0),
]


def quiz():
    st.header("📝 اختبر نفسك")
    with st.form("quiz"):
        ans = [st.radio(f"{i+1}. {q}", opts, index=None, key=f"qz{i}") for i, (q, opts, _) in enumerate(QUIZ)]
        done = st.form_submit_button("تصحيح")
    if done:
        score = sum(a == opts[k] for a, (_, opts, k) in zip(ans, QUIZ))
        st.metric("النتيجة", f"{score} / {len(QUIZ)}")
        for i, (a, (q, opts, k)) in enumerate(zip(ans, QUIZ)):
            if a != opts[k]:
                st.caption(f"السؤال {i+1}: الجواب الصحيح «{opts[k]}»")
        if score == len(QUIZ):
            st.balloons()


# ------------------------------------------------------------------ التنقل
PAGES = {
    "🏠 الرئيسية": home,
    "1️⃣ الخطوات الأولى": axis1,
    "2️⃣ الكائنات": axis2,
    "3️⃣ الإحصاء الوصفي": axis3,
    "4️⃣ استيراد البيانات": axis4,
    "5️⃣ أطر البيانات": axis5,
    "6️⃣ السكربتات": axis6,
    "🧪 تمارين TD": td,
    "📚 الملاحق": appendix,
    "📝 اختبار": quiz,
}
with st.sidebar:
    st.title("R 📊")
    page = st.radio("المحاور", list(PAGES), label_visibility="collapsed")
    st.caption("إعداد التطبيق مبني على محاضرة الأستاذ ناشي سفيان — 2026/2027")
PAGES[page]()
