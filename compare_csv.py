import streamlit as st
import pandas as pd

st.set_page_config(page_title="クーポン照合アプリ", layout="wide")
st.title("🎟️ クーポン照合アプリ（1ファイル・2シート照合版）")

# ファイルアップロード
file = st.file_uploader("📂 Excelファイルをアップロード", type=["xlsx"])

if file:
    # シート選択
    excel = pd.ExcelFile(file)
    sheet1 = st.selectbox("🗂 新しいクーポン（依頼表）のシートを選んでください", excel.sheet_names, key="sheet1")
    sheet2 = st.selectbox("🗂 比較対象（CMS）のシートを選んでください", excel.sheet_names, key="sheet2")

    if st.button("🚀 照合する"):
        df1 = pd.read_excel(file, sheet_name=sheet1)
        df2 = pd.read_excel(file, sheet_name=sheet2)

        # 列名のマッピング
        columns_1 = {
            "コード": "クーポンＣＤ",
            "名称": "商品・クーポン名称",
            "正価": "正価税込",
            "売価": "売価税込",
            "開始日": "開始日",
            "終了日": "終了日"
        }

        columns_2 = {
            "コード": "クーポン番号※",
            "名称": "クーポン名/商品名※",
            "正価": "割引前価格（税込）",
            "売価": "割引後価格（税込）",
            "開始日": "利用開始日時(常/キ/エ)",
            "終了日": "利用終了日時(常/キ/エ)"
        }

        # 比較用のDataFrameを整形
        df1_renamed = df1.rename(columns={
            columns_1["コード"]: "クーポンコード",
            columns_1["名称"]: "名称_新",
            columns_1["正価"]: "正価_新",
            columns_1["売価"]: "売価_新",
            columns_1["開始日"]: "開始_新",
            columns_1["終了日"]: "終了_新"
        })

        df2_renamed = df2.rename(columns={
            columns_2["コード"]: "クーポンコード",
            columns_2["名称"]: "名称_旧",
            columns_2["正価"]: "正価_旧",
            columns_2["売価"]: "売価_旧",
            columns_2["開始日"]: "開始_旧",
            columns_2["終了日"]: "終了_旧"
        })

        # マージ（クーポンコードで照合）
        merged = pd.merge(df1_renamed, df2_renamed, on="クーポンコード", how="outer", indicator=True)

        # 各項目の一致判定
        for col in ["名称", "正価", "売価", "開始", "終了"]:
            col_new = f"{col}_新"
            col_old = f"{col}_旧"
            if col_new in merged and col_old in merged:
                merged[f"{col}一致"] = merged[col_new] == merged[col_old]

        # 状態カラムを作成
        def 判定(row):
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

        merged["判定"] = merged.apply(判定, axis=1)

        # 表示列を整理
        display_cols = [
            "クーポンコード", "判定",
            "名称_新", "名称_旧",
            "正価_新", "正価_旧",
            "売価_新", "売価_旧",
            "開始_新", "開始_旧",
            "終了_新", "終了_旧"
        ]

        st.success("✅ 照合完了！結果は以下の通り👇")
        st.dataframe(merged[display_cols], use_container_width=True)

        # ダウンロード
        csv = merged[display_cols].to_csv(index=False, encoding="utf-8-sig")
        st.download_button("⬇️ 結果CSVをダウンロード", data=csv, file_name="照合結果.csv", mime="text/csv")


# デバッグ用：列名を表示
st.write("🧾 シート①の列名一覧（依頼表）:", list(df1.columns))
st.write("🧾 シート②の列名一覧（CMS）:", list(df2.columns))

