from docx2pdf import convert
import os

convert('PROJECT_DOCUMENTATION.docx', 'PROJECT_DOCUMENTATION.pdf')
size = os.path.getsize('PROJECT_DOCUMENTATION.pdf')
print(f'PDF generated: {size:,} bytes')
