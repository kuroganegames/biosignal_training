from pathlib import Path
import json,html,zipfile,re
B=Path('/media/kurogane/backup/bisignal_training/work_sim_2/output/pdf/saccade_detection_sources')
refs={r['key']:r for r in json.loads((B/'catalog.json').read_text())['references']}
rows=[
 dict(id='vt',name='VT / I-VT',family='速度閾値',refs=['Salvucci2000','Komogortsev2010','Bahill1981'],pages='Salvucci：PDF 3頁／Komogortsev：PDF 3頁',
 principle='隣接する視線点から速度を計算し、閾値を超えるサンプルをサッケード、低いサンプルを固視とする。連続する同じラベルをイベントにまとめる。',
 parameters='速度閾値。必要に応じて平滑化・速度推定法、最短持続時間、イベント結合条件を設定する。',auto='基本形では速度閾値を利用者が指定する。',
 example='Salvucciらは先行研究の例として20°/sを紹介するが、普遍的な推奨値ではない。Daiらの比較に使ったVTは自作実装。',
 strengths='処理が単純で高速。判定理由を説明しやすく、オンライン処理や基準となる実装を作りやすい。',
 limitations='速度を求める微分で雑音が増える。閾値を下げると偽陽性、上げると小さい・遅いサッケードの見逃しが増える。開始・終了時刻も閾値に依存する。'),
 dict(id='dt',name='DT / I-DT',family='分散度閾値',refs=['Salvucci2000','Blignaut2009','Komogortsev2010'],pages='Salvucci：PDF 4頁／Blignaut：PDF 5–14頁',
 principle='最小時間幅の窓を動かし、窓内の視線の広がりが閾値以下なら固視とみなして窓を拡張する。固視に属さない区間をサッケードとして区別する。代表的な分散度はD=(max x−min x)+(max y−min y)。',
 parameters='分散度の定義と閾値、最小固視持続時間。必要に応じて固視の結合・欠測処理条件。',auto='窓の長さは固視候補に応じて拡張されるが、初期の時間幅と空間閾値は指定する。',
 example='Salvucciらでは最小固視持続時間100–200 msの利用を説明。Blignautの実験では固視半径1°が有効だったが、半径とx/y範囲の和は別の分散指標であり、数値をそのまま転用できない。DaiらのDTは自作実装。',
 strengths='速度の微分を直接必要とせず、固視の位置・持続時間を得やすい。原理と実装が比較的単純。',
 limitations='雑音やドリフトで点群が広がると固視が分割される。設定した分散度と最小時間で結果が変わり、サッケード境界の精密な推定には弱い。'),
 dict(id='engbert',name='Engbert–Kliegl（2003）',family='適応速度閾値',refs=['Engbert2003'],pages='PDF 2頁・第2節',
 principle='水平・垂直の速度分布を中央値に基づく頑健な尺度で評価し、雑音に比例する楕円形の閾値領域の外側を候補とする。原著では両眼で時間的に重なる候補を採用する。',
 parameters='閾値倍率λ、最短持続時間、速度推定の窓、両眼の時間的重なり条件。',auto='水平・垂直それぞれの速度のばらつきと、そこから決まる絶対速度閾値を試行ごとに推定する。',
 example='原著：λ=6、最短3サンプル。原著の250 Hz記録では3サンプル=12 ms。速度は5点を使って推定。サンプリング周波数を変えた際に3サンプルと12 msを同一視しない。',
 strengths='固定の速度値より記録間の雑音差に適応しやすい。マイクロサッケードの検出が目的で、両眼一致によって単眼の雑音を除きやすい。',
 limitations='高雑音で閾値が上がると小振幅・低速の運動を見逃しやすい。λと持続時間の選び方に依存する。原著の両眼条件を使うには両眼記録が必要。'),
 dict(id='nh',name='Nyström–Holmqvist（2010）／NH・ONH',family='適応速度閾値',refs=['Nystrom2010','Friedman2018'],pages='Nyström：PDF 5–8頁、表2（PDF 7頁）',
 principle='平滑化後の速度から、固視雑音に基づくピーク閾値を反復推定する。サッケードの前後を探索し、局所雑音も使って境界を定め、サッケード後のグリセードを別イベントに分類する。',
 parameters='Savitzky–Golay（SG）フィルタの次数・窓長、反復の初期閾値と収束条件、雑音倍率、局所閾値の重み、最短持続時間、異常速度・加速度の上限。',auto='ピーク閾値μ+6σ、開始閾値μ+3σ、局所雑音を含む終了閾値をデータから計算する。',
 example='原著の表2：SG 2次、窓長=最小サッケード持続時間の2倍、最小サッケード10 ms・固視40 ms、終了閾値の重み0.7/0.3。上限速度1,000°/s・加速度100,000°/s²。μとσは閾値推定に用いる雑音の平均と標準偏差。',
 strengths='雑音に応じた閾値を使い、サッケードの検出だけでなく境界探索とグリセードの分離まで扱う。教師データは不要。',
 limitations='平滑化と雑音推定の影響が大きい。非常にきれいなデータでは閾値が低くなり過検出、高雑音では見逃しが起こりうる。フィルタ遅延を含む実装差にも注意が必要。'),
 dict(id='mnh',name='Friedmanら（2018）／MNH',family='NHの修正',refs=['Friedman2018'],pages='PDF 4–11頁、表3（PDF 10頁）',
 principle='NHの平滑化を弱め、ピーク・副閾値を固定する。速度の局所最小と位置波形を考慮して境界を補正し、RIONEPSという不規則な振動雑音の除外とPSO判定を追加・変更する。',
 parameters='ピーク・副閾値、SG窓長、最小サッケード・固視持続時間、雑音除外条件、PSO判定条件。',auto='固視雑音の速度分布の90パーセンタイルを、アーティファクト区間の拡張とPSO終了判定に利用する。主要なサッケード速度閾値は固定。',
 example='原著（主に1,000 Hzの読書データ）：ピーク55°/s、副閾値45°/s、SG窓7 ms・2次、最小サッケード10 ms・固視30 ms。ノイズ除外上限1,500°/s・100,000°/s²。',
 strengths='原著の読書データでは、ONHに対して開始・終了点の誤りが減少した。PSOと振動性雑音を明示的に扱う。',
 limitations='非常に小さいサッケードを検出できないことを著者らが報告。固定閾値や読書データ向けの規則は別条件で再検証が必要で、低速の運動にも不利になりうる。'),
 dict(id='clusterfix',name='König–Buffalo（2014）／Cluster Fix',family='教師なしクラスタリング',refs=['Konig2014'],pages='PDF 2–3頁・第2.2節、表1',
 principle='距離・速度・加速度・軌跡方向の角度変化（原著のangular velocity）の4特徴を正規化し、k-meansで全体を分類する。続いて各固視周辺を局所的に再クラスタリングし、小さいサッケードも探す。',
 parameters='前処理フィルタ、クラスタ数の候補範囲・反復、局所解析の範囲、最短固視・サッケード持続時間など。',auto='クラスタ数はシルエット幅に基づいて選ぶ。固定の速度・加速度によるサッケード判定閾値を指定する必要はない。',
 example='原著：200→1,000 Hzに補間、30 Hz低域通過。全体k=2–5、局所k=1–5、固視の前後50 msを再解析。最短サッケード10 ms・固視25 ms（加えて5 ms未満の固視を処理）。',
 strengths='教師ラベルが不要。振幅の異なる運動を全体と局所の両方で解析し、小さいサッケードと雑音のある固視の区別、境界の精度向上を狙える。',
 limitations='反復クラスタリングによる計算負荷が大きく、微小サッケードの検出は周辺の雑音に左右される。「閾値不要」は速度等の判定閾値についてであり、時間条件・前処理・探索設定は残る。'),
 dict(id='irf',name='Zemblysら（2018）／IRF・I-RF',family='教師ありランダムフォレスト',refs=['Zemblys2018','Zemblys2019Correction'],pages='2018：PDF 5–8頁／2019訂正：PDF 1–2頁',
 principle='速度・分散度・位置の変化・雑音指標などから各サンプルの特徴量を作り、ランダムフォレストで固視・サッケード・PSOの確率を推定する。時間方向の平滑化と規則による後処理でイベントを確定する。',
 parameters='学習済みモデルと、その特徴抽出法・窓長・後処理規則。新規学習時は教師ラベル、特徴選択、木の数、分岐条件、クラス重みなど。',auto='分類境界は学習で獲得する。学習済みモデルを使う際、利用者が記録ごとの速度閾値を設定する必要は基本的にない。',
 example='原著の初期の完全モデルは14特徴・200本の木、Gini基準。その後、特徴と木の数を削減しており、200本を全実装の既定値とは扱わない。原著の後処理にはサッケード6–150 ms、固視50 ms以上、サッケード間隔25 msなどがある。訂正版のコード・モデルと一組で確認する。',
 strengths='複数の特徴から非線形な判定ができ、雑音やサンプリング周波数の変化を学習に含められる。固視・サッケード・PSOをまとめて分類できる。',
 limitations='教師ラベルの品質と、学習条件からのずれに影響される。特徴抽出・学習・モデル管理の負担がある。2019年訂正で後処理の説明とコードが修正されている。'),
 dict(id='hmm',name='HMM / I-HMM',family='確率的時系列モデル',refs=['Salvucci2000','Komogortsev2010'],pages='Salvucci：PDF 3–4頁／Komogortsev：PDF 3頁',
 principle='固視とサッケードを2つの隠れ状態とし、各状態の速度分布と状態の遷移確率を使って系列を推定する。比較実装ではVTによる初期分類、Viterbi推定、Baum–Welch再推定を使う。',
 parameters='初期状態確率、遷移確率、各状態の観測速度分布（平均・分散など）。比較実装では初期速度閾値、再推定回数も必要。',auto='確率パラメータはデータから再推定できる。Komogortsevらの実装では再推定を4回行った。',
 example='Salvucciらは2状態それぞれの観測分布・遷移確率を説明。Komogortsevらでは速度閾値による初期割当ても使うため、単純に「閾値なし」とは言えない。',
 strengths='隣接する時刻のつながりを使い、サンプル単位の速度閾値より確率的な判断ができる。パラメータの再推定が可能。',
 limitations='初期化・分布の仮定・2状態という設計に依存する。固視と低速サッケードの速度分布が重なると識別しにくい。PSOや追従を独立に扱うには状態設計の拡張が必要。'),
 dict(id='mst',name='MST / I-MST',family='空間グラフ',refs=['Salvucci2000','Komogortsev2010'],pages='Salvucci：PDF 4–5頁／Komogortsev：PDF 3–4頁',
 principle='視線点を頂点として、辺長の合計が最小となる木（最小全域木）を構築する。長い辺をサッケードに対応付け、短い辺でつながる点の集まりを固視とする。',
 parameters='辺長の閾値と解析窓。Salvucciらの局所適応形では最小分岐深さ、局所的な辺長の平均・標準偏差や比率の基準も用いる。',auto='局所適応形では周囲の辺長の統計を判定に利用する。比較実装の距離閾値と窓長は指定する。',
 example='Komogortsevらの実装は非重複の200 ms窓内で木を構築し、点間距離の閾値で分類した。原典の局所適応形と設定項目は同一ではない。',
 strengths='速度微分に直接依存しない。空間的なまとまりを使うため、信号の一部が欠けても固視を識別しうる。',
 limitations='木の構築の計算量が必要。窓長・空間閾値に依存し、空間的な近さだけでは時間順序や再訪固視、正確なサッケード境界を扱いにくい。'),
 dict(id='kf',name='KF / I-KF（Sauter系）',family='予測残差の検定',refs=['Sauter1991','Komogortsev2010'],pages='Sauter：PDF 2–6頁／Komogortsev：PDF 3頁',
 principle='カルマンフィルタによる予測と観測の差が、通常の運動・雑音では説明しにくいほど大きいかをχ²検定する。Sauter原典は追従速度のARモデルとイノベーションを使い、Hinkley検定で境界を求める。',
 parameters='モデルの次数・係数と初期条件、状態・測定雑音の分散、検定窓長N、χ²の判定閾値または有意水準。原典の境界推定にはHinkleyの設定。',auto='予測状態と誤差共分散を逐次更新する。原典では滑らかな追従成分からモデルを同定する。',
 example='Daiらが参照するKomogortsev実装は「位置・速度」の2状態モデルで、予測速度と観測速度の差の二乗を窓内で集計する。Sauter原典のARモデル＋Hinkley処理をそのまま使うものとは区別する。',
 strengths='単純な速度の大小に加えて、予測できない変化を検出できる。再帰的な計算が可能で、Sauter原典は滑動性追従とサッケードの分離を扱う。',
 limitations='モデルと雑音分散の設定に敏感。装置や運動の性質が変わると残差の解釈も変わる。急な雑音とサッケードを分ける設定や、境界決定の追加処理が必要。'),
 dict(id='dai',name='参考：Daiら（2021）の提案法',family='区分多項式近似＋速度閾値',refs=['Dai2021'],pages='PDF 4–9頁・式5、16–19／適用範囲：PDF 15頁',
 principle='眼位を暗黙の区分2次多項式として表し、1階差分と3階差分へのスパース正則化による最適化で雑音を除去する。その速度に開始・終了で異なる閾値を適用する。',
 parameters='正則化係数α・β（雑音σ、平均振幅A、平均持続時間D、サンプリング周波数fから自動算出）、開始・終了速度閾値、持続時間・瞬目近傍・イベント間隔などの後処理条件。',auto='α・βはデータの概略統計とサンプリング周波数を使う経験式で設定する。手動調整を要しない設計でも、固定の検出規則は残る。',
 example='原著：開始30°/s、終了10°/s、最短12 ms、最小サッケード間隔40 ms、瞬目から10サンプル未満を除外、ピーク800°/s超を除外。500 Hzではα=8σ、β=4√A exp(5D)σ（Aは度、Dは秒）。他のfには式18–19を使う。',
 strengths='原著の比較では高雑音や病的な低速サッケードに良好な成績を示した。雑音除去と検出を組み合わせ、波形の急な変化を残すことを狙う。',
 limitations='最適化の計算が必要で、α・βや後処理の仮定の影響は残る。原著は眼振・滑動性追従を対象外としている。開始閾値30°/s未満の動きは、その設定のままでは検出できない。')
]
meta={'created':'2026-11-18','scope':'Dai et al. (2021)の比較10手法＋提案法の参考行','basis':'収集済み英語原論文の本文・表を確認。長所・短所は原著の記載と検出原理からの整理を含み、普遍的な性能順位ではない。','parameter_note':'数値は各原著の設定例であり、Daiの比較に用いた各コードの設定値をすべて同定したものではない。','rows':rows}
(B/'saccade_methods_comparison_ja.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
e=html.escape

def ref_links(keys):
 out=[]
 for k in keys:
  r=refs[k];label=r['authors'].split(',')[0]+' '+str(r['year'])
  url='https://doi.org/'+r['doi'] if r.get('doi') else r['source']
  out.append(f'<a href="{e(url)}">{e(label)}</a>')
 return ' · '.join(out)

body=[]
for r in rows:
 cls='reference' if r['id']=='dai' else ''
 body.append(f'<tr id="{r["id"]}" class="{cls}" data-search="{e(" ".join(str(r[k]) for k in ["name","family","principle","parameters","strengths","limitations"]))}"><th scope="row"><strong>{e(r["name"])}</strong><span class="badge">{e(r["family"])}</span><div class="refs">{ref_links(r["refs"])}</div></th><td>{e(r["principle"])}</td><td>{e(r["parameters"])}<div class="auto"><b>自動化される部分：</b>{e(r["auto"])}</div></td><td>{e(r["strengths"])}</td><td>{e(r["limitations"])}</td></tr>')
details=[]
for r in rows:
 links=[]
 for key in r['refs']:
  v=refs[key]
  links.append(f'<a href="{e(v["local_pdf"])}">{e(v["authors"].split(",")[0])} {v["year"]} 原文</a> / <a href="{e(v["japanese_pdf"])}">日本語版</a>')
 details.append(f'<article><h3>{e(r["name"])}</h3><p>{e(r["example"])}</p><p class="small">確認箇所：{e(r["pages"])}</p><p class="small">'+ ' · '.join(links)+'</p></article>')
notes=[
'各手法に共通して、視線座標と時刻またはサンプリング周波数、欠測・瞬目の扱いを明示する。°や°/sの閾値を用いる場合は、視角単位への換算が必要。',
'「適応的」「ノンパラメトリック」「利用者による調整不要」は、設定が一切存在しないという意味ではない。前処理、持続時間、学習時の設定なども含めて比較する。',
'DaiらはVT・DTを自作し、それ以外は著者らの公開実装を利用したと記載している。HMM・MST・KFはKomogortsevらの実装を参照する。原典の説明と特定コードの挙動は同一とは限らない。',
'Daiらは比較に共通の後処理（最短12 ms、間隔40 ms、瞬目近傍・過大ピークの除外など）を加えている。したがって、元の検出器だけの特性とDai論文の評価結果を混同しない。',
'Zemblys法は2019年訂正を含めて読む。規則違反イベントは、まず該当クラスの確率を0にして次に確からしいクラスへ再分類する。訂正版では最終的な決定論的な後処理も加えられた。後処理の説明・コード・モデルの版を記録する。',
'Nyströmの「グリセード」と、Friedman・Zemblysの「PSO（サッケード後振動）」は、論文・実装ごとの分類定義を確認する。固視・サッケードの2値だけを出す方法との比較では、ラベル対応も指定する。',
'収集12本は12種類の独立した検出法を意味しない。Salvucciは複数手法の共通文献、BahillはVTの背景文献、BlignautはDTの閾値・分散指標の検討、2019年論文はIRFの訂正である。'
]
css='''*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,"Noto Sans CJK JP",sans-serif;color:#233646;background:#f4f7f8;font-size:14px;line-height:1.65}main{max-width:1900px;margin:auto;padding:36px 28px 70px}h1{font-size:30px;line-height:1.35;color:#133e53;margin:8px 0 15px}h2{font-size:22px;margin-top:36px;color:#173e50}h3{font-size:17px;color:#173e50;margin:0 0 9px}a{color:#00687c;text-underline-offset:3px}.lead{max-width:1050px}.small,.refs{font-size:12px;color:#526674}.notice{padding:16px 20px;background:#e6f1f2;border-left:4px solid #218084;max-width:1200px}.toolbar{display:flex;gap:14px;align-items:center;flex-wrap:wrap;margin:22px 0 12px}input{width:340px;max-width:100%;font:inherit;padding:10px 13px;border:1px solid #a8bec7;border-radius:5px}button{font:inherit;padding:10px 16px;background:#16485d;color:white;border:0;border-radius:5px;cursor:pointer}.tablewrap{overflow:auto;border:1px solid #ccd9df;background:white}table{border-collapse:separate;border-spacing:0;width:100%;min-width:1250px;table-layout:fixed}thead th{position:sticky;top:0;background:#19495c;color:white;font-weight:650;text-align:left;padding:15px;z-index:2}thead th:first-child{width:16%}thead th:nth-child(2){width:23%}thead th:nth-child(3){width:24%}thead th:nth-child(4){width:17%}thead th:nth-child(5){width:20%}tbody th,td{vertical-align:top;text-align:left;border-bottom:1px solid #d7e1e5;padding:18px 15px;font-weight:400}tbody tr:nth-child(even){background:#f5f9fa}tbody tr.reference{background:#e9f2ec}tbody th{border-right:1px solid #e0e8eb}strong{font-weight:700}.badge{display:block;font-size:12px;color:#176568;margin:10px 0 8px}.auto{font-size:12px;margin-top:12px;padding-top:10px;border-top:1px solid #d9e4e8;color:#48616f}.details{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.details article{padding:22px;background:white;border:1px solid #d7e1e5;border-radius:7px}li{margin:9px 0}footer{margin-top:28px;font-size:12px;color:#5b6d78}[hidden]{display:none!important}@media(max-width:800px){main{padding:24px 16px}.details{grid-template-columns:1fr}h1{font-size:25px}}@media print{@page{size:A3 landscape;margin:12mm}body{background:white;font-size:9pt}main{padding:0;max-width:none}h1{font-size:20pt}.toolbar,.nav{display:none}.tablewrap{overflow:visible;border:none}table{min-width:0;font-size:8pt}thead{display:table-header-group}thead th{position:static}th,td{padding:8px!important}tr,article{break-inside:avoid}.auto,.small,.refs,.badge{font-size:7.5pt}.details{display:block}.details article{margin:12px 0}.notice{font-size:9pt}a{color:inherit;text-decoration:none}}'''
html_doc='''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>サッケード検出法の日本語比較表</title><style>'''+css+'''</style></head><body><main><p class="nav"><a href="index.html">← 論文一覧・日本語PDFへ</a></p><h1>サッケード検出法の日本語比較表</h1><p class="lead">Daiら（2021）の比較対象10手法を整理し、提案法を参考として加えた。原理、必要な設定、自動で推定される部分、長所・短所を英語原典に基づいてまとめている。</p><div class="notice"><b>数値は各原著の設定例。</b>装置、サンプリング周波数、対象の眼球運動、雑音に合わせた検証が必要であり、普遍的な推奨値ではない。長所・短所には、論文の報告と検出原理からの整理を含む。全条件に共通する性能順位を示すものではない。</div><div class="toolbar"><label>手法・用語で検索　<input id="filter" type="search" placeholder="例：低速、PSO、クラスタ"></label><span id="count">11手法</span><button onclick="window.print()">印刷</button><a href="#parameters">原著の設定例</a><a href="#notes">比較時の注意点</a></div><div class="tablewrap"><table><thead><tr><th>手法・原典</th><th>検出の原理</th><th>必要な設定・自動化</th><th>長所</th><th>短所・注意点</th></tr></thead><tbody>'''+''.join(body)+'''</tbody></table></div><h2 id="parameters">原著の設定例と確認箇所</h2><p>ページ番号は、このフォルダに収録した原文PDF内のページを指す。Dai論文の各比較実装に、そのまま同じ値が使われたという意味ではない。</p><div class="details">'''+''.join(details)+'''</div><h2 id="notes">比較時に条件をそろえるポイント</h2><ol>'''+''.join('<li>'+e(n)+'</li>' for n in notes)+'''</ol><p>評価元：<a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC8212426/">Dai et al. (2021)</a>、<a href="00_Dai_et_al_2021_target.pdf#page=9">原文PDF・比較方法の記載（9頁）</a>。</p><footer>作成：2026年11月18日（Asia/Tokyo）。対象は収集済み論文に含まれる方式であり、最新の全検出法を網羅する表ではない。原文PDFと日本語訳の内容は変更していない。</footer></main><script>const input=document.getElementById('filter');const rows=[...document.querySelectorAll('tbody tr')];input.addEventListener('input',()=>{const q=input.value.trim().toLocaleLowerCase();let n=0;rows.forEach(r=>{r.hidden=!r.dataset.search.toLocaleLowerCase().includes(q);if(!r.hidden)n++;});document.getElementById('count').textContent=n+' / 11手法';});</script></body></html>'''
(B/'saccade_methods_comparison_ja.html').write_text(html_doc)
index=B/'index.html';s=index.read_text();block='<div class="banner" id="method-comparison" style="margin:20px 0"><p><strong>検出法の日本語比較表</strong>：原理、必要なパラメータ、長所・短所、原著の設定例をまとめました。</p><p><a href="saccade_methods_comparison_ja.html">10比較手法＋Dai提案法の比較表を開く</a></p></div>'
if 'id="method-comparison"' not in s:
 marker='<h2>比較10手法と文献の対応</h2>';assert marker in s;s=s.replace(marker,block+marker);index.write_text(s)
archive=B.parent/'saccade_detection_sources_with_japanese.zip';tmp=archive.with_suffix('.new.zip');changed={B.name+'/index.html':re.sub(r' · <a href="../saccade_detection_sources_with_japanese.zip">.*?</a>','',index.read_text()).encode(),B.name+'/saccade_methods_comparison_ja.html':html_doc.encode(),B.name+'/saccade_methods_comparison_ja.json':(B/'saccade_methods_comparison_ja.json').read_bytes()}
with zipfile.ZipFile(archive) as old,zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as new:
 for item in old.infolist():
  if item.filename not in changed:new.writestr(item,old.read(item.filename))
 for name,data in changed.items():new.writestr(name,data)
tmp.replace(archive)
print('Created Japanese comparison for',len(rows),'methods and updated index + ZIP')
