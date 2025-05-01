import streamlit as st
import pandas as pd
from difflib import get_close_matches

def get_similar_column(columns, keyword):
    columns = [str(col).strip() for col in columns]  # ←ここを修正
    matches = get_close_matches(keyword, columns, n=1, cutoff=0.6)
    return matches[0] if matches else None


# ページ設定
st.set_page_config(page_title="クーポン照合アプリ", layout="wide")
st.title("🎟️ クーポン照合アプリ")

# ファイルアップロード
uploaded_file = st.file_uploader("📂 Excelファイル（.xlsx）をアップロードしてください", type="xlsx")

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names

    st.markdown("### 🗂 シート選択")
    sheet1 = st.selectbox("🆕 元データ（依頼表）", sheet_names, key="sheet1")
    sheet2 = st.selectbox("📄 比較対象（CMS）", sheet_names, key="sheet2")

    if st.button("🚀 照合スタート！"):
        # データ読み込み（依頼表は4行目から）
        df1 = pd.read_excel(uploaded_file, sheet_name=sheet1, header=3)
        df2 = pd.read_excel(uploaded_file, sheet_name=sheet2, header=0)

        # 列名の前後スペース除去
        df1.columns = df1.columns.str.strip()
        df2.columns = df2.columns.str.strip()

        # 列名一覧確認
        with st.expander("📝 シート①（依頼表）の列名", expanded=False):
            st.write(df1.columns.tolist())
        with st.expander("📝 シート②（CMS）の列名", expanded=False):
            st.write(df2.columns.tolist())

        # 🔍 マージキー（クーポンコード）列を自動取得
        key1 = get_similar_column(df1.columns, "クーポンＣＤ")
        key2 = get_similar_column(df2.columns, "クーポン番号※")

        if not key1 or not key2:
            st.error("❌ クーポンコードの列が見つかりませんでした。列名を確認してください。")
            st.stop()

        df1["マージ用コード"] = df1[key1]
        df2["マージ用コード"] = df2[key2]

        # 🔍 比較対象の列ペア（キーワードベースで自動取得）
        comparison_keywords = [
            ("商品・クーポン名称", "クーポン名/商品名※"),
            ("正価税込", "割引前価格（税込）"),
            ("売価税込", "割引後価格（税込）"),
            ("開始日", "利用開始日時(常/キ/エ)"),
            ("終了日", "利用終了日時(常/キ/エ)")
        ]

        comparison_columns = []
        for kw1, kw2 in comparison_keywords:
            col1 = get_similar_column(df1.columns, kw1)
            col2 = get_similar_column(df2.columns, kw2)
            if col1 and col2:
                comparison_columns.append((col1, col2))

        if len(comparison_columns) == 0:
            st.error("❌ 比較対象の列が見つかりませんでした。")
            st.stop()

        # 🔁 マージ処理（outer joinで差分も見える）
        merged = pd.merge(df1, df2, on="マージ用コード", how="outer", indicator=True)

        # 一致フラグ追加
        for col1, col2 in comparison_columns:
            merged[f"{col1} ⇄ {col2} 一致"] = merged[col1] == merged[col2]

        # 判定列の作成
        def get_status(row):
            if row["_merge"] != "both":
                return "❌"
            for col1, col2 in comparison_columns:
                match_col = f"{col1} ⇄ {col2} 一致"
                if match_col in row and row[match_col] is False:
                    return "❌"
            return "✅"

        merged["判定"] = merged.apply(get_status, axis=1)

        # 表示用の列を準備
        display_cols = ["マージ用コード", "判定"]
        renamed_cols = {"マージ用コード": "クーポンコード", "判定": "判定"}

        for col1, col2 in comparison_columns:
            display_cols.extend([col1, col2])
            renamed_cols[col1] = f"{col1}（依頼表）"
            renamed_cols[col2] = f"{col2}（CMS）"

        df_display = merged[display_cols].rename(columns=renamed_cols)

        # 結果表示（縦スクロール対応）
        st.markdown("### ✅ 照合結果")
        st.data_editor(
            df_display,
            use_container_width=True,
            height=700,
            disabled=True
        )

        # CSVダウンロード
        csv = df_display.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("⬇️ 結果CSVをダウンロード", data=csv, file_name="クーポン照合結果.csv", mime="text/csv")
