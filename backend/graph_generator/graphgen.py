import random
import math
import numpy as np
import pandas as pd
import networkx as nx
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

N_TRANSACTIONS = 20000        # total transactions
N_CARDS = 4000                # distinct cards
N_DEVICES = 3500
N_MERCHANTS = 800
start_time = datetime(2024,1,1)

def random_amount():
    # realistic skewed distribution
    return max(1.0, float(np.random.exponential(scale=60.0)))

merchant_categories = ['grocery','electronics','travel','food','entertainment','utilities','fashion','health']
def sample_merchant_category():
    return random.choice(merchant_categories)

def make_transaction(i):
    card_id = f"card_{random.randint(0, N_CARDS-1)}"
    device_id = f"dev_{random.randint(0, N_DEVICES-1)}"
    merchant_id = f"m_{random.randint(0, N_MERCHANTS-1)}"
    amount = round(random_amount(),2)
    # time spaced randomly; some users have bursts
    ts = start_time + timedelta(seconds=int(np.random.exponential(scale=3600*24)))
    category = sample_merchant_category()
    # simple derived features
    is_high_risk_merchant = 1 if category in ['electronics','travel'] and random.random()<0.12 else 0
    location_distance = abs(np.random.normal(loc=5.0, scale=15.0))  # km from home
    return {
        'tx_id': f'tx_{i}',
        'card_id': card_id,
        'device_id': device_id,
        'merchant_id': merchant_id,
        'amount': amount,
        'timestamp': ts.isoformat(),
        'merchant_category': category,
        'is_high_risk_merchant': is_high_risk_merchant,
        'location_distance_km': round(location_distance,2)
    }

# generate transactions
tx_list = [make_transaction(i) for i in range(N_TRANSACTIONS)]
df_tx = pd.DataFrame(tx_list)

# Inject fraud patterns:
# 1) high-amount rapid sequence from new device for a card
# 2) multiple failed attempts (we simulate as many small txs + one large)
fraud_labels = np.zeros(len(df_tx), dtype=int)

# Strategy A: For some cards, create burst of high-value txs from different devices
n_fraud_cards = int(N_CARDS * 0.02)   # 2% cards involved in fraud
fraud_card_ids = [f"card_{i}" for i in np.random.choice(range(N_CARDS), n_fraud_cards, replace=False)]
for card in fraud_card_ids:
    # select some transactions for this card to mark as fraud
    idxs = df_tx[df_tx['card_id']==card].index
    if len(idxs)==0:
        continue
    chosen = np.random.choice(idxs, min(3, len(idxs)), replace=False)
    for idx in chosen:
        fraud_labels[idx] = 1
        # bump amount to signify fraud
        df_tx.at[idx,'amount'] = df_tx.at[idx,'amount'] * (5 + np.random.rand()*10)
        df_tx.at[idx,'is_high_risk_merchant'] = 1

# Strategy B: random scattered single fraudulent txs
random_frauds = np.random.choice(df_tx.index, size=int(N_TRANSACTIONS*0.01), replace=False)
fraud_labels[random_frauds] = 1
for idx in random_frauds:
    df_tx.at[idx,'amount'] = df_tx.at[idx,'amount'] * (3 + np.random.rand()*7)
    df_tx.at[idx,'is_high_risk_merchant'] = 1

df_tx['label'] = fraud_labels

# Build graph edges (simple heuristics)
G = nx.Graph()
for i, row in df_tx.iterrows():
    G.add_node(row['tx_id'], **row.to_dict())

# Edges:
# Connect transactions with same card, same device, same merchant, or within 5 minutes from same card
card_groups = df_tx.groupby('card_id').groups
for card, idxs in card_groups.items():
    idxs = list(idxs)
    if len(idxs) <= 1: continue
    # fully connect small groups or make chain for large
    if len(idxs) < 6:
        for a in idxs:
            for b in idxs:
                if a < b:
                    G.add_edge(df_tx.at[a,'tx_id'], df_tx.at[b,'tx_id'], edge_type='same_card')
    else:
        # connect nearest by time
        sub = df_tx.loc[idxs].sort_values('timestamp')
        ids = sub['tx_id'].values
        for i1,i2 in zip(ids[:-1], ids[1:]):
            G.add_edge(i1, i2, edge_type='same_card')

# same device
device_groups = df_tx.groupby('device_id').groups
for dev, idxs in device_groups.items():
    idxs = list(idxs)
    if len(idxs) <= 1: continue
    for a in idxs[:10]:
        for b in idxs[:10]:
            if a < b:
                G.add_edge(df_tx.at[a,'tx_id'], df_tx.at[b,'tx_id'], edge_type='same_device')

# same merchant (light connecting)
merchant_groups = df_tx.groupby('merchant_id').groups
for m, idxs in merchant_groups.items():
    idxs = list(idxs)
    if len(idxs) <= 1: continue
    sample_idxs = np.random.choice(idxs, min(8, len(idxs)), replace=False)
    for i1 in sample_idxs:
        for i2 in sample_idxs:
            if i1 < i2:
                G.add_edge(df_tx.at[i1,'tx_id'], df_tx.at[i2,'tx_id'], edge_type='same_merchant')

# quick succession edges (within 5 minutes for same card)
df_tx['timestamp_dt'] = pd.to_datetime(df_tx['timestamp'])
grouped = df_tx.sort_values('timestamp_dt').groupby('card_id')
for _, sub in grouped:
    sub = sub.sort_values('timestamp_dt')
    for i in range(len(sub)-1):
        t1 = sub.iloc[i]['timestamp_dt']
        t2 = sub.iloc[i+1]['timestamp_dt']
        if (t2 - t1).total_seconds() < 300:  # 5 minutes
            id1 = sub.iloc[i]['tx_id']; id2 = sub.iloc[i+1]['tx_id']
            G.add_edge(id1, id2, edge_type='quick_succession')

# Export node table and edges
edges = []
for u,v,data in G.edges(data=True):
    edges.append({'source': u, 'target': v, 'edge_type': data.get('edge_type','unknown')})
df_edges = pd.DataFrame(edges)

# Save CSVs
df_tx.drop(columns=['timestamp_dt']).to_csv('transactions.csv', index=False)
df_edges.to_csv('edges.csv', index=False)

print("Saved transactions.csv and edges.csv")
print("Transactions:", len(df_tx), "Edges:", len(df_edges))
