"""
Render all .mmd files in diagrams/ to PNG using mermaid-cli.
"""
import os
import subprocess
import glob

DIAGRAMS_DIR = 'diagrams'

def render_all():
    mmd_files = sorted(glob.glob(os.path.join(DIAGRAMS_DIR, '*.mmd')))
    print(f"Found {len(mmd_files)} .mmd files to render\n")
    
    success = 0
    for mmd_file in mmd_files:
        png_file = mmd_file.replace('.mmd', '.png')
        name = os.path.basename(mmd_file)
        
        # Skip if already rendered
        if os.path.exists(png_file) and os.path.getsize(png_file) > 0:
            print(f"  ✅ {name} (already exists, {os.path.getsize(png_file):,} bytes)")
            success += 1
            continue
        
        print(f"  🎨 Rendering {name}...")
        try:
            result = subprocess.run(
                f'npx -y @mermaid-js/mermaid-cli -i "{mmd_file}" -o "{png_file}" -w 1200 -b white',
                capture_output=True, text=True, timeout=60,
                shell=True,
                cwd=os.getcwd()
            )
            
            if os.path.exists(png_file) and os.path.getsize(png_file) > 0:
                print(f"    ✅ {os.path.getsize(png_file):,} bytes")
                success += 1
            else:
                stderr = result.stderr[:200] if result.stderr else 'no output'
                print(f"    ❌ Failed: {stderr}")
        except subprocess.TimeoutExpired:
            print(f"    ❌ Timeout")
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    print(f"\n✅ Rendered {success}/{len(mmd_files)} diagrams")

if __name__ == '__main__':
    render_all()
