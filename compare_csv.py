import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="クーポン照合アプリ", layout="wide")
st.title("🎟️ クーポン照合アプリ")

# --- アップローダー ---
st.subheader("1️⃣ ファイルをアップロードしてください（CSVまたはExcel）")

file1 = st.file_uploader("🗂️ ファイル①（最新 or 登録予定のデータ）", type=["csv", "xlsx"], key="file1")
file2 = st.file_uploader("🗂️ ファイル②（過去データ or 照合対象）", type=["csv", "xlsx"], key="file2")

# --- 読み込み関数 ---
def load_file(file, label):
    if not file:
        return None

    ext = file.name.split(".")[-1].lower()
    if ext == "csv":
        try:
            df = pd.read_csv(io.StringIO(file.getvalue().decode("utf-8")))
        except:
            df = pd.read_csv(io.StringIO(file.getvalue().decode("shift_jis")))
        st.success(f"✅ {label}：CSVファイルを読み込みました")
        return df

    elif ext == "xlsx":
        xls = pd.ExcelFile(file)
        sheet = st.selectbox(f"📄 {label}：シートを選んでください", xls.sheet_names, key=label)
        df = pd.read_excel(file, sheet_name=sheet)
        st.success(f"✅ {label}：Excelのシート「{sheet}」を読み込みました")
        return df

    else:
        st.error(f"❌ {label}：対応していないファイル形式です")
        return None

# --- 読み込み処理 ---
df1 = load_file(file1, "ファイル①")
df2 = load_file(file2, "ファイル②")

# --- 比較処理 ---
if df1 is not None and df2 is not None:
    st.subheader("2️⃣ 比較設定")

    key1 = st.selectbox("🔑 ファイル①のクーポンコード列を選んでください", df1.columns, key="key1")
    key2 = st.selectbox("🔑 ファイル②のクーポンコード列を選んでください", df2.columns, key="key2")

    common_cols = list(set(df1.columns) & set(df2.columns))
    compare_cols = st.multiselect("📝 照合したい項目を選択（例：名称、価格、公開期間）", common_cols)

    if st.button("🚀 照合を実行"):
        # マージ処理
        merged = pd.merge(
            df1,
            df2,
            left_on=key1,
            right_on=key2,
            how="outer",
            suffixes=('_新規', '_既存'),
            indicator=True
        )

        # 状態を表示（追加・削除・一致）
        merged["照合結果"] = merged["_merge"].map({
            "both": "一致 or 内容確認",
            "left_only": "新規追加",
            "right_only": "既存のみ（削除？）"
        })

        # 内容比較
        for col in compare_cols:
            col_新 = f"{col}_新規"
            col_旧 = f"{col}_既存"
            if col_新 in merged.columns and col_旧 in merged.columns:
                merged[f"{col}が一致？"] = merged[col_新] == merged[col_旧]

        # 結果表示
        st.success("✅ 照合完了！結果を表示します👇")
        st.dataframe(merged, use_container_width=True)

        # ダウンロードボタン
        csv = merged.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("⬇️ 結果をCSVでダウンロード", data=csv, file_name="クーポン照合結果.csv", mime="text/csv")
