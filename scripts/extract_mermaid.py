"""
Extract all Mermaid diagram blocks from PROJECT_DOCUMENTATION.md,
save each as a .mmd file, and render to PNG using mmdc (mermaid-cli).
"""
import re
import os
import subprocess

INPUT_MD = 'PROJECT_DOCUMENTATION.md'
DIAGRAMS_DIR = 'diagrams'

def extract_mermaid_blocks(md_path):
    """Extract all mermaid code blocks from the markdown file."""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all ```mermaid ... ``` blocks
    pattern = r'```mermaid\s*\n(.*?)```'
    matches = list(re.finditer(pattern, content, re.DOTALL))
    
    diagrams = []
    for i, match in enumerate(matches):
        code = match.group(1).strip()
        # Determine diagram name from context (look at preceding heading)
        start = match.start()
        # Find the nearest heading before this block
        preceding_text = content[:start]
        headings = re.findall(r'#+\s+(.+)', preceding_text)
        if headings:
            last_heading = headings[-1].strip()
            # Create clean filename from heading
            name = re.sub(r'[^a-zA-Z0-9]+', '_', last_heading).strip('_').lower()
            name = name[:50]  # limit length
        else:
            name = f'diagram_{i+1}'
        
        diagrams.append({
            'index': i + 1,
            'name': name,
            'code': code,
            'match_start': match.start(),
            'match_end': match.end()
        })
    
    return diagrams

def render_diagrams(diagrams, output_dir):
    """Render each mermaid diagram to PNG using mmdc."""
    os.makedirs(output_dir, exist_ok=True)
    rendered = []
    
    for d in diagrams:
        mmd_file = os.path.join(output_dir, f"{d['index']:02d}_{d['name']}.mmd")
        png_file = os.path.join(output_dir, f"{d['index']:02d}_{d['name']}.png")
        
        # Write .mmd file
        with open(mmd_file, 'w', encoding='utf-8') as f:
            f.write(d['code'])
        
        # Render with mmdc
        print(f"  [{d['index']}/{len(diagrams)}] Rendering: {d['name']}...")
        try:
            result = subprocess.run(
                ['npx', '-y', '@mermaid-js/mermaid-cli', 'mmdc',
                 '-i', mmd_file, '-o', png_file,
                 '-w', '1200', '-b', 'white',
                 '--scale', '2'],
                capture_output=True, text=True, timeout=60,
                shell=True
            )
            
            if os.path.exists(png_file):
                size = os.path.getsize(png_file)
                print(f"    ✅ {png_file} ({size:,} bytes)")
                d['png_path'] = png_file
                rendered.append(d)
            else:
                print(f"    ❌ Failed: {result.stderr[:200] if result.stderr else 'no output'}")
                d['png_path'] = None
        except subprocess.TimeoutExpired:
            print(f"    ❌ Timeout")
            d['png_path'] = None
        except Exception as e:
            print(f"    ❌ Error: {e}")
            d['png_path'] = None
    
    return rendered

if __name__ == '__main__':
    print("=" * 60)
    print("Mermaid Diagram Extractor & Renderer")
    print("=" * 60)
    
    # Extract
    print(f"\n📊 Extracting Mermaid blocks from {INPUT_MD}...")
    diagrams = extract_mermaid_blocks(INPUT_MD)
    print(f"   Found {len(diagrams)} Mermaid diagrams\n")
    
    for d in diagrams:
        print(f"  {d['index']}. {d['name']}")
    
    # Render
    print(f"\n🎨 Rendering diagrams to PNG...")
    rendered = render_diagrams(diagrams, DIAGRAMS_DIR)
    
    print(f"\n✅ Rendered {len(rendered)}/{len(diagrams)} diagrams to {DIAGRAMS_DIR}/")
