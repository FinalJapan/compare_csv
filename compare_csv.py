import streamlit as st
import pandas as pd
import io

st.title("📊 Excel & CSV 両対応！ファイル比較アプリ")

# ファイルを複数受け取る（csv/xlsx対応）
files = st.file_uploader(
    "2つのファイル（CSVまたはExcel）をアップロードしてください",
    type=["csv", "xlsx"],
    accept_multiple_files=True
)

# ファイルが2つアップロードされたら処理開始
if files and len(files) == 2:
    dfs = []

    for i, file in enumerate(files):
        filename = file.name
        ext = filename.split(".")[-1].lower()

        st.subheader(f"📁 ファイル{i+1}: {filename}")

        if ext == "csv":
            # CSVの場合
            try:
                df = pd.read_csv(io.StringIO(file.getvalue().decode("utf-8")))
            except UnicodeDecodeError:
                df = pd.read_csv(io.StringIO(file.getvalue().decode("shift_jis")))
            dfs.append(df)
            st.success("✅ CSVとして読み込み完了！")
        elif ext == "xlsx":
            # Excelの場合：シートを選ばせる
            xls = pd.ExcelFile(file)
            sheet = st.selectbox(f"シート選択（ファイル{i+1}）", xls.sheet_names, key=f"sheet_{i}")
            df = pd.read_excel(file, sheet_name=sheet)
            dfs.append(df)
            st.success(f"✅ Excelとして『{sheet}』を読み込み完了！")
        else:
            st.error("対応していないファイル形式です。CSVまたはExcel（.xlsx）をアップロードしてください。")
            st.stop()

    # 2つのDataFrameが読み込めたら比較へ
    if len(dfs) == 2:
        df1, df2 = dfs

        # 共通カラム抽出
        common_cols = list(set(df1.columns) & set(df2.columns))
        if not common_cols:
            st.error("⚠️ 共通のカラムが見つかりません！")
        else:
            key = st.selectbox("🔑 比較するキー列を選択してください", common_cols)

            # 比較実行
            merged = pd.merge(df1, df2, on=key, how='outer', suffixes=('_file1', '_file2'), indicator=True)
            merged['状態'] = merged['_merge'].map({
                'both': '一致 or 内容違い',
                'left_only': 'ファイル1にだけ存在',
                'right_only': 'ファイル2にだけ存在'
            })

            st.success("✅ 比較完了！結果を表示します👇")
            st.dataframe(merged)

            # CSVダウンロード
            csv = merged.to_csv(index=False, encoding='utf-8-sig')
            st.download_button("⬇️ 結果をCSVでダウンロード", data=csv, file_name="比較結果.csv", mime="text/csv")

else:
    st.info("👆 ファイルを2つアップロードしてください（CSV or Excel）")
