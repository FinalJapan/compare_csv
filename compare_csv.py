import streamlit as st
import pandas as pd

st.set_page_config(page_title="クーポン照合アプリ", layout="wide")
st.title("🎟️ クーポン照合アプリ")

uploaded_file = st.file_uploader("📂 Excelファイル（.xlsx）をアップロードしてください", type="xlsx")

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names

    st.markdown("### 🗂 シート選択")
    sheet1 = st.selectbox("🆕 元データ（依頼表）", sheet_names, key="sheet1")
    sheet2 = st.selectbox("📄 比較対象（CMS）", sheet_names, key="sheet2")

    if st.button("🚀 照合スタート！"):
        # ファイル読み込み
        df1 = pd.read_excel(uploaded_file, sheet_name=sheet1, header=3)
        df2 = pd.read_excel(uploaded_file, sheet_name=sheet2, header=0)

        # 列名トリム
        df1.columns = df1.columns.str.strip()
        df2.columns = df2.columns.str.strip()

        # 列名表示（折りたたみ）
        with st.expander("📝 シート①（依頼表）の列名一覧", expanded=False):
            st.write(df1.columns.tolist())

        with st.expander("📝 シート②（CMS）の列名一覧", expanded=False):
            st.write(df2.columns.tolist())

        # マージキー
        df1["マージ用コード"] = df1["クーポンＣＤ"]
        df2["マージ用コード"] = df2["クーポン番号※"]

        merged = pd.merge(df1, df2, on="マージ用コード", how="outer", indicator=True)

        # 比較カラム
        comparison_columns = [
            ("商品・クーポン名称", "クーポン名/商品名※"),
            ("正価税込", "割引前価格（税込）"),
            ("売価税込", "割引後価格（税込）"),
            ("開始日", "利用開始日時(常/キ/エ)"),
            ("終了日", "利用終了日時(常/キ/エ)")
        ]

        # 一致判定
        for col1, col2 in comparison_columns:
            if col1 in merged.columns and col2 in merged.columns:
                merged[f"{col1} ⇄ {col2} 一致"] = merged[col1] == merged[col2]

        # 判定列（✅ / ❌）
        def get_status(row):
            if row["_merge"] != "both":
                return "❌"
            for col1, col2 in comparison_columns:
                if f"{col1} ⇄ {col2} 一致" in row and row[f"{col1} ⇄ {col2} 一致"] is False:
                    return "❌"
            return "✅"

        merged["判定"] = merged.apply(get_status, axis=1)

        # 表示列＋リネーム
        display_cols = ["マージ用コード", "判定"]
        renamed_cols = {
            "マージ用コード": "クーポンコード",
            "判定": "判定"
        }

        for col1, col2 in comparison_columns:
            if col1 in merged.columns and col2 in merged.columns:
                display_cols += [col1, col2]
                renamed_cols[col1] = f"{col1}①"
                renamed_cols[col2] = f"{col2}②"

        df_display = merged[display_cols].rename(columns=renamed_cols)

        # 表示（縦スクロール対応、横スクロールなし）
        st.markdown("### ✅ 照合結果（全件表示）")
        st.data_editor(
            df_display,
            use_container_width=True,
            height=700,
            disabled=True
        )

        # ダウンロード
        csv = df_display.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("⬇️ 結果CSVをダウンロード", data=csv, file_name="クーポン照合結果.csv", mime="text/csv")
