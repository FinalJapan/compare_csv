import streamlit as st
import pandas as pd

st.title("📊 CSVファイル比較くん（Streamlit版）")

# ファイルアップロード
file1 = st.file_uploader("CSVファイル①をアップロード", type="csv")
file2 = st.file_uploader("CSVファイル②をアップロード", type="csv")

# ファイル読み込み（エンコード対策付き）
try:
    df1 = pd.read_csv(file1, encoding="utf-8")
except UnicodeDecodeError:
    df1 = pd.read_csv(file1, encoding="shift_jis")

try:
    df2 = pd.read_csv(file2, encoding="utf-8")
except UnicodeDecodeError:
    df2 = pd.read_csv(file2, encoding="shift_jis")


    # 比較キー選択（1列目をデフォルトに）
    key = st.selectbox("🔑 比較するキー（IDなど）を選んでください", df1.columns)

    if st.button("📌 比較する"):
        # データ突き合わせ
        merged = pd.merge(df1, df2, on=key, how='outer', suffixes=('_file1', '_file2'), indicator=True)

        # 状態の説明を追加
        merged['状態'] = merged['_merge'].map({
            'both': '一致 or 内容違い',
            'left_only': '削除された',
            'right_only': '新規追加'
        })

        st.success("✅ 比較完了！結果は以下のとおり👇")

        # 表示
        st.dataframe(merged)

        # ダウンロードボタン
        csv = merged.to_csv(index=False, encoding='utf-8-sig')
        st.download_button("⬇️ 結果をCSVでダウンロード", data=csv, file_name='比較結果.csv', mime='text/csv')

