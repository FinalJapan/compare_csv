import streamlit as st
import pandas as pd

st.set_page_config(page_title="クーポン照合アプリ", layout="wide")
st.title("🎟️ クーポン照合アプリ（1ファイル・2シート照合）")

# アップロード
uploaded_file = st.file_uploader("📂 Excelファイル（.xlsx）を1つアップロードしてください", type="xlsx")

if uploaded_file:
    # Excelファイルを読み込んでシート一覧を取得
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names

    st.markdown("### 🗂 比較したいシートを選択してください")
    sheet1 = st.selectbox("🆕 新しいクーポン（依頼表）", sheet_names, key="sheet1")
    sheet2 = st.selectbox("📄 比較対象（CMS）", sheet_names, key="sheet2")

    if st.button("🚀 照合スタート！"):
        # シート読み込み
        df1 = pd.read_excel(uploaded_file, sheet_name=sheet1)
        df2 = pd.read_excel(uploaded_file, sheet_name=sheet2)

        # 列名をトリム（余分な空白や改行を削除）
        df1.columns = df1.columns.str.strip()
        df2.columns = df2.columns.str.strip()

        # 実際の列名表示（デバッグにも便利）
        st.write("✅ シート① 列名:", list(df1.columns))
        st.write("✅ シート② 列名:", list(df2.columns))

        # 列名マッピング（現場データに対応）
        df1_renamed = df1.rename(columns={
            "クーポンＣＤ": "クーポンコード",
            "商品・クーポン名称": "名称_新",
            "正価税込": "正価_新",
            "売価税込": "売価_新",
            "開始日": "開始_新",
            "終了日": "終了_新"
        })

        df2_renamed = df2.rename(columns={
            "クーポン番号※": "クーポンコード",
            "クーポン名/商品名※": "名称_旧",
            "割引前価格（税込）": "正価_旧",
            "割引後価格（税込）": "売価_旧",
            "利用開始日時(常/キ/エ)": "開始_旧",
            "利用終了日時(常/キ/エ)": "終了_旧"
        })

        # クーポンコードでマージ
        merged = pd.merge(df1_renamed, df2_renamed, on="クーポンコード", how="outer", indicator=True)

        # 各項目の一致判定
        for col in ["名称", "正価", "売価", "開始", "終了"]:
            col_new = f"{col}_新"
            col_old = f"{col}_旧"
            if col_new in merged and col_old in merged:
                merged[f"{col}一致"] = merged[col_new] == merged[col_old]

        # 判定列を作成
        def get_status(row):
            if row["_merge"] == "left_only":
                return "🆕 新規追加"
            elif row["_merge"] == "right_only":
                return "❌ 削除対象"
            elif any([
                row.get("名称一致") is False,
                row.get("正価一致") is False,
                row.get("売価一致") is False,
                row.get("開始一致") is False,
                row.get("終了一致") is False
            ]):
                return "⚠️ 変更あり"
            else:
                return "✅ 一致"

        merged["判定"] = merged.apply(get_status, axis=1)

        # 表示用カラム
        display_cols = [
            "クーポンコード", "判定",
            "名称_新", "名称_旧",
            "正価_新", "正価_旧",
            "売価_新", "売価_旧",
            "開始_新", "開始_旧",
            "終了_新", "終了_旧"
        ]

        st.markdown("### ✅ 照合結果")
        st.dataframe(merged[display_cols], use_container_width=True)

        # CSV出力
        csv = merged[display_cols].to_csv(index=False, encoding="utf-8-sig")
        st.download_button("⬇️ 結果CSVをダウンロード", data=csv, file_name="クーポン照合結果.csv", mime="text/csv")
