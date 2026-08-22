"""
Adim 3.3 - Re-ID degerlendirmesi

Gomuler uzerinde kosinus benzerligi ile en-yakin-komsu eslestirmesi yapar ve
SeaTurtleID2022'nin resmi bolunmelerinde raporlar:

  split_closed         - zamansal (yil bazli) bolunme; gercekci senaryo
  split_closed_random  - rastgele bolunme; ayni gunun karelerini sizdirir
  split_open           - acik-set: sorgularin bir kismi galeride hic yok

Metrikler: top-1 / top-5 dogruluk, mAP ve acik-set icin esik tabanli
  "yeni birey" ayrimi (kabul edilen esikte precision/recall).

Not: burada egitim yok. Bu, pretrained backbone + kosinus kNN temel cizgisi.
Uretimde bu skorlar, metrik ogrenme (ArcFace vb.) ile iyilestirilir.
"""

import argparse
import os

import numpy as np


def load(npz_path):
    d = np.load(npz_path, allow_pickle=True)
    return d


def _rank_metrics(sim, q_ident, g_ident, topk=(1, 5, 10)):
    """sim: [Q, G] kosinus benzerlik matrisi. Sadece galeride var olan sorgular."""
    order = np.argsort(-sim, axis=1)
    ranked = g_ident[order]                    # [Q, G] kimlik etiketleri
    hits = ranked == q_ident[:, None]

    out = {}
    for k in topk:
        out[f'top{k}'] = float(hits[:, :k].any(axis=1).mean())

    # mAP
    aps = []
    for i in range(hits.shape[0]):
        rel = hits[i]
        n_rel = rel.sum()
        if n_rel == 0:
            aps.append(0.0)
            continue
        idx = np.flatnonzero(rel)
        prec = (np.arange(len(idx)) + 1) / (idx + 1)
        aps.append(float(prec.mean()))
    out['mAP'] = float(np.mean(aps))
    return out


def evaluate_closed(emb, ident, split, gallery=('train', 'valid'), query='test'):
    g_mask = np.isin(split, gallery)
    q_mask = split == query
    G, Q = emb[g_mask], emb[q_mask]
    g_ident, q_ident = ident[g_mask], ident[q_mask]

    # Kapali-set: galeride karsiligi olmayan sorgular disarida birakilir
    known = np.isin(q_ident, np.unique(g_ident))
    dropped = int((~known).sum())
    Q, q_ident = Q[known], q_ident[known]

    sim = Q @ G.T                              # gomuler L2-normalize
    res = _rank_metrics(sim, q_ident, g_ident)
    res.update(gallery_size=int(G.shape[0]), query_size=int(Q.shape[0]),
               gallery_identities=int(len(np.unique(g_ident))),
               dropped_unknown_queries=dropped)
    return res


def evaluate_open(emb, ident, split, gallery=('train', 'valid'), query='test'):
    """Acik-set: 'galeride yok' kararini esikle ver, en iyi F1 esigini bul."""
    g_mask = np.isin(split, gallery)
    q_mask = split == query
    G, Q = emb[g_mask], emb[q_mask]
    g_ident, q_ident = ident[g_mask], ident[q_mask]

    known_ids = set(np.unique(g_ident).tolist())
    is_known = np.array([i in known_ids for i in q_ident])

    sim = Q @ G.T
    best_idx = np.argmax(sim, axis=1)
    best_sim = sim[np.arange(len(Q)), best_idx]
    pred_ident = g_ident[best_idx]

    rows = []
    for thr in np.arange(0.50, 0.96, 0.01):
        accept = best_sim >= thr                      # 'mevcut kayit' dedik
        tp = int((accept & is_known & (pred_ident == q_ident)).sum())
        fp = int((accept & (~is_known | (pred_ident != q_ident))).sum())
        fn = int(((~accept) & is_known).sum())
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        # yeni birey tespiti
        new_correct = int(((~accept) & (~is_known)).sum())
        new_total = int((~is_known).sum())
        rows.append(dict(threshold=round(float(thr), 2), precision=prec, recall=rec,
                         f1=f1, new_individual_recall=new_correct / new_total if new_total else 0.0))

    best = max(rows, key=lambda r: r['f1'])
    return dict(query_size=int(len(Q)), known_queries=int(is_known.sum()),
                unknown_queries=int((~is_known).sum()), best=best, sweep=rows)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description='Re-ID degerlendirme')
    ap.add_argument('--embeddings',
                    default=os.path.join(here, 'data', 'embeddings_resnet50_head.npz'))
    ap.add_argument('--json-out', default=os.path.join(here, 'data', 'eval_results.json'))
    args = ap.parse_args()

    d = load(args.embeddings)
    emb = d['embeddings'].astype(np.float32)
    ident = d['identity'].astype(str)
    ok = d['ok'] if 'ok' in d else np.ones(len(emb), dtype=np.int8)

    valid = ok == 1
    if (~valid).any():
        print(f'{(~valid).sum()} okunamayan goruntu haric tutuldu')
    emb, ident = emb[valid], ident[valid]

    print(f'Gomu: {emb.shape} | {len(np.unique(ident))} birey\n')

    results = {}
    for split_col in ('split_closed', 'split_closed_random'):
        if split_col not in d:
            continue
        split = d[split_col].astype(str)[valid]
        r = evaluate_closed(emb, ident, split)
        results[split_col] = r
        print(f'== {split_col} (kapali-set) ==')
        print(f'   galeri {r["gallery_size"]} goruntu / {r["gallery_identities"]} birey,'
              f' sorgu {r["query_size"]}')
        print(f'   top-1 {r["top1"]*100:6.2f}%   top-5 {r["top5"]*100:6.2f}%'
              f'   top-10 {r["top10"]*100:6.2f}%   mAP {r["mAP"]*100:6.2f}%')
        if r['dropped_unknown_queries']:
            print(f'   (galeride olmayan {r["dropped_unknown_queries"]} sorgu haric)')
        print()

    if 'split_open' in d:
        split = d['split_open'].astype(str)[valid]
        r_closed = evaluate_closed(emb, ident, split)
        r_open = evaluate_open(emb, ident, split)
        results['split_open'] = {'closed_metrics': r_closed, 'open_set': r_open}
        print('== split_open (acik-set) ==')
        print(f'   bilinen sorgu {r_open["known_queries"]},'
              f' yeni birey {r_open["unknown_queries"]}')
        b = r_open['best']
        print(f'   en iyi F1 esigi: {b["threshold"]:.2f}'
              f' -> precision {b["precision"]*100:.2f}%  recall {b["recall"]*100:.2f}%'
              f'  F1 {b["f1"]*100:.2f}%')
        print(f'   yeni-birey yakalama: {b["new_individual_recall"]*100:.2f}%')
        print()

    import json
    with open(args.json_out, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f'-> {args.json_out}')


if __name__ == '__main__':
    main()
