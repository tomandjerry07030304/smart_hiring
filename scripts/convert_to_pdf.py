"""
Convert Markdown Documentation to PDF format using reportlab
"""
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

def convert_md_to_pdf(md_file, output_dir="Documentation_Package_PDF"):
    """Convert markdown file to PDF with professional formatting"""
    print(f"Converting {md_file} to PDF...")
    
    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Output file path
    output_file = os.path.join(output_dir, os.path.basename(md_file).replace('.md', '.pdf'))
    
    # Create PDF document
    doc = SimpleDocTemplate(
        output_file,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#34495e'),
        spaceAfter=10,
        spaceBefore=10
    )
    
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=HexColor('#7f8c8d'),
        spaceAfter=8,
        spaceBefore=8
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=HexColor('#2c3e50'),
        spaceAfter=6,
        alignment=TA_JUSTIFY
    )
    
    code_style = ParagraphStyle(
        'CustomCode',
        parent=styles['Code'],
        fontSize=8,
        textColor=HexColor('#c7254e'),
        backColor=HexColor('#f9f2f4'),
        leftIndent=20,
        spaceAfter=6
    )
    
    # Parse markdown and add to PDF
    lines = md_content.split('\n')
    in_code_block = False
    code_block_lines = []
    first_heading = True
    
    for line in lines:
        line = line.rstrip()
        
        # Handle code blocks
        if line.startswith('```'):
            if in_code_block:
                # End of code block
                code_text = '\n'.join(code_block_lines)
                if code_text.strip():
                    elements.append(Preformatted(code_text, code_style))
                    elements.append(Spacer(1, 0.2*inch))
                code_block_lines = []
                in_code_block = False
            else:
                # Start of code block
                in_code_block = True
            continue
        
        if in_code_block:
            code_block_lines.append(line)
            continue
        
        # Skip empty lines
        if not line:
            elements.append(Spacer(1, 0.1*inch))
            continue
        
        try:
            # Handle headers
            if line.startswith('# '):
                if first_heading:
                    elements.append(Paragraph(line[2:], title_style))
                    first_heading = False
                else:
                    elements.append(PageBreak())
                    elements.append(Paragraph(line[2:], heading1_style))
            elif line.startswith('## '):
                elements.append(Paragraph(line[3:], heading1_style))
            elif line.startswith('### '):
                elements.append(Paragraph(line[4:], heading2_style))
            elif line.startswith('#### '):
                elements.append(Paragraph(line[5:], heading3_style))
            
            # Handle bullet points
            elif line.startswith('- ') or line.startswith('* '):
                text = '• ' + line[2:]
                elements.append(Paragraph(text, body_style))
            
            # Handle numbered lists
            elif len(line) > 2 and line[0].isdigit() and line[1:3] in ['. ', ') ']:
                elements.append(Paragraph(line, body_style))
            
            # Handle bold text
            elif '**' in line:
                # Simple bold replacement
                formatted_line = line.replace('**', '<b>', 1)
                formatted_line = formatted_line.replace('**', '</b>', 1)
                while '**' in formatted_line:
                    formatted_line = formatted_line.replace('**', '<b>', 1)
                    formatted_line = formatted_line.replace('**', '</b>', 1)
                elements.append(Paragraph(formatted_line, body_style))
            
            # Handle inline code
            elif '`' in line:
                formatted_line = line.replace('`', '<font color="#c7254e"><i>', 1)
                formatted_line = formatted_line.replace('`', '</i></font>', 1)
                while '`' in formatted_line:
                    formatted_line = formatted_line.replace('`', '<font color="#c7254e"><i>', 1)
                    formatted_line = formatted_line.replace('`', '</i></font>', 1)
                elements.append(Paragraph(formatted_line, body_style))
            
            # Regular paragraph
            else:
                if line.strip():
                    elements.append(Paragraph(line, body_style))
        
        except Exception as e:
            # If formatting fails, add as plain text
            try:
                elements.append(Paragraph(line.replace('<', '&lt;').replace('>', '&gt;'), body_style))
            except:
                pass
    
    # Build PDF
    doc.build(elements)
    print(f"✅ Created: {output_file}")
    return output_file

def main():
    """Convert all 7 documentation files to PDF"""
    docs = [
        "COMPLETE_PROJECT_ANALYSIS_AND_DOCUMENTATION.md",
        "QUICK_REFERENCE_GUIDE.md",
        "PROJECT_ANALYSIS_SUMMARY_FOR_FACULTY.md",
        "ARCHITECTURE_DIAGRAMS.md",
        "DOCUMENTATION_INDEX.md",
        "DETAILED_CODE_ANALYSIS_APPENDIX.md",
        "TESTING_AND_DEPLOYMENT_GUIDE.md"
    ]
    
    # Create output directory
    output_dir = "Documentation_Package_PDF"
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("Converting Documentation to PDF Format")
    print("=" * 60)
    
    converted_files = []
    for doc in docs:
        if os.path.exists(doc):
            try:
                output_file = convert_md_to_pdf(doc, output_dir)
                converted_files.append(output_file)
            except Exception as e:
                print(f"❌ Error converting {doc}: {str(e)}")
        else:
            print(f"⚠️ File not found: {doc}")
    
    print("\n" + "=" * 60)
    print(f"✅ Conversion Complete! {len(converted_files)}/{len(docs)} files converted")
    print(f"📁 Output directory: {os.path.abspath(output_dir)}")
    print("=" * 60)
    
    # Create ZIP archive
    import zipfile
    zip_name = "Smart_Hiring_Documentation_PDF.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in converted_files:
            zipf.write(file, os.path.basename(file))
    
    file_size = os.path.getsize(zip_name) / 1024
    print(f"\n📦 Created ZIP archive: {zip_name}")
    print(f"📊 Size: {file_size:.1f} KB")

if __name__ == "__main__":
    main()
