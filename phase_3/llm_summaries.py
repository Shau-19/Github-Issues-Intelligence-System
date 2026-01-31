import pandas as pd
import json
import os
from dotenv import load_dotenv
load_dotenv()
df = pd.read_csv('data/issues_with_severity.csv')

with open('data/cluster_analysis.json', 'r') as f:
    clusters = json.load(f)

# Groq LLM for RAG summaries
def generate_rag_summary(cluster_name, samples, features):
    """RAG: Retrieve cluster samples + Generate explanation"""
    try:
        from groq import Groq
        
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # RAG prompt: Context + Question
        context = "\n".join(f"- {s}" for s in samples[:5])
        
        prompt = f"""Cluster: {cluster_name}
                    Features: {features}

                    Sample issues:
                                {context}

                    Answer in 2 sentences:
                                1. Root cause pattern
                                2. Recommended action (fix/investigate/automate/monitor)"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Pattern: {cluster_name.lower()} (LLM unavailable)"

summaries = {}

for cluster_id, info in clusters.items():
    name = info['name']
    size = info['size']
    samples = info['sample_titles'][:5]
    
    # Feature summary for context
    features_desc = f"{info['features']['avg_severity']:.1f} severity"
    if info['features'].get('has_error_trace', 0) > 0.5:
        features_desc += ", error traces"
    
    # RAG: Retrieve samples + Generate explanation
    root_cause = generate_rag_summary(name, samples, features_desc)
    
    summary = {
        'cluster': name,
        'size': size,
        'root_cause': root_cause,
        'samples': samples[:3],
        'features': features_desc
    }
    
    summaries[name] = summary
    
    print(f"\n🔷 {name} ({size} issues)")
    print(f"   📊 Features: {features_desc}")
    print(f"   💡 Root cause: {root_cause}")
    print(f"   📝 Sample: {samples[0][:60]}...")

with open('data/cluster_summaries.json', 'w') as f:
    json.dump(summaries, f, indent=2)

print("\n✅ Saved: cluster_summaries.json (RAG-powered)")