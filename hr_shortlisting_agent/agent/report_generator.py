"""
Report generator for creating JSON, HTML, and PDF shortlist reports.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path

from jinja2 import Template
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates JSON, HTML, and PDF shortlist reports from ranked scored candidates.
    """

    def __init__(self, output_dir: str):
        """
        Initialize report generator with output directory.

        Args:
            output_dir: Directory where reports will be saved.
        """
        self.output_dir = output_dir
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        logger.info(f"Report output directory: {self.output_dir}")

    def generate_json(self, ranked_results: list, filename: str = "shortlist_report.json") -> str:
        """
        Generate a JSON report of ranked candidates.

        Args:
            ranked_results: List of ranked and scored candidate dicts.
            filename: Name of the output JSON file.

        Returns:
            Full path to the generated JSON file.
        """
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(ranked_results, f, indent=2)

        logger.info(f"JSON report generated: {filepath}")
        return filepath

    def generate_html(
        self,
        ranked_results: list,
        jd_dict: dict,
        filename: str = "shortlist_report.html",
    ) -> str:
        """
        Generate an HTML report with styled table and expandable candidate details.

        Args:
            ranked_results: List of ranked and scored candidate dicts.
            jd_dict: Job description dict.
            filename: Name of the output HTML file.

        Returns:
            Full path to the generated HTML file.
        """
        # Calculate summary statistics
        total = len(ranked_results)
        hire_count = sum(1 for r in ranked_results if r.get("hire_recommendation") == "Hire")
        maybe_count = sum(1 for r in ranked_results if r.get("hire_recommendation") == "Maybe")
        no_hire_count = sum(1 for r in ranked_results if r.get("hire_recommendation") == "No Hire")

        # Build candidate rows
        candidate_details = []
        for result in ranked_results:
            rank = result.get("rank", "N/A")
            candidate = result.get("candidate", {})
            name = candidate.get("name", "Unknown")
            skills_score = result.get("skills_match", {}).get("score", 0)
            skills_justification = result.get("skills_match", {}).get("justification", "")
            experience_score = result.get("experience_relevance", {}).get("score", 0)
            experience_justification = result.get("experience_relevance", {}).get("justification", "")
            education_score = result.get("education_certs", {}).get("score", 0)
            education_justification = result.get("education_certs", {}).get("justification", "")
            project_score = result.get("project_portfolio", {}).get("score", 0)
            project_justification = result.get("project_portfolio", {}).get("justification", "")
            comms_score = result.get("communication_quality", {}).get("score", 0)
            comms_justification = result.get("communication_quality", {}).get("justification", "")
            total_score = result.get("weighted_total", 0)
            recommendation = result.get("hire_recommendation", "N/A")

            # Color coding for recommendation
            if recommendation == "Hire":
                badge_color = "#28a745"
                badge_text = "✓ Hire"
            elif recommendation == "Maybe":
                badge_color = "#ffc107"
                badge_text = "⚠ Maybe"
            else:
                badge_color = "#dc3545"
                badge_text = "✗ No Hire"

            candidate_html = f"""
            <tr>
                <td class="rank">{rank}</td>
                <td class="name">{name}</td>
                <td class="score">{skills_score}</td>
                <td class="score">{experience_score}</td>
                <td class="score">{education_score}</td>
                <td class="score">{project_score}</td>
                <td class="score">{comms_score}</td>
                <td class="score"><strong>{total_score}</strong></td>
                <td class="recommendation" style="background-color: {badge_color}; color: white;">{badge_text}</td>
            </tr>
            <tr class="details-row">
                <td colspan="9">
                    <details>
                        <summary>View Justifications</summary>
                        <div class="justifications">
                            <p><strong>Skills Match ({skills_score}/10):</strong> {skills_justification}</p>
                            <p><strong>Experience Relevance ({experience_score}/10):</strong> {experience_justification}</p>
                            <p><strong>Education & Certs ({education_score}/10):</strong> {education_justification}</p>
                            <p><strong>Project Portfolio ({project_score}/10):</strong> {project_justification}</p>
                            <p><strong>Communication Quality ({comms_score}/10):</strong> {comms_justification}</p>
                        </div>
                    </details>
                </td>
            </tr>
            """
            candidate_details.append(candidate_html)

        # Build HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>HR Shortlist Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                    color: #333;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    border-bottom: 3px solid #007bff;
                    padding-bottom: 20px;
                    margin-bottom: 20px;
                }}
                .header h1 {{
                    margin: 0;
                    color: #007bff;
                    font-size: 28px;
                }}
                .header .timestamp {{
                    color: #666;
                    font-size: 12px;
                    margin-top: 5px;
                }}
                .summary {{
                    display: grid;
                    grid-template-columns: repeat(4, 1fr);
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .summary-card {{
                    text-align: center;
                    padding: 20px;
                    border-radius: 5px;
                    background-color: #f9f9f9;
                    border: 1px solid #ddd;
                }}
                .summary-card .number {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #007bff;
                }}
                .summary-card .label {{
                    font-size: 14px;
                    color: #666;
                    margin-top: 10px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                    font-size: 13px;
                }}
                table th {{
                    background-color: #007bff;
                    color: white;
                    padding: 12px;
                    text-align: left;
                    border: 1px solid #ddd;
                }}
                table td {{
                    padding: 10px;
                    border: 1px solid #ddd;
                }}
                table tr:nth-child(odd) {{
                    background-color: #f9f9f9;
                }}
                table tr:hover {{
                    background-color: #f0f0f0;
                }}
                .rank {{
                    font-weight: bold;
                    text-align: center;
                    width: 40px;
                }}
                .score {{
                    text-align: center;
                    width: 50px;
                }}
                .name {{
                    font-weight: 500;
                }}
                .recommendation {{
                    text-align: center;
                    font-weight: bold;
                    border-radius: 3px;
                }}
                .details-row {{
                    background-color: #f5f5f5 !important;
                }}
                .details-row td {{
                    padding: 15px;
                }}
                details {{
                    cursor: pointer;
                }}
                details summary {{
                    color: #007bff;
                    font-weight: bold;
                    outline: none;
                }}
                details summary:hover {{
                    text-decoration: underline;
                }}
                .justifications {{
                    margin-top: 10px;
                    padding: 10px;
                    background-color: white;
                    border-radius: 3px;
                }}
                .justifications p {{
                    margin: 5px 0;
                    font-size: 12px;
                    line-height: 1.4;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 HR Shortlist Report — {jd_dict.get("job_title", "Position")}</h1>
                    <div class="timestamp">Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
                </div>

                <div class="summary">
                    <div class="summary-card">
                        <div class="number">{total}</div>
                        <div class="label">Total Candidates Screened</div>
                    </div>
                    <div class="summary-card">
                        <div class="number" style="color: #28a745;">{hire_count}</div>
                        <div class="label">Hire ✓</div>
                    </div>
                    <div class="summary-card">
                        <div class="number" style="color: #ffc107;">{maybe_count}</div>
                        <div class="label">Maybe ⚠</div>
                    </div>
                    <div class="summary-card">
                        <div class="number" style="color: #dc3545;">{no_hire_count}</div>
                        <div class="label">No Hire ✗</div>
                    </div>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Candidate Name</th>
                            <th>Skills</th>
                            <th>Experience</th>
                            <th>Education</th>
                            <th>Projects</th>
                            <th>Comms</th>
                            <th><strong>Total</strong></th>
                            <th>Recommendation</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(candidate_details)}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """

        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"HTML report generated: {filepath}")
        return filepath

    def generate_pdf(
        self,
        ranked_results: list,
        jd_dict: dict,
        filename: str = "shortlist_report.pdf",
    ) -> str:
        """
        Generate a PDF report using ReportLab.

        Args:
            ranked_results: List of ranked and scored candidate dicts.
            jd_dict: Job description dict.
            filename: Name of the output PDF file.

        Returns:
            Full path to the generated PDF file.
        """
        filepath = os.path.join(self.output_dir, filename)

        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=20,
            textColor=colors.HexColor("#007bff"),
            spaceAfter=6,
            alignment=TA_CENTER,
        )
        title = Paragraph(f"HR Shortlist Report — {jd_dict.get('job_title', 'Position')}", title_style)
        elements.append(title)

        # Timestamp
        timestamp_style = ParagraphStyle(
            "Timestamp",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.grey,
            alignment=TA_CENTER,
        )
        timestamp = Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", timestamp_style)
        elements.append(timestamp)
        elements.append(Spacer(1, 0.3 * inch))

        # Summary statistics
        total = len(ranked_results)
        hire_count = sum(1 for r in ranked_results if r.get("hire_recommendation") == "Hire")
        maybe_count = sum(1 for r in ranked_results if r.get("hire_recommendation") == "Maybe")
        no_hire_count = sum(1 for r in ranked_results if r.get("hire_recommendation") == "No Hire")

        summary_text = f"""
        <b>Summary:</b><br/>
        Total Candidates Screened: {total}<br/>
        Hire: {hire_count} | Maybe: {maybe_count} | No Hire: {no_hire_count}
        """
        elements.append(Paragraph(summary_text, styles["Normal"]))
        elements.append(Spacer(1, 0.2 * inch))

        # Candidates table
        table_data = [
            [
                "Rank",
                "Name",
                "Skills",
                "Exp.",
                "Edu.",
                "Proj.",
                "Comms",
                "Total",
                "Recommendation",
            ]
        ]

        for result in ranked_results:
            rank = result.get("rank", "")
            candidate = result.get("candidate", {})
            name = candidate.get("name", "Unknown")[:20]  # Truncate for table
            skills = result.get("skills_match", {}).get("score", 0)
            experience = result.get("experience_relevance", {}).get("score", 0)
            education = result.get("education_certs", {}).get("score", 0)
            project = result.get("project_portfolio", {}).get("score", 0)
            comms = result.get("communication_quality", {}).get("score", 0)
            total_score = result.get("weighted_total", 0)
            recommendation = result.get("hire_recommendation", "N/A")

            table_data.append(
                [
                    str(rank),
                    name,
                    str(skills),
                    str(experience),
                    str(education),
                    str(project),
                    str(comms),
                    f"{total_score:.2f}",
                    recommendation,
                ]
            )

        # Create table with styling
        table = Table(table_data, colWidths=[0.5 * inch, 1.5 * inch, 0.6 * inch, 0.6 * inch, 0.6 * inch,
                                              0.6 * inch, 0.6 * inch, 0.7 * inch, 1 * inch])
        table_style = TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#007bff")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]
        )

        # Color recommendation cells
        for i, result in enumerate(ranked_results, start=1):
            recommendation = result.get("hire_recommendation", "N/A")
            if recommendation == "Hire":
                table_style.add("BACKGROUND", (8, i), (8, i), colors.lightgreen)
            elif recommendation == "Maybe":
                table_style.add("BACKGROUND", (8, i), (8, i), colors.lightyellow)
            else:
                table_style.add("BACKGROUND", (8, i), (8, i), colors.lightcoral)

        table.setStyle(table_style)
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))

        # Detailed justifications
        elements.append(Paragraph("<b>Candidate Justifications</b>", styles["Heading2"]))
        elements.append(Spacer(1, 0.1 * inch))

        for result in ranked_results:
            rank = result.get("rank", "")
            candidate = result.get("candidate", {})
            name = candidate.get("name", "Unknown")

            details_text = f"<b>#{rank} — {name}</b><br/>"
            details_text += f"Skills Match: {result.get('skills_match', {}).get('justification', '')}<br/>"
            details_text += f"Experience: {result.get('experience_relevance', {}).get('justification', '')}<br/>"
            details_text += f"Education: {result.get('education_certs', {}).get('justification', '')}<br/>"
            details_text += f"Projects: {result.get('project_portfolio', {}).get('justification', '')}<br/>"
            details_text += f"Communication: {result.get('communication_quality', {}).get('justification', '')}<br/>"

            elements.append(Paragraph(details_text, styles["Normal"]))
            elements.append(Spacer(1, 0.1 * inch))

        # Build PDF
        doc.build(elements)
        logger.info(f"PDF report generated: {filepath}")
        return filepath
