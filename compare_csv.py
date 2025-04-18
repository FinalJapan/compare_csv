import pandas as pd
import streamlit as st

st.title("📑 複数シート対応！Excel比較アプリ")

uploaded_file = st.file_uploader("Excelファイルをアップロード", type=["xlsx"])

if uploaded_file:
    # ファイル全体読み込み
    excel = pd.ExcelFile(uploaded_file)

    # シート選択
    sheet_names = excel.sheet_names
    sheet1 = st.selectbox("比較対象：シート①を選択", sheet_names)
    sheet2 = st.selectbox("比較対象：シート②を選択", sheet_names, index=1 if len(sheet_names) > 1 else 0)

    if st.button("📌 比較する！"):
        # シートをそれぞれ読み込み
        df1 = pd.read_excel(uploaded_file, sheet_name=sheet1)
        df2 = pd.read_excel(uploaded_file, sheet_name=sheet2)

        # キー列選択（共通の列にしてね）
        common_cols = list(set(df1.columns) & set(df2.columns))
        if not common_cols:
            st.error("共通の列がないため比較できません！")
        else:
            key = st.selectbox("🔑 比較するキー列", common_cols)

            # 比較処理
            merged = pd.merge(df1, df2, on=key, how='outer', suffixes=('_sheet1', '_sheet2'), indicator=True)
            merged['状態'] = merged['_merge'].map({
                'both': '一致 or 内容違い',
                'left_only': 'シート1にだけ存在',
                'right_only': 'シート2にだけ存在'
            })

            st.success("✅ 比較完了！結果を以下に表示します。")
            st.dataframe(merged)
