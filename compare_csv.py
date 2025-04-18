# compare_csv.py
import pandas as pd
import sys

# 引数チェック
if len(sys.argv) != 3:
    print("使い方：python compare_csv.py data1.csv data2.csv")
    sys.exit()

# ファイル読み込み
file1 = sys.argv[1]
file2 = sys.argv[2]

df1 = pd.read_csv(file1)
df2 = pd.read_csv(file2)

# 比較に使うキー（1列目と仮定）
key = df1.columns[0]

# データをマージ（突き合わせ）
merged = pd.merge(df1, df2, on=key, how='outer', suffixes=('_file1', '_file2'), indicator=True)

# 状態をわかりやすくする
merged['_状態'] = merged['_merge'].map({
    'both': '一致 or 内容比較必要',
    'left_only': '削除された',
    'right_only': '新規追加'
})

# 結果を保存
merged.to_csv('comparison_result.csv', index=False, encoding='utf-8-sig')

print("✅ 比較完了！結果を comparison_result.csv に出力しました。")
