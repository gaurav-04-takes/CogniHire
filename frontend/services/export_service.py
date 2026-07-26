"""
Frontend Export Service.

Architectural layer:
    Frontend (Utility/Service).

Purpose:
    Provides functionality to generate downloadable PDF reports from structured
    AI analysis data (match scores, skill gaps, ATS keywords).
"""
import json
from fpdf import FPDF
import tempfile
import os

class ExportService:
    """
    Utility class for transforming JSON analysis data into formatted PDF documents.
    """
    
    @staticmethod
    def generate_pdf_report(data: dict) -> bytes:
        """
        Generates a PDF report containing match scores, skill gaps, and ATS analysis.
        Returns the PDF as raw bytes suitable for Streamlit download buttons.
        """
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        
        pdf.cell(0, 10, "CogniHire Analysis Report", ln=True, align="C")
        pdf.ln(10)
        
        pdf.set_font("Arial", "B", 12)
        
        if "match" in data:
            match_data = data["match"]
            pdf.cell(0, 10, "Match Score Analysis", ln=True)
            pdf.set_font("Arial", "", 11)
            pdf.cell(0, 8, f"Overall Score: {match_data.get('overall_score', 0)}%", ln=True)
            pdf.multi_cell(0, 8, f"Explanation: {match_data.get('explanation', '')}")
            pdf.ln(5)
            
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Dimension Breakdown", ln=True)
            pdf.set_font("Arial", "", 11)
            for dim in ["skills", "experience", "education", "keywords"]:
                d_data = match_data.get(dim, {})
                pdf.cell(0, 8, f"{dim.capitalize()}: {d_data.get('score', 0)}%", ln=True)
            pdf.ln(10)
            
        if "skills" in data:
            skills_data = data["skills"]
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Skill Gap Analysis", ln=True)
            pdf.set_font("Arial", "", 11)
            
            missing = skills_data.get("missing_skills", [])
            if missing:
                pdf.cell(0, 8, "Missing Skills:", ln=True)
                for ms in missing:
                    pdf.cell(0, 8, f"- {ms.get('skill', 'Unknown')}: {ms.get('impact', 'Unknown')}", ln=True)
            else:
                pdf.cell(0, 8, "No missing skills detected.", ln=True)
            pdf.ln(10)
            
        if "ats" in data:
            ats_data = data["ats"]
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "ATS Analysis", ln=True)
            pdf.set_font("Arial", "", 11)
            
            missing_kw = ats_data.get("missing_keywords", [])
            pdf.cell(0, 8, "Missing Keywords:", ln=True)
            for kw in missing_kw:
                pdf.cell(0, 8, f"- {kw}", ln=True)
                
        # Save to temp and read
        fd, temp_path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        
        pdf.output(temp_path)
        
        with open(temp_path, "rb") as f:
            pdf_bytes = f.read()
            
        os.remove(temp_path)
        
        return pdf_bytes
