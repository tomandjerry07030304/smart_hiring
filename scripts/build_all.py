"""
build_all.py - Master build script for SMART_HIRING_DETAILS.docx
Integrates all phases (1 through 7.3) into a single comprehensive document.

Usage: python build_all.py
Output: SMART_HIRING_DETAILS.docx in the project root directory.
"""
import sys
import os
import time

# Ensure the project root is in the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from doc_generator.helpers import create_document, add_cover_page, add_toc_placeholder


def build_document():
    """Build the complete SMART_HIRING_DETAILS.docx document."""
    start_time = time.time()
    print("=" * 60)
    print("  SMART_HIRING_DETAILS.docx — Master Build Script")
    print("=" * 60)
    print()

    # Step 1: Create the document with styling
    print("[1/10] Creating document with professional styling...")
    doc = create_document()
    add_cover_page(doc)
    add_toc_placeholder(doc)
    print("       Cover page and table of contents added.")

    # Step 2: Phase 1 — Parts 0-1
    print("[2/10] Phase 1: Executive Overview & System Architecture...")
    from doc_generator.phase1_parts0_1 import add_part0, add_part1
    doc = add_part0(doc)
    doc = add_part1(doc)
    print("       Parts 0-1 complete.")

    # Step 3: Phase 2 — Parts 2-3
    print("[3/10] Phase 2: Flask & MongoDB...")
    from doc_generator.phase2_parts2_3 import add_part2, add_part3
    doc = add_part2(doc)
    doc = add_part3(doc)
    print("       Parts 2-3 complete.")

    # Step 4: Phase 3 — Parts 4-5
    print("[4/10] Phase 3: Redis/Celery & AI/NLP...")
    from doc_generator.phase3_parts4_5 import add_part4, add_part5
    doc = add_part4(doc)
    doc = add_part5(doc)
    print("       Parts 4-5 complete.")

    # Step 5: Phase 4 — Parts 6-7-8
    print("[5/10] Phase 4: Security, File Handling & Assessment Engine...")
    from doc_generator.phase4_parts6_7_8 import add_part6, add_part7, add_part8
    doc = add_part6(doc)
    doc = add_part7(doc)
    doc = add_part8(doc)
    print("       Parts 6-8 complete.")

    # Step 6: Phase 5 — Parts 9-12
    print("[6/10] Phase 5: AI Interview, Video, Analytics & Admin...")
    from doc_generator.phase5_parts9_12 import add_part9, add_part10, add_part11, add_part12
    doc = add_part9(doc)
    doc = add_part10(doc)
    doc = add_part11(doc)
    doc = add_part12(doc)
    print("       Parts 9-12 complete.")

    # Step 7: Phase 6 — Parts 13-16
    print("[7/10] Phase 6: API Design, Data Modeling, DevOps & Error Handling...")
    from doc_generator.phase6_parts13_16 import add_part13, add_part14, add_part15, add_part16
    doc = add_part13(doc)
    doc = add_part14(doc)
    doc = add_part15(doc)
    doc = add_part16(doc)
    print("       Parts 13-16 complete.")

    # Step 8: Phase 7.1 — Parts 17-18
    print("[8/10] Phase 7.1: Testing & Scalability...")
    from doc_generator.phase7_1_parts17_18 import add_part17
    doc = add_part17(doc)  # Part 17 function includes Part 18 content
    print("       Parts 17-18 complete.")

    # Step 9: Phase 7.2 — Parts 19-20
    print("[9/10] Phase 7.2: Ethical AI & Glossary/Cheat Sheet...")
    from doc_generator.phase7_2_parts19_20 import add_part19
    doc = add_part19(doc)  # Part 19 function includes Part 20 content
    print("       Parts 19-20 complete.")

    # Step 10: Phase 7.3 — Special Sections
    print("[10/10] Phase 7.3: Special Sections (Limitations, Roadmap, Maps)...")
    from doc_generator.phase7_3_special import add_special_sections
    doc = add_special_sections(doc)
    print("        Special sections complete.")

    # Save the document
    output_path = os.path.join(project_root, "SMART_HIRING_DETAILS.docx")
    print()
    print(f"Saving document to: {output_path}")
    doc.save(output_path)

    elapsed = time.time() - start_time
    file_size = os.path.getsize(output_path)
    file_size_mb = file_size / (1024 * 1024)

    print()
    print("=" * 60)
    print(f"  BUILD COMPLETE!")
    print(f"  File: SMART_HIRING_DETAILS.docx")
    print(f"  Size: {file_size_mb:.2f} MB")
    print(f"  Time: {elapsed:.1f} seconds")
    print("=" * 60)

    return output_path


if __name__ == "__main__":
    build_document()
