"""
Real-World Stress Test for Resume Parser v4.1
=============================================
Tests 3 real PDF resumes + 1 BYPASS RESUME designed to trick the parser.
"""
import os
import sys
import time
sys.path.insert(0, '.')

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from backend.services.resume_parser_service import get_resume_parser

# ==============================================================================
# CANDIDATE A: Silicon Valley Engineer (Overlap Test)
# ==============================================================================
def create_silicon_valley_resume(filename):
    c = canvas.Canvas(filename, pagesize=LETTER)
    c.drawString(100, 750, "Jordan Smith")
    c.drawString(100, 735, "jordan.smith@gmail.com | +1-415-555-0199 | San Francisco, CA")

    c.drawString(100, 700, "PROFESSIONAL EXPERIENCE")
    c.line(100, 695, 500, 695)

    c.drawString(100, 675, "Senior Software Engineer | Google")
    c.drawString(400, 675, "Jan 2020 - Present")
    c.drawString(100, 660, "- Architected distributed systems using Go and Kubernetes.")
    c.drawString(100, 645, "- Led migration of monolith to microservices on GCP.")

    c.drawString(100, 615, "Technical Advisor | Startup Inc.")
    c.drawString(400, 615, "Jan 2021 - Present")
    c.drawString(100, 600, "- Advised on scalability and database sharding.")

    c.drawString(100, 570, "Software Engineer | Facebook (Meta)")
    c.drawString(400, 570, "Jan 2017 - Dec 2019")
    c.drawString(100, 555, "- Built React frontend for internal tools.")

    c.drawString(100, 520, "SKILLS")
    c.line(100, 515, 500, 515)
    c.drawString(100, 500, "Languages: Python, Go, Java, C++")
    c.drawString(100, 485, "Tech: Kubernetes, Docker, AWS, GCP, React, TensorFlow")

    c.drawString(100, 450, "EDUCATION")
    c.line(100, 445, 500, 445)
    c.drawString(100, 430, "M.S. Computer Science, Stanford University (2016)")
    c.save()
    print(f"  Generated: {filename}")

# ==============================================================================
# CANDIDATE B: Bangalore Developer (Indian PII Test)
# ==============================================================================
def create_bangalore_resume(filename):
    c = canvas.Canvas(filename, pagesize=LETTER)
    c.drawString(100, 750, "Rahul Sharma")
    c.drawString(100, 735, "rahul.dev@email.com | +91 98765 43210 | Bangalore, India")
    c.drawString(100, 720, "DOB: 15/08/1995 | Nationality: Indian | Marital Status: Single")

    c.drawString(100, 690, "SUMMARY")
    c.drawString(100, 675, "Full Stack Developer with 5 years of experience in MERN stack.")

    c.drawString(100, 650, "EXPERIENCE")
    c.line(100, 645, 500, 645)
    c.drawString(100, 630, "Lead Developer | Tech Mahindra")
    c.drawString(400, 630, "June 2021 - Present")
    c.drawString(100, 615, "- Managing a team of 10 developers.")
    c.drawString(100, 600, "- Developed Fintech app using Node.js and MongoDB.")

    c.drawString(100, 570, "Software Engineer | Infosys")
    c.drawString(400, 570, "May 2018 - May 2021")
    c.drawString(100, 555, "- Worked on Java Spring Boot backend services.")

    c.drawString(100, 520, "PROJECTS")
    c.line(100, 515, 500, 515)
    c.drawString(100, 500, "- Smart Hiring System (Python, Flask, React)")
    c.drawString(100, 485, "- E-commerce Platform (MERN Stack, Redis)")

    c.drawString(100, 450, "EDUCATION")
    c.line(100, 445, 500, 445)
    c.drawString(100, 430, "B.Tech Computer Science, IIT Bombay (2018)")
    c.save()
    print(f"  Generated: {filename}")

# ==============================================================================
# CANDIDATE C: Messy/Creative Resume (Stress Test)
# ==============================================================================
def create_messy_resume(filename):
    c = canvas.Canvas(filename, pagesize=LETTER)
    c.drawString(50, 750, "CREATIVE DESIGNER / ALEX TAYLOR")
    c.drawString(50, 730, "contact: alex@design.io phone: 555-0102")

    c.drawString(50, 680, "I make things look good.")
    c.drawString(50, 660, "Tools I use: Figma, Adobe XD, Sketch, Photoshop, Illustrator")

    c.drawString(300, 680, "WORK HISTORY")
    c.drawString(300, 660, "Senior Designer @ Apple")
    c.drawString(300, 645, "2019 - 2023")
    c.drawString(300, 630, "Redesigned the App Store interface.")

    c.drawString(50, 550, "Freelance")
    c.drawString(50, 535, "2015 - 2019")
    c.drawString(50, 520, "Web design for various startups.")
    c.save()
    print(f"  Generated: {filename}")

# ==============================================================================
# CANDIDATE D: THE BYPASS RESUME (Adversarial Attack)
# ==============================================================================
def create_bypass_resume(filename):
    """
    This resume is DESIGNED to exploit parser weaknesses:
    
    Attack 1: INVISIBLE SKILL STUFFING
      - White text (invisible to humans) packed with 50+ skills
      - Tests if parser blindly trusts extracted text
    
    Attack 2: FAKE EXPERIENCE INFLATION
      - Claims "15+ years of experience" in text
      - But date ranges only show 2 years of actual work
      - Tests if parser trusts keywords over computed dates
    
    Attack 3: HOBBIES SKILL INJECTION
      - Skills hidden in HOBBIES section to bypass context-aware filter
      - Uses synonyms: "INTERESTS" instead of "HOBBIES"
    
    Attack 4: CONFIDENCE GAMING
      - Perfect formatting to maximize confidence score
      - But the content is fabricated
    """
    c = canvas.Canvas(filename, pagesize=LETTER)

    # Normal visible header
    c.drawString(100, 750, "Eva Phantom")
    c.drawString(100, 735, "eva.phantom@email.com | +1-555-000-0000")

    c.drawString(100, 700, "SUMMARY")
    c.drawString(100, 685, "Visionary tech leader with 15+ years of experience in AI, ML,")
    c.drawString(100, 670, "blockchain, IoT, quantum computing, and cloud architecture.")

    # ATTACK 1: Invisible skill stuffing (white text on white background)
    c.setFillColorRGB(1, 1, 1)  # WHITE text - invisible on screen/print
    c.drawString(100, 50, "kubernetes docker terraform ansible puppet chef aws azure gcp")
    c.drawString(100, 35, "react angular vue svelte django flask fastapi spring express")
    c.drawString(100, 20, "tensorflow pytorch keras scikit-learn pandas numpy opencv")
    c.drawString(100, 5, "blockchain ethereum solidity web3 defi nft smart contracts")
    c.setFillColorRGB(0, 0, 0)  # Back to black

    c.drawString(100, 640, "SKILLS")
    c.line(100, 635, 500, 635)
    c.drawString(100, 620, "Python, JavaScript, SQL")  # Only 3 REAL skills

    c.drawString(100, 590, "EXPERIENCE")
    c.line(100, 585, 500, 585)
    # ATTACK 2: Only 2 years of actual work
    c.drawString(100, 570, "Junior Developer | Small Corp")
    c.drawString(400, 570, "Jan 2022 - Dec 2023")
    c.drawString(100, 555, "- Built basic CRUD applications.")

    c.drawString(100, 520, "PROJECTS")
    c.line(100, 515, 500, 515)
    c.drawString(100, 500, "- Todo App (HTML, CSS)")
    c.drawString(100, 485, "- Calculator (Python)")

    c.drawString(100, 450, "EDUCATION")
    c.line(100, 445, 500, 445)
    c.drawString(100, 430, "B.S. Computer Science, Generic University (2021)")

    # ATTACK 3: Skills in Interests section (should be filtered)
    c.drawString(100, 400, "INTERESTS")
    c.line(100, 395, 500, 395)
    c.drawString(100, 380, "Machine Learning, Deep Learning, Kubernetes orchestration,")
    c.drawString(100, 365, "Docker containerization, AWS cloud architecture, TensorFlow")

    c.drawString(100, 330, "CERTIFICATIONS")
    c.drawString(100, 315, "AWS Certified Solutions Architect")
    c.drawString(100, 300, "Google Cloud Professional Data Engineer")

    c.drawString(100, 270, "LANGUAGES")
    c.drawString(100, 255, "English - Fluent")
    c.drawString(100, 240, "Spanish - Intermediate")

    c.save()
    print(f"  Generated: {filename}")

# ==============================================================================
# THE TEST ENGINE
# ==============================================================================
def run_real_world_test():
    parser = get_resume_parser()

    files = {
        "candidate_A.pdf": create_silicon_valley_resume,
        "candidate_B.pdf": create_bangalore_resume,
        "candidate_C.pdf": create_messy_resume,
        "candidate_D_BYPASS.pdf": create_bypass_resume,
    }

    print("\n" + "=" * 70)
    print(f"  DEPLOYING v4.1 PARSER ON {len(files)} REAL-WORLD SCENARIOS")
    print("=" * 70)

    for filename, creator_func in files.items():
        creator_func(filename)

        with open(filename, "rb") as f:
            file_bytes = f.read()

        start_time = time.time()
        result = parser.parse_resume(file_bytes, filename)
        duration = round(time.time() - start_time, 2)

        print(f"\n{'=' * 70}")
        if "BYPASS" in filename:
            print(f"  ADVERSARIAL REPORT: {filename} ({duration}s)")
        else:
            print(f"  REPORT: {filename} ({duration}s)")
        print(f"{'=' * 70}")

        # --- Version ---
        print(f"  Parser Version: {result.get('parser_version', 'unknown')}")

        # --- PII / Anonymization ---
        anon = result.get('anonymized_text', '')
        email_ok = '[EMAIL]' in anon
        phone_ok = '[PHONE]' in anon
        print(f"  Anonymization: Email={'PASS' if email_ok else 'FAIL'} | Phone={'PASS' if phone_ok else 'FAIL'}")

        if "candidate_B" in filename:
            nat_ok = '[NATIONALITY]' in anon
            mar_ok = '[MARITAL]' in anon
            dob_ok = '[DOB]' in anon or '[DATE]' in anon
            print(f"    Indian PII: DOB={'PASS' if dob_ok else 'FAIL'} | Nationality={'PASS' if nat_ok else 'FAIL'} | Marital={'PASS' if mar_ok else 'FAIL'}")

        # --- Skills ---
        skills = result.get('skills', [])
        ca_skills = result.get('skills_context_aware', [])
        skill_names = [s['name'] if isinstance(s, dict) else s for s in skills]
        ca_skill_names = [s['name'] if isinstance(s, dict) else s for s in ca_skills]
        print(f"  Skills (total): {len(skills)}")
        print(f"    Top 5: {skill_names[:5]}")
        print(f"  Skills (context-aware): {len(ca_skills)}")

        if "BYPASS" in filename:
            # Check if invisible skills got picked up
            invisible_stuffed = sum(1 for s in skill_names if s.lower() in ['terraform', 'ansible', 'puppet', 'chef', 'svelte'])
            print(f"    ATTACK 1 - Invisible Skill Stuffing: {'BLOCKED' if invisible_stuffed <= 2 else 'BYPASSED (' + str(invisible_stuffed) + ' stuffed skills found)'}")
            # Check if HOBBIES/INTERESTS skills leaked
            ca_sections = set(s.get('section', '') for s in ca_skills if isinstance(s, dict))
            interests_leaked = 'interests' in ca_sections
            print(f"    ATTACK 3 - Interests Skill Injection: {'BLOCKED' if not interests_leaked else 'BYPASSED (skills from interests leaked)'}")

        # --- Experience ---
        exp_data = result.get('experience', {})
        exp_years = exp_data.get('total_years', 0) if isinstance(exp_data, dict) else 0
        print(f"  Experience: {exp_years} years")

        if "candidate_A" in filename:
            # 2017-Present ~9 years, but 2020-Present and 2021-Present overlap
            # Correct: ~8 years (2017-2019: 3yrs + 2020-Present: ~6yrs with overlap merged)
            verdict = "OVERLAP HANDLED" if exp_years <= 9 else "DOUBLE-COUNTED"
            print(f"    Overlap Test: {verdict}")
        elif "BYPASS" in filename:
            # Claims 15+ years but only has 2 years of real dates
            if exp_years >= 10:
                print(f"    ATTACK 2 - Fake Experience: BYPASSED (parser believed '15 years' claim)")
            else:
                print(f"    ATTACK 2 - Fake Experience: BLOCKED (computed {exp_years} from dates)")

        # --- Projects ---
        projects = result.get('projects', [])
        print(f"  Projects: {len(projects)}")
        for proj in projects[:3]:
            if isinstance(proj, dict):
                print(f"    - {proj.get('name', 'N/A')} | Tech: {proj.get('tech_stack', [])}")

        # --- Confidence ---
        conf = result.get('confidence', {})
        overall = conf.get('overall', 0)
        print(f"  Confidence: {overall}")

        if "BYPASS" in filename:
            if overall >= 0.7:
                print(f"    ATTACK 4 - Confidence Gaming: BYPASSED (high confidence on fake resume!)")
            else:
                print(f"    ATTACK 4 - Confidence Gaming: BLOCKED (low confidence = suspicious)")

        # --- Sections ---
        sections = list(result.get('sections', {}).keys())
        print(f"  Sections Detected: {sections}")

    # Final Summary
    print("\n" + "=" * 70)
    print("  TEST COMPLETE")
    print("=" * 70)

    # Cleanup
    for f in files.keys():
        if os.path.exists(f):
            os.remove(f)
    print("  Cleaned up generated PDFs.")


if __name__ == "__main__":
    run_real_world_test()
