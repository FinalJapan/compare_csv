import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="クーポン照合アプリ", layout="wide")
st.title("🎟️ クーポン照合アプリ（最適化版）")

# ---------- アップローダー ----------
st.subheader("1️⃣ ファイルをアップロード（CSVまたはExcel）")

file1 = st.file_uploader("🗂️ ファイル①（最新・新規データ）", type=["csv", "xlsx"], key="file1")
file2 = st.file_uploader("🗂️ ファイル②（旧・比較対象データ）", type=["csv", "xlsx"], key="file2")

# ---------- 読み込み関数 ----------
def load_file(file, label):
    if not file:
        return None
    ext = file.name.split(".")[-1].lower()

    if ext == "csv":
        try:
            df = pd.read_csv(io.StringIO(file.getvalue().decode("utf-8")))
        except:
            df = pd.read_csv(io.StringIO(file.getvalue().decode("shift_jis")))
        st.success(f"✅ {label}: CSVファイルを読み込みました")
        return df

    elif ext == "xlsx":
        xls = pd.ExcelFile(file)
        sheet = st.selectbox(f"📄 {label}: シートを選択", xls.sheet_names, key=label)
        df = pd.read_excel(file, sheet_name=sheet)
        st.success(f"✅ {label}: Excelのシート「{sheet}」を読み込みました")
        return df

    else:
        st.error(f"❌ {label}: 未対応ファイル形式です")
        return None

# ---------- データ読み込み ----------
df1 = load_file(file1, "ファイル①")
df2 = load_file(file2, "ファイル②")

if df1 is not None and df2 is not None:
    st.subheader("2️⃣ 比較設定")

    key1 = st.selectbox("🔑 ファイル①のクーポンコード列", df1.columns, key="key1")
    key2 = st.selectbox("🔑 ファイル②のクーポンコード列", df2.columns, key="key2")

    common_cols = list(set(df1.columns) & set(df2.columns))
    compare_cols = st.multiselect("📝 照合したい列（例：名称、価格、公開期間など）", common_cols)

    if st.button("🚀 照合する"):
        # マージ処理
        merged = pd.merge(
            df1,
            df2,
            left_on=key1,
            right_on=key2,
            how="outer",
            suffixes=('_新', '_旧'),
            indicator=True
        )

        merged["照合結果"] = merged["_merge"].map({
            "both": "一致 or 内容比較",
            "left_only": "🆕 新規追加",
            "right_only": "❌ 削除された"
        })

        # 内容比較
        diff_flags = []
        for col in compare_cols:
            col_new = f"{col}_新"
            col_old = f"{col}_旧"
            if col_new in merged.columns and col_old in merged.columns:
                flag_col = f"{col}が一致？"
                merged[flag_col] = merged[col_new] == merged[col_old]
                diff_flags.append(flag_col)

        # 差異フラグまとめて1つの列に
        if diff_flags:
            merged["変更あり？"] = merged[diff_flags].apply(lambda row: not all(row), axis=1)

        # 表示切替
        st.subheader("3️⃣ 表示設定")
        表示モード = st.radio("表示モードを選んでください", ["差異のあるデータのみ", "すべて表示"], horizontal=True)

        if 表示モード == "差異のあるデータのみ":
            display_df = merged[(merged["照合結果"] != "一致 or 内容比較") | (merged.get("変更あり？") == True)]
            st.info(f"📌 差異のあるデータを表示（{len(display_df)}件）")
        else:
            display_df = merged

        # 表示列の絞り込み（スッキリ表示）
        base_cols = [key1 if key1 in display_df.columns else key2, "照合結果", "変更あり？"]
        new_cols = [f"{col}_新" for col in compare_cols if f"{col}_新" in display_df.columns]
        old_cols = [f"{col}_旧" for col in compare_cols if f"{col}_旧" in display_df.columns]

        final_cols = base_cols + new_cols + old_cols
        st.dataframe(display_df[final_cols], use_container_width=True)

        # ダウンロード機能
        csv = display_df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("⬇️ 結果をCSVでダウンロード", data=csv, file_name="クーポン照合結果.csv", mime="text/csv")
