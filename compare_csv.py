import streamlit as st
import pandas as pd
import io

st.title("📁 Excel / CSV 比較アプリ（2ファイル個別アップロード版）")

file1 = st.file_uploader("ファイル①をアップロード", type=["csv", "xlsx"], key="file1")
file2 = st.file_uploader("ファイル②をアップロード", type=["csv", "xlsx"], key="file2")

df_list = []

def read_uploaded_file(file, file_label):
    if not file:
        return None

    filename = file.name
    ext = filename.split('.')[-1].lower()

    st.subheader(f"{file_label}: {filename}")

    if ext == 'csv':
        try:
            df = pd.read_csv(io.StringIO(file.getvalue().decode("utf-8")))
        except UnicodeDecodeError:
            df = pd.read_csv(io.StringIO(file.getvalue().decode("shift_jis")))
        st.success("✅ CSVとして読み込み完了！")
        return df

    elif ext == 'xlsx':
        xls = pd.ExcelFile(file)
        sheet = st.selectbox(f"{file_label}のシートを選択", xls.sheet_names, key=f"{file_label}_sheet")
        df = pd.read_excel(file, sheet_name=sheet)
        st.success(f"✅ Excelのシート「{sheet}」を読み込み完了！")
        return df

    else:
        st.error("❌ 対応していないファイル形式です（CSVまたはExcelのみ）")
        return None

# ファイルを読み込み
df1 = read_uploaded_file(file1, "ファイル①")
df2 = read_uploaded_file(file2, "ファイル②")

# 比較ボタン
if df1 is not None and df2 is not None:
    common_cols = list(set(df1.columns) & set(df2.columns))
    if not common_cols:
        st.error("⚠️ 共通の列がないため比較できません！")
    else:
        key = st.selectbox("🔑 比較するキー列を選択してください", common_cols)

        if st.button("📌 比較する！"):
            merged = pd.merge(df1, df2, on=key, how='outer', suffixes=('_file1', '_file2'), indicator=True)
            merged['状態'] = merged['_merge'].map({
                'both': '一致 or 内容違い',
                'left_only': 'ファイル①にのみ存在',
                'right_only': 'ファイル②にのみ存在'
            })

            st.success("✅ 比較完了！結果は以下のとおり👇")
            st.dataframe(merged)

            csv = merged.to_csv(index=False, encoding='utf-8-sig')
            st.download_button("⬇️ 結果をCSVでダウンロード", data=csv, file_name="比較結果.csv", mime="text/csv")
