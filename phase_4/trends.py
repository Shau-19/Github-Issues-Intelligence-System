import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Seaborn styling
sns.set_style("whitegrid")
sns.set_palette("husl")

# Load data
df = pd.read_csv('data/issues_with_severity.csv')
df['created_at'] = pd.to_datetime(df['created_at'])
df['month'] = df['created_at'].dt.to_period('M')

# Monthly aggregation
trends = df.groupby(['month', 'cluster_name']).size().reset_index(name='count')
top_clusters = df['cluster_name'].value_counts().head(3).index

# Plot
plt.figure(figsize=(14, 6))
for cluster in top_clusters:
    data = trends[trends['cluster_name'] == cluster]
    plt.plot(data['month'].astype(str), data['count'], 
             marker='o', label=cluster, linewidth=2.5, markersize=7)

plt.xlabel('Month', fontsize=12, fontweight='bold')
plt.ylabel('Issues', fontsize=12, fontweight='bold')
plt.title('Issue Trends by Cluster (Monthly)', fontsize=14, fontweight='bold', pad=15)
plt.legend(fontsize=11, frameon=True)

# Clean x-axis
ax = plt.gca()
labels = [label.get_text() for label in ax.get_xticklabels()]
ax.set_xticks(range(0, len(labels), 3))
ax.set_xticklabels(labels[::3], rotation=45, ha='right', fontsize=10)

plt.tight_layout()
plt.savefig('data/trends.png', dpi=300, bbox_inches='tight')

print("✅ Saved: trends.png (seaborn styled)")