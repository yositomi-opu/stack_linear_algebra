# 実学系・日本語MCQサンプル

大学の授業やWorkshopで改変して使うための、真偽一対型（`require_pairs=true`）CSVサンプルです。1ファイルが1問に対応し、各命題について正しい文 `C`、誤った文 `W`、両者に共通する解説フィードバックを収録しています。WebAppの「CSV/XLSX読込」から1ファイルずつ読み込み、選択肢数、正解数、文言などを編集できます。

## 収録カテゴリ

| 識別子 | 分野 | ファイル | 問題数 | 1問の真偽ペア数 |
|---|---|---:|---:|---:|
| `NUR` | 看護学（感染対策） | `NUR01.csv`–`NUR10.csv` | 10 | 5 |
| `CIV` | 法学（日本の民法） | `CIV01.csv`–`CIV10.csv` | 10 | 4 |
| `ECO` | 経済学基礎 | `ECO01.csv`–`ECO10.csv` | 10 | 4 |
| `STA` | 統計リテラシー | `STA01.csv`–`STA10.csv` | 10 | 4 |
| `ETH` | 研究倫理 | `ETH01.csv`–`ETH10.csv` | 10 | 4 |
| `ICT` | 情報・AIリテラシー | `ICT01.csv`–`ICT10.csv` | 10 | 4 |

`STA`、`ETH`、`ICT`は、専門を問わず大学教員が導入教育やFDで使いやすく、誤答後のフィードバックに学習上の意味を持たせやすい追加分野として選びました。

## 利用上の注意

- これは完成済みの標準試験問題ではなく、WebAppで編集するための教材原案です。授業の到達目標、用語、所属機関の規程に合わせて担当教員が確認してください。
- `CIV`は2026年9月10日時点の日本の民法を前提とした入門例です。法的助言には使わず、利用時点の条文、判例、特別法を確認してください。
- `NUR`は感染対策の基礎例です。臨床判断や個別患者への指示には使わず、所属施設の最新手順を優先してください。
- `ETH`と`ICT`は、法令、学会、投稿先、所属機関、利用サービスごとに規程が異なる事項を含みます。各組織の現行ルールへ合わせてください。
- 誤文 `W` は誤概念を明確にするため断定的にしています。授業ではフィードバックまで必ず表示させることを推奨します。

## 主な確認資料

- [e-Gov法令検索「民法」](https://laws.e-gov.go.jp/document?lawid=129AC0000000089)
- [厚生労働省「標準予防策と経路別予防策」](https://www.mhlw.go.jp/content/001301258.pdf)
- [日本銀行「金融政策は景気や物価にどのように影響を及ぼすのですか？」](https://www.boj.or.jp/about/education/oshiete/seisaku/b28.htm)
- [総務省統計局「統計用語辞典」](https://www.stat.go.jp/naruhodo/13_yougo/ta-gyo.html)
- [文部科学省「研究活動における不正行為への対応等」](https://www.mext.go.jp/a_menu/jinzai/fusei/index.htm)
- [IPA「情報セキュリティ10大脅威」](https://www.ipa.go.jp/security/10threats/index.html)

## 再生成

看護学10問は既存の `SampleNurse001.csv`–`SampleNurse010.csv`を読み込み、それ以外は生成スクリプト内の定義から作ります。

```sh
python3 app/mcq-webapp/samples/applied-ja/generate_samples.py
```

生成後は、次の検査スクリプトでファイル数、識別子、真偽ペア、フィードバック、CSVの再読込みを確認できます。

```sh
python3 app/mcq-webapp/samples/applied-ja/validate_samples.py
```
