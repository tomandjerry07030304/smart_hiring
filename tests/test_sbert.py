"""Diagnose sentence-transformers import issue."""
import os
os.environ['USE_SENTENCE_TRANSFORMERS'] = 'true'

print("Step 1: Checking sentence_transformers import...")
try:
    from sentence_transformers import SentenceTransformer
    print("  OK - sentence_transformers imported!")
    
    print("Step 2: Loading model all-MiniLM-L6-v2...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("  OK - Model loaded!")
    
    print("Step 3: Test encoding...")
    emb = model.encode(["Hello world", "Test sentence"])
    print(f"  OK - Embeddings shape: {emb.shape}")
    print("\nSBERT is FULLY WORKING!")
    
except ImportError as e:
    print(f"  IMPORT ERROR: {e}")
    print("  Checking sub-dependencies...")
    
    for lib in ['torch', 'transformers', 'numpy', 'scipy', 'sklearn']:
        try:
            __import__(lib)
            print(f"    {lib}: OK")
        except ImportError as ie:
            print(f"    {lib}: MISSING - {ie}")

except Exception as e:
    print(f"  OTHER ERROR: {type(e).__name__}: {e}")
