import streamlit as st
import pandas as pd

st.set_page_config(page_title="クーポン照合アプリ（リネームなしVer）", layout="wide")
st.title("🎟️ クーポン照合アプリ（1ファイル・2シート・リネームなし）")

uploaded_file = st.file_uploader("📂 Excelファイル（.xlsx）をアップロードしてください", type="xlsx")

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names

    st.markdown("### 🗂 シート選択")
    sheet1 = st.selectbox("🆕 新しいデータ（依頼表）", sheet_names, key="sheet1")
    sheet2 = st.selectbox("📄 比較対象（CMS）", sheet_names, key="sheet2")

    if st.button("🚀 照合スタート！"):
        df1 = pd.read_excel(uploaded_file, sheet_name=sheet1)
        df2 = pd.read_excel(uploaded_file, sheet_name=sheet2)

        # 列名トリム（空白や改行を除去）
        df1.columns = df1.columns.str.strip()
        df2.columns = df2.columns.str.strip()

        st.write("✅ シート①の列名:", df1.columns.tolist())
        st.write("✅ シート②の列名:", df2.columns.tolist())

        # クーポンコードを共通名にしてマージ準備
        df1["マージ用コード"] = df1["クーポンＣＤ"]
        df2["マージ用コード"] = df2["クーポン番号※"]

        merged = pd.merge(df1, df2, on="マージ用コード", how="outer", indicator=True)

        # 比較対象の列名（元のまま）
        comparison_columns = [
            ("商品・クーポン名称", "クーポン名/商品名※"),
            ("正価税込", "割引前価格（税込）"),
            ("売価税込", "割引後価格（税込）"),
            ("開始日", "利用開始日時(常/キ/エ)"),
            ("終了日", "利用終了日時(常/キ/エ)")
        ]

        # 各項目の一致判定
        for col1, col2 in comparison_columns:
            if col1 in merged.columns and col2 in merged.columns:
                merged[f"{col1} ⇄ {col2} 一致"] = merged[col1] == merged[col2]

        # 判定列
        def get_status(row):
            if row["_merge"] == "left_only":
                return "🆕 新規追加"
            elif row["_merge"] == "right_only":
                return "❌ 削除対象"
            elif any(row.get(f"{c1} ⇄ {c2} 一致") is False for c1, c2 in comparison_columns):
                return "⚠️ 変更あり"
            else:
                return "✅ 一致"

        merged["判定"] = merged.apply(get_status, axis=1)

        # 表示する列を整える（存在するものだけ）
        display_cols = ["マージ用コード", "判定"]
        for col1, col2 in comparison_columns:
            if col1 in merged.columns and col2 in merged.columns:
                display_cols += [col1, col2]

        st.markdown("### ✅ 照合結果")
        st.dataframe(merged[display_cols], use_container_width=True)

        csv = merged[display_cols].to_csv(index=False, encoding="utf-8-sig")
        st.download_button("⬇️ 結果CSVをダウンロード", data=csv, file_name="クーポン照合結果.csv", mime="text/csv")
