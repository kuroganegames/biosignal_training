# -*- coding: utf-8 -*-
# Generated from the companion educational notebook.
# 0-A. 環境確認
import base64, gzip, hashlib, io, json, platform
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import sklearn
from IPython.display import display, Markdown
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge

OUT = Path('outputs')
OUT.mkdir(exist_ok=True)
SEED = 20261108
HISTORY = 3
ALPHA = 10.0
plt.rcParams.update({'figure.dpi': 110, 'font.size': 10,
                     'axes.spines.top': False, 'axes.spines.right': False})
VERSIONS = {'python': platform.python_version(), 'numpy': np.__version__,
            'pandas': pd.__version__, 'matplotlib': matplotlib.__version__,
            'scikit-learn': sklearn.__version__}
print(VERSIONS)

# @title 1-A. 同梱された公開データを展開（変更不要）
# CSVの圧縮スナップショット。pickle等の実行可能形式は使用しません。
SNAPSHOTS = {"vfpwgRetest24d2.csv":{"sha256":"2d387f3045b74dadd884c12f18c1a09ed7fe5b51168d85ebd34c61b6f14ae439","gzip_base64":"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"},"p24d2_coordinates.csv":{"sha256":"b75ecc679f2aa140aa5a4345314f311ca714db8ffe97055e21433695337756bf","gzip_base64":"H4sIAAAAAAACA1WSS47CMBBE95ylLMWfxPEFOAF7NCNYRIoATRgJbj/u9pAuS2xeq+mqlOtxX25PvPDGsp2/1+V2OW+P+/OweriC4HH8WrfrYQ1wkTCCKYFXRzg/ov7+eZJLhlkuGc5gKuBVP6C75KupqlN2DiplHEXKMImU4QimCbya0R2a0emUqpvrvz9hDOrD2KsP4yA+DKP4MExgElmjCXro9PMrlNHJzGrD2aCoDxvEQY3QQJ+RWN+RWJwQyksSavjuYydO6NVyk99zinOTt0FR+Z3ToPLG8nWEAd22NoM4oZNLrWnOCpK0azzQuHggfWOWEhCPWjketASp3i1CGmiGxBrizn93hodlYgMAAA=="},"LICENSE.visualFields.txt":{"sha256":"c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4","gzip_base64":"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"},"provenance.json":{"sha256":"44c070d1a3b6128b805544adc32201e5097cd70c9cf52e5511d3ac1a3dbb2322","gzip_base64":"H4sIAAAAAAACA8VWTW/cNhC9+1cMFgXaAlmtRH3Hp8BxAQNBHayDXooioMjhig0lCiS1thvkv3cobWyn9SGHJgUMw8sZzrz3OG/WH88ANhMXH/gBNy9hc9R+5uYXjUb6zYsYPKLz2o4xmCVpUq+nwvHxvbDDoEOMyAILUaRNVZaS5ZWkX0oVqi6aoi2F4qIuOlHXfL3M59Bb9+S6SEvBZC1zjlWd5wyxVW0hKta2vGiZwJynbdZm63WjBY5+gfuKoPcIb9YTYEm6png7O4GeUj7Sx8hCTbeHPQb0gRWSJU7yhyCFZ2diuT6Eyb/c7Ry/TQ469HM3e3TCjgHHkBDeXeS9eyrS7mup7yQPfPccjhefUfies7KKQBoVb6XEv+xYlnepKIqmS1UrsK5KUWGDbdbwKlVlLlqOqcxElqeyyVtRyQY3S8lPa+WNsWLgk//fSD/t/wxZlslcsbQRkqcyTxlnVZFWtcoqyao8DkbesLLmArM4BlWbNk3Zlky2bds0HfuS7OvLm4v91dt3V9e/Jk8xJ+EufG/2T7A8Rzxl9GQFT+usYhmvkddNWaZKSpU2Hb1kW1dFVfC8EGVTpiyjnKwpOt4VWV5kmH1J/M3VxeWvN5f/DWk9cKdH5Whgs93X2nN3gvAcV1FnJFMrVZvVrFKizGhSsauZzLMGRVU2LK1YzXLWMVW3JEiLTS2FykuZEuMT17MT3w2BfbKZ9hB4ZxDwbrIuoATu4eLmt3PYw2seECS/9+D1KBCytk63aUY/sNaI6cHC1c01pVGuD8T84M9htDAg97OjhCM3M3oQPR8PKBO4sNZJPcb8f3RWzg5wmvgfpsXkcHknzCwpOFk9Bg+GVTuTl6Al6a2Vpkh3D4E22bq4gC7/6KGjhnaY7EhZ8NMesm3HPcqfk9MOfsDwfmFCpVY13lGh004nNtYRcALEY9iDHoHHsoMdwelDH7Z4j/BYiwjwARO4piAdGKCVZWzwyR4G7Zx1Hu62/E57kNpPht+Dsg6ub+CWBsnOARxSKYwagqetrIM+6nBPHcw8jD6Bt4QH3ZGE67WHR+Qg5+XSYCUaQ3+dnxqCHc2qzqkjyXX3BeIVgFbge3sba3ARyANgUK30VHQDWKep1aLDvyXEY3wNEb9Wfl8N9U1Xw373oOvJLt++n7GcHub7dVxdQO2o2x+r3vyIPPhHjV8ZQ6PqghZ64tEaPWXAwfCZuvPFgz1yE3oaIMO9pzeEydkDzVD0PhjeofHJZ0Jx8n2Y5T0tAD8PcfB1CGRPQQOlBTc0SOTpkWZEzSaOiwvbgG44Ofuh0Nu5M9r3NGlxJ0TXLA4m65Ss2NI6AU94l8nzc/cnigA1SPSTDjFpxUCfhdPTMtxWQcbgFvEDQfAr+kfciwwPLdXkPi8c7hD+QmfPIegBd2SRZXyXc7KCwN4aetOt0R+iiUcfooqPdUkslFosdwJ3BwxApoteGvEuelVEs9ICpH9IXpDaAQ4zpzcPSIe0eBbEpDJplCzPePbp7G9/PeC3NAoAAA=="}}
DATA = Path('data')
DATA.mkdir(exist_ok=True)
SNAPSHOT_BYTES = {}
for name, item in SNAPSHOTS.items():
    raw = gzip.decompress(base64.b64decode(item['gzip_base64']))
    assert hashlib.sha256(raw).hexdigest() == item['sha256'], name
    SNAPSHOT_BYTES[name] = raw
    target = DATA / name
    if not target.exists():
        target.write_bytes(raw)
    elif target.read_bytes() != raw:
        print(f'{name}: ローカルファイルは変更済み。保持し、解析には同梱版を使います。')
df = pd.read_csv(io.BytesIO(SNAPSHOT_BYTES['vfpwgRetest24d2.csv']), parse_dates=['date'])
coords = pd.read_csv(io.BytesIO(SNAPSHOT_BYTES['p24d2_coordinates.csv']))
provenance = json.loads(SNAPSHOT_BYTES['provenance.json'])
print('data:', df.shape, 'coordinates:', coords.shape)

# 1-B. 構造の監査：この段階で結果に応じた除外・補完はしない
locs54 = [f'l{i}' for i in range(1, 55)]
blind = coords.loc[coords['is_blind_spot'], 'point'].tolist()
locs = [c for c in locs54 if c not in blind]
coords52 = coords.set_index('point').loc[locs]
df = df.sort_values(['id', 'eye', 'date']).reset_index(drop=True)
df['visit'] = df.groupby(['id', 'eye']).cumcount() + 1
df['gap_days'] = df.groupby(['id', 'eye'])['date'].diff().dt.days

qc = {
    'participants': int(df['id'].nunique()),
    'eyes': int(df[['id','eye']].drop_duplicates().shape[0]),
    'exams': len(df),
    'missing_sensitivities': int(df[locs54].isna().sum().sum()),
    'duplicate_id_eye_date': int(df.duplicated(['id','eye','date']).sum()),
    'min_sensitivity_db': float(df[locs54].min().min()),
    'max_sensitivity_db': float(df[locs54].max().max()),
    'blind_spot_columns': blind,
    'constant_metadata': [c for c in ['time','duration','fpr','fnr','fl','type']
                          if df[c].nunique(dropna=False) == 1],
    'max_gap_days': float(df['gap_days'].max())
}
print(json.dumps(qc, ensure_ascii=False, indent=2))
display(df.groupby(['id','eye']).size().rename('exams').reset_index().head())
display(df[['fpr','fnr','fl']].agg(['min','max','nunique']))
display(df.loc[df['gap_days'] > 35, ['id','eye','date','gap_days']])
assert df['id'].nunique() == 30
assert df.groupby(['id','eye']).size().eq(12).all()
assert df.groupby('id')['eye'].nunique().eq(1).all()
assert len(locs) == 52 and blind == ['l26','l35']
assert not df.duplicated(['id','eye','date']).any()
assert np.isfinite(df[locs].to_numpy(dtype=float)).all()
assert (df[locs].to_numpy() >= 0).all()
(OUT / 'qc.json').write_text(json.dumps(qc, ensure_ascii=False, indent=2), encoding='utf-8')

# 2-A. 21人/9人を固定して保存
splitter = GroupShuffleSplit(n_splits=1, test_size=9, random_state=SEED)
train_rows, test_rows = next(splitter.split(df, groups=df['id']))
train_ids = np.sort(df.iloc[train_rows]['id'].unique())
test_ids = np.sort(df.iloc[test_rows]['id'].unique())
assert set(train_ids).isdisjoint(set(test_ids))
assert (len(train_ids),len(test_ids)) == (21,9)
train_df = df[df['id'].isin(train_ids)].copy()
print('train IDs:', train_ids.tolist())
print('test IDs :', test_ids.tolist())
split_record = {'seed': SEED, 'train_ids': train_ids.tolist(), 'test_ids': test_ids.tolist()}
(OUT / 'patient_split.json').write_text(json.dumps(split_record,indent=2),encoding='utf-8')

# 2-B. 位置地図。左右を右眼基準にそろえていることを明記する
def map_values(ax, values, title, vmin=0, vmax=40, cmap='viridis'):
    sc = ax.scatter(coords52['x'], coords52['y'], c=values, s=220,
                    marker='s', cmap=cmap, vmin=vmin, vmax=vmax)
    ax.scatter([15,15], [3,-3], marker='x', s=50, color='gray')
    ax.axhline(0, color='gray', linewidth=.5)
    ax.axvline(0, color='gray', linewidth=.5)
    ax.set(xlim=(-30,30), ylim=(-26,26), aspect='equal', title=title,
           xlabel='x (deg), right-eye convention', ylabel='y (deg)')
    return sc

example_id = int(train_ids[0])  # 結果の見栄えで患者を選ばない
example = train_df[train_df['id'] == example_id].sort_values('date')
fig, axes = plt.subplots(1,3, figsize=(12,3.8), constrained_layout=True)
for ax, k in zip(axes, [0,1,2]):
    sc = map_values(ax, example.iloc[k][locs].to_numpy(dtype=float),
                    f'Patient {example_id}, visit {k+1}', vmax=45)
fig.colorbar(sc, ax=axes, label='Sensitivity (dB)', shrink=.8)
fig.savefig(OUT / '01_three_fields.png', dpi=160, bbox_inches='tight')
plt.show()

ms = example[locs].mean(axis=1)  # Mean sensitivity。MDではない
fig, axes = plt.subplots(1,2, figsize=(11,3.7), constrained_layout=True)
axes[0].plot(example['visit'], ms, 'o-', label='Mean sensitivity')
axes[0].set(xlabel='Recorded visit order', ylabel='MS (dB)',
            title=f'Patient {example_id}: 52-point mean')
for point in ['l1','l10','l20']:
    axes[1].plot(example['visit'], example[point], 'o-', label=point, alpha=.8)
axes[1].set(xlabel='Recorded visit order', ylabel='Sensitivity (dB)',
            title='Three prespecified locations')
axes[1].legend()
fig.savefig(OUT / '02_retest_variation.png', dpi=160, bbox_inches='tight')
plt.show()

# 3-A. 未来の値・未来の日時をXへ入れない
histories, targets, metadata = [], [], []
for (pid, eye), g in df.groupby(['id','eye'], sort=True):
    g = g.sort_values('date').reset_index(drop=True)
    values = g[locs].to_numpy(dtype=float)
    for j in range(HISTORY, len(g)):
        h = values[j-HISTORY:j]
        assert g.loc[j-1,'date'] < g.loc[j,'date']
        histories.append(h)
        targets.append(values[j])
        metadata.append({'id': int(pid), 'eye': eye,
                         'target_visit': int(g.loc[j,'visit']),
                         'history_last_date': g.loc[j-1,'date'],
                         'target_date': g.loc[j,'date'],
                         'gap_days': float(g.loc[j,'gap_days']),
                         'target_fl': float(g.loc[j,'fl'])})
history = np.stack(histories)
Y = np.stack(targets)
meta = pd.DataFrame(metadata)
mean3 = history.mean(axis=1)  # axis=1 は「3検査」の方向
last = history[:,-1,:]
X = np.concatenate([mean3, last-mean3], axis=1)
is_train = meta['id'].isin(train_ids).to_numpy()
is_test = meta['id'].isin(test_ids).to_numpy()
assert history.shape == (270,3,52) and X.shape == (270,104) and Y.shape == (270,52)
assert (is_train.sum(),is_test.sum()) == (189,81)
assert np.all(is_train ^ is_test)
assert set(meta.loc[is_train,'id']).isdisjoint(set(meta.loc[is_test,'id']))
print('history, X, Y:', history.shape, X.shape, Y.shape)
print('training / evaluation windows:', is_train.sum(), is_test.sum())
display(meta.head())

# 4-A. 固定モデルを学習。評価側にはfitを使わない
model = make_pipeline(StandardScaler(), Ridge(alpha=ALPHA, solver='svd'))
model.fit(X[is_train], Y[is_train])
preds = {'last': last[is_test].copy(),
         'mean3': mean3[is_test].copy(),
         'ridge': model.predict(X[is_test])}
y_test = Y[is_test]
test_meta = meta.loc[is_test].reset_index(drop=True)
assert all(p.shape == y_test.shape and np.isfinite(p).all() for p in preds.values())
print('Evaluation patients:', test_meta['id'].nunique(), 'windows:', len(test_meta))
print('Predicted points per window:', y_test.shape[1])
print('Ridge negative predictions:', int((preds['ridge'] < 0).sum()))
# 負値なども黙ってクリップせず、このモデルの性質として評価・記録する

# 5-A. 患者別、集団平均、対応のある差
patient_mae = pd.DataFrame(index=test_ids)
patient_mae.index.name = 'id'
for name, pred in preds.items():
    per_window = np.abs(pred-y_test).mean(axis=1)
    patient_mae[name] = (pd.DataFrame({'id': test_meta['id'], 'mae': per_window})
                         .groupby('id')['mae'].mean())
metrics = pd.DataFrame({
    'patient_macro_MAE_dB': patient_mae.mean(),
    'worst_patient_MAE_dB': patient_mae.max(),
    'negative_predictions': {name: int((p < 0).sum()) for name,p in preds.items()}
})
display(metrics.round(4))
display(patient_mae.round(3))
metrics.to_csv(OUT / 'metrics.csv', encoding='utf-8-sig')
patient_mae.to_csv(OUT / 'patient_mae.csv', encoding='utf-8-sig')

fig, axes = plt.subplots(1,2, figsize=(11,4.2), constrained_layout=True)
colors = {'last':'#9a7b53','mean3':'#168c87','ridge':'#6c66b5'}
axes[0].bar(metrics.index, metrics['patient_macro_MAE_dB'],
            color=[colors[n] for n in metrics.index])
axes[0].set(ylabel='Patient-macro MAE (dB)', title='Lower is closer to the next measurement')
for name in preds:
    axes[1].plot([str(i) for i in patient_mae.index], patient_mae[name],
                 'o-', label=name, color=colors[name])
axes[1].set(xlabel='Held-out patient ID', ylabel='MAE (dB)', title='Variation between patients')
axes[1].legend()
fig.savefig(OUT / '03_model_comparison.png', dpi=170, bbox_inches='tight')
plt.show()

# 5-B. 患者単位のpaired bootstrap。負の差ならAの方が誤差が小さい
def paired_patient_bootstrap(a, b, repetitions=5000, seed=SEED):
    differences = (patient_mae[a] - patient_mae[b]).to_numpy()
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(differences), size=(repetitions, len(differences)))
    boot = differences[idx].mean(axis=1)
    lo, hi = np.quantile(boot, [.025,.975])
    return {'comparison': f'{a} - {b}', 'mean_difference_dB': float(differences.mean()),
            'ci_2.5%': float(lo), 'ci_97.5%': float(hi), 'patients': len(differences)}
ci = pd.DataFrame([paired_patient_bootstrap('mean3','last'),
                   paired_patient_bootstrap('ridge','mean3')])
display(ci.round(4))
ci.to_csv(OUT / 'paired_bootstrap.csv', index=False, encoding='utf-8-sig')

# 5-C. 同じ重みで患者別平均を作ってから、点ごとに集計
point_mae = {}
for name, pred in preds.items():
    per_patient = [np.abs(pred[test_meta['id'].eq(pid).to_numpy()] -
                          y_test[test_meta['id'].eq(pid).to_numpy()]).mean(axis=0)
                   for pid in test_ids]
    point_mae[name] = np.stack(per_patient).mean(axis=0)
fig, axes = plt.subplots(1,3, figsize=(12,4), constrained_layout=True)
vmax = max(float(v.max()) for v in point_mae.values())
for ax, name in zip(axes, preds):
    sc = map_values(ax, point_mae[name], f'{name}: point-wise MAE', vmax=vmax, cmap='magma')
fig.colorbar(sc, ax=axes, label='MAE (dB)', shrink=.8)
fig.savefig(OUT / '04_pointwise_errors.png', dpi=170, bbox_inches='tight')
plt.show()
pd.DataFrame(point_mae, index=locs).to_csv(OUT/'point_mae.csv', encoding='utf-8-sig')

# 将来の正解値ではなく、予測時に知っている過去3回平均で層別する
prior = mean3[is_test]
bands = [('0-<15 dB',0,15), ('15-<25 dB',15,25), ('25+ dB',25,np.inf)]
band_rows = []
for label, lo, hi in bands:
    mask = (prior >= lo) & (prior < hi)
    for name, pred in preds.items():
        per_patient = []
        for pid in test_ids:
            rows = test_meta['id'].eq(pid).to_numpy()
            selected = mask[rows]
            if selected.any():
                per_patient.append(float(np.abs(pred[rows]-y_test[rows])[selected].mean()))
        band_rows.append({'prior_band': label, 'method': name,
                          'patients_with_points': len(per_patient),
                          'point_observations': int(mask.sum()),
                          'patient_macro_MAE_dB': float(np.mean(per_patient)) if per_patient else np.nan})
band_metrics = pd.DataFrame(band_rows)
display(band_metrics.round(3))
band_metrics.to_csv(OUT/'sensitivity_bands.csv',index=False,encoding='utf-8-sig')

# 5-D. 失敗例の調査。選び方を記録する
worst_id = int(patient_mae['ridge'].idxmax())
within = np.flatnonzero(test_meta['id'].eq(worst_id).to_numpy())
ridge_window_error = np.abs(preds['ridge']-y_test).mean(axis=1)
worst_k = int(within[np.argmax(ridge_window_error[within])])
fig, axes = plt.subplots(1,3, figsize=(12,4), constrained_layout=True)
sc_sens = map_values(axes[0], mean3[is_test][worst_k], 'Past 3-visit mean', vmax=45)
map_values(axes[1], y_test[worst_k], 'Next observed measurement', vmax=45)
fig.colorbar(sc_sens, ax=axes[:2], label='Sensitivity (dB)', shrink=.8)
delta = preds['ridge'][worst_k] - y_test[worst_k]
limit = max(1., float(np.abs(delta).max()))
sc = map_values(axes[2], delta, 'Ridge minus observed', vmin=-limit, vmax=limit, cmap='coolwarm')
fig.colorbar(sc, ax=axes[2], label='Signed error (dB)', shrink=.8)
fig.suptitle(f'Error review: patient {worst_id}, visit {test_meta.loc[worst_k,"target_visit"]}')
fig.savefig(OUT / '05_error_review.png', dpi=170, bbox_inches='tight')
plt.show()
display(test_meta.loc[[worst_k]])
print('This is an error-selected case, not a representative example.')

# 6-A. 実装例：データ契約と確認事項を持つ予測関数
training_range = (float(history[is_train].min()), float(history[is_train].max()))
def predict_next_field(exams, method='mean3'):
    if method not in ('last','mean3','ridge'):
        raise ValueError('method must be last, mean3, or ridge')
    required = ['id','eye','date'] + locs
    missing = [c for c in required if c not in exams.columns]
    if missing:
        raise ValueError(f'Missing required columns: {missing}')
    g = exams[required].copy()
    if g[['id','eye','date']].isna().any().any():
        raise ValueError('Missing patient, eye, or date')
    if len(g[['id','eye']].drop_duplicates()) != 1:
        raise ValueError('Input must contain exactly one patient and one eye')
    if not g['eye'].isin(['OD','OS']).all():
        raise ValueError('eye must be OD or OS')
    g['date'] = pd.to_datetime(g['date'], errors='raise')
    if g['date'].isna().any():
        raise ValueError('Missing exam date after parsing')
    if g['date'].duplicated().any():
        raise ValueError('Duplicate exam date')
    if len(g) < HISTORY:
        raise ValueError('At least 3 past examinations are required')
    g = g.sort_values('date').tail(HISTORY)
    h = g[locs].to_numpy(dtype=float)
    if not np.isfinite(h).all():
        raise ValueError('Non-finite sensitivity; review missing data first')
    if (h < 0).any():
        raise ValueError('This tutorial data contract expects non-negative dB values')
    m, l = h.mean(axis=0), h[-1]
    if method == 'last':
        p = l.copy()
    elif method == 'mean3':
        p = m.copy()
    else:
        x = np.concatenate([m,l-m])[None,:]
        p = model.predict(x)[0]
    flags = []
    low, high = training_range
    if ((h < low) | (h > high)).any():
        flags.append('input_outside_observed_training_range')
    if ((p < low) | (p > high)).any():
        flags.append('prediction_outside_observed_training_range')
    return {'patient_id': int(g['id'].iloc[0]), 'eye': str(g['eye'].iloc[0]),
            'as_of_date': g['date'].max().date().isoformat(), 'method': method,
            'unit': 'dB', 'coordinate_convention': 'right-eye',
            'predicted_sensitivity': dict(zip(locs, map(float,p))),
            'status': 'review' if flags else 'computed', 'flags': flags,
            'purpose': 'educational_next_measurement_prediction'}

demo_id = int(test_ids[0])
demo = df[df['id'].eq(demo_id)].sort_values('date').head(HISTORY)
demo_output = predict_next_field(demo, method='mean3')
display({k:v for k,v in demo_output.items() if k != 'predicted_sensitivity'})
display(pd.Series(demo_output['predicted_sensitivity']).head())
(OUT/'poc_example.json').write_text(json.dumps(demo_output,ensure_ascii=False,indent=2),encoding='utf-8')

# 仕様の確認：患者が混ざった入力は受け付けない
bad = pd.concat([demo, df[df['id'].eq(int(test_ids[1]))].head(1)], ignore_index=True)
try:
    predict_next_field(bad)
except ValueError as e:
    print('Expected rejection:', e)
else:
    raise AssertionError('Mixed-patient input must be rejected')

# 6-B. 数値入りの下書きを保存。考察欄を自分の言葉で完成させる
summary_lines = [
    '研究メモ：視野の短期再検査データによる次回測定値の予測',
    '',
    '問い：過去3回の測定は、前回値だけより次回の52点をよく予測するか。',
    '資料：visualFields::vfpwgRetest24d2。30患者・30眼・360検査。',
    '出典：Artes et al. 2014, doi:10.1016/j.ophtha.2014.04.015',
    f'設計：学習21人・189窓／評価9人・81窓。seed={SEED}。',
    '入力：過去3回。目的変数：日付順で次の検査の52点感度。',
    '盲点付近2点のみを位置定義により除外。患者・検査の除外なし。',
    '評価：患者内で点・回を平均したMAEを患者間で等しく平均。',
    '', '結果（dB、小さいほど次回の測定に近い）：',
]
for name, row in metrics.iterrows():
    summary_lines.append(f'  {name}: MAE={row.patient_macro_MAE_dB:.4f}, '
                         f'最大患者MAE={row.worst_patient_MAE_dB:.4f}')
summary_lines += ['', '患者単位paired bootstrap（95% percentile区間）：']
for _, row in ci.iterrows():
    summary_lines.append(f'  {row["comparison"]}: {row["mean_difference_dB"]:.4f} '
                         f'[{row["ci_2.5%"]:.4f}, {row["ci_97.5%"]:.4f}]')
summary_lines += [
    '', 'QC：fprが0固定、time/durationが0固定。ID 7に資料の週次説明と異なる長い間隔。',
    f'失敗例：Ridge患者MAE最大のID {worst_id}を、選択規則を明示して点別に調査。',
    '', '解釈（自分で記入）：',
    '  1. どの方法がどう違ったか。患者別に逆転はあったか。',
    '  2. 期待と違った結果を説明する仮説を2つ。未検証であることも記す。',
    '  3. 次の実験を1つ。追加で必要なデータと成功条件を記す。',
    '', '限界：9患者の評価。単一の小さな再検査データ。Ridgeの調整・外部検証なし。',
    '      次回の測定値の予測であり、真の感度回復・診断・長期進行の実証ではない。',
    '      bootstrapは学習集合や施設差の不確実性を含まない。',
    '      最小のテスト誤差を見て勝者を選び、その誤差を確定性能と扱わない。'
]
report = '\n'.join(summary_lines)
(OUT/'research_memo.txt').write_text(report,encoding='utf-8')
print(report)
(OUT/'environment.json').write_text(json.dumps(VERSIONS,indent=2),encoding='utf-8')

# 6-C. 結果だけをZIPにまとめる（必要に応じてダウンロード）
import zipfile
archive = Path('findex_results.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in sorted(OUT.rglob('*')):
        if p.is_file():
            z.write(p, arcname=str(p))
print('Saved:', archive.resolve())
# Colabで自動ダウンロードする場合のみ、次の2行を有効にする：
# from google.colab import files
# files.download(str(archive))
