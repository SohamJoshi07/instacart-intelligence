import pandas as pd
import os
import shutil

os.makedirs('data/processed', exist_ok=True)

# ── FIX 1: Convert rfm_segments to correct parquet files ──────
print("Loading rfm_segments...")
df = pd.read_parquet('data/processed/rfm_segments.csv')

# Add cluster column if missing
if 'cluster' not in df.columns:
    segment_map = {s: i for i, s in enumerate(df['segment'].unique())}
    df['cluster'] = df['segment'].map(segment_map)

# Save user_segments.parquet
cols_seg = ['user_id', 'recency', 'frequency', 'rfm_r', 'rfm_f', 'cluster', 'segment']
df[cols_seg].to_parquet('data/processed/user_segments.parquet', index=False)
print(f"user_segments.parquet saved: {df[cols_seg].shape}")

# Save user_rfm.parquet
cols_rfm = ['user_id', 'recency', 'frequency', 'rfm_r', 'rfm_f']
df[cols_rfm].to_parquet('data/processed/user_rfm.parquet', index=False)
print(f"user_rfm.parquet saved: {df[cols_rfm].shape}")

# ── FIX 2: Rename user_summary to user_order_summary ──────────
src = 'data/processed/user_summary.parquet'
dst = 'data/processed/user_order_summary.parquet'

if os.path.exists(dst):
    print("user_order_summary.parquet already exists - skipping")
elif os.path.exists(src):
    shutil.copy(src, dst)
    print("user_order_summary.parquet created from user_summary.parquet")
else:
    print("WARNING: user_summary.parquet not found")

# ── FINAL CHECK ───────────────────────────────────────────────
print()
print("Files in data/processed/:")
for f in sorted(os.listdir('data/processed')):
    size = os.path.getsize(f'data/processed/{f}')
    print(f"  {f:45s} {size/1024/1024:.1f} MB")

# ── VALIDATE ──────────────────────────────────────────────────
print()
print("Validating user_segments.parquet...")
seg = pd.read_parquet('data/processed/user_segments.parquet')
print(f"  Rows:     {len(seg):,}")
print(f"  Columns:  {list(seg.columns)}")
print(f"  Nulls:    {seg.isnull().sum().sum()}")
print()
print("Segment distribution:")
for seg_name, count in seg['segment'].value_counts().items():
    pct = count / len(seg) * 100
    print(f"  {seg_name:20s}: {count:,} users ({pct:.1f}%)")

print()
print("All files ready for Phase 3.")