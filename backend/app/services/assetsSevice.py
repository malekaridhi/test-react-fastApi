import logging
from typing import Dict, Any, Optional
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
import json

logger = logging.getLogger(__name__)

class AssetService:
    """Service for generating downloadable assets (PDFs, templates, etc.)"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#6366f1'),
            spaceAfter=30,
        ))
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#4f46e5'),
            spaceAfter=12,
        ))
    
    def generate_checklist_pdf(self, lead_magnet: Dict[str, Any]) -> BytesIO:
        """Generate a PDF checklist"""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            story = []
            
            # Title
            title = Paragraph(lead_magnet.get('title', 'Checklist'), self.styles['CustomTitle'])
            story.append(title)
            story.append(Spacer(1, 0.2*inch))
            
            # Value Promise
            if lead_magnet.get('value_promise'):
                intro = Paragraph(lead_magnet['value_promise'], self.styles['BodyText'])
                story.append(intro)
                story.append(Spacer(1, 0.3*inch))
            
            # Checklist Steps
            content = lead_magnet.get('content', {})
            steps = content.get('steps', [])
            
            if steps:
                for step in steps:
                    # Step title with checkbox
                    step_title = f"☐ {step.get('title', 'Step')}"
                    step_para = Paragraph(step_title, self.styles['CustomHeading'])
                    story.append(step_para)
                    
                    # Step description
                    desc = step.get('description', '')
                    desc_para = Paragraph(desc, self.styles['BodyText'])
                    story.append(desc_para)
                    
                    # Time estimate if available
                    if step.get('time_estimate'):
                        time_para = Paragraph(
                            f"<i>⏱ Estimated time: {step['time_estimate']}</i>",
                            self.styles['BodyText']
                        )
                        story.append(time_para)
                    
                    story.append(Spacer(1, 0.2*inch))
            
            doc.build(story)
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            logger.error(f"Error generating checklist PDF: {str(e)}")
            raise
    
    def generate_template_file(self, lead_magnet: Dict[str, Any]) -> BytesIO:
        """Generate a template document"""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            story = []
            
            # Title
            title = Paragraph(lead_magnet.get('title', 'Template'), self.styles['CustomTitle'])
            story.append(title)
            story.append(Spacer(1, 0.2*inch))
            
            # Content
            content = lead_magnet.get('content', {})
            template_content = content.get('content', '')
            
            # Split by sections if available
            sections = content.get('sections', [])
            if sections and template_content:
                for section in sections:
                    section_para = Paragraph(section, self.styles['CustomHeading'])
                    story.append(section_para)
                    story.append(Spacer(1, 0.1*inch))
            
            # Add main content
            if template_content:
                for line in template_content.split('\n'):
                    if line.strip():
                        para = Paragraph(line, self.styles['BodyText'])
                        story.append(para)
                        story.append(Spacer(1, 0.1*inch))
            
            doc.build(story)
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            logger.error(f"Error generating template file: {str(e)}")
            raise
    
    def generate_report_pdf(self, lead_magnet: Dict[str, Any]) -> BytesIO:
        """Generate a report PDF"""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            story = []
            
            # Title
            title = Paragraph(lead_magnet.get('title', 'Report'), self.styles['CustomTitle'])
            story.append(title)
            story.append(Spacer(1, 0.3*inch))
            
            # Executive Summary
            content = lead_magnet.get('content', {})
            sections = content.get('sections', [])
            
            for section in sections:
                section_title = section.get('title', '')
                section_content = section.get('content', '')
                
                # Section heading
                heading = Paragraph(section_title, self.styles['CustomHeading'])
                story.append(heading)
                story.append(Spacer(1, 0.1*inch))
                
                # Section content
                para = Paragraph(section_content, self.styles['BodyText'])
                story.append(para)
                story.append(Spacer(1, 0.2*inch))
            
            doc.build(story)
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            logger.error(f"Error generating report PDF: {str(e)}")
            raise
    
    def generate_calculator_html(self, lead_magnet: Dict[str, Any]) -> str:
        """Generate HTML for an interactive calculator"""
        content = lead_magnet.get('content', {})
        inputs = content.get('inputs', [])
        formula = content.get('formula', '')
        output = content.get('output', {})
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{lead_magnet.get('title', 'Calculator')}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .calculator {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #6366f1;
            margin-bottom: 10px;
        }}
        .input-group {{
            margin: 20px 0;
        }}
        label {{
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }}
        input {{
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }}
        button {{
            background: #6366f1;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
            margin-top: 20px;
        }}
        button:hover {{
            background: #4f46e5;
        }}
        .result {{
            margin-top: 20px;
            padding: 20px;
            background: #f0fdf4;
            border-left: 4px solid #22c55e;
            border-radius: 5px;
            display: none;
        }}
        .result h2 {{
            margin: 0 0 10px 0;
            color: #15803d;
        }}
        .result-value {{
            font-size: 32px;
            font-weight: bold;
            color: #15803d;
        }}
    </style>
</head>
<body>
    <div class="calculator">
        <h1>{lead_magnet.get('title', 'Calculator')}</h1>
        <p>{lead_magnet.get('value_promise', '')}</p>
        
        <form id="calculatorForm">
"""
        
        # Add input fields
        for inp in inputs:
            html += f"""
            <div class="input-group">
                <label for="{inp.get('name', '')}">{inp.get('label', '')}</label>
                <input 
                    type="{inp.get('type', 'number')}" 
                    id="{inp.get('name', '')}" 
                    name="{inp.get('name', '')}"
                    placeholder="{inp.get('placeholder', '')}"
                    required
                >
            </div>
"""
        
        html += f"""
            <button type="submit">Calculate</button>
        </form>
        
        <div class="result" id="result">
            <h2>{output.get('label', 'Result')}</h2>
            <div class="result-value" id="resultValue"></div>
        </div>
    </div>
    
    <script>
        document.getElementById('calculatorForm').addEventListener('submit', function(e) {{
            e.preventDefault();
            
            // Get input values
"""
        
        for inp in inputs:
            html += f"""
            const {inp.get('name', '')} = parseFloat(document.getElementById('{inp.get('name', '')}').value);
"""
        
        # Simple formula evaluation (you might want to make this more robust)
        html += f"""
            
            // Calculate result
            const result = {formula.replace('=', '').strip() if formula else '0'};
            
            // Display result
            const unit = "{output.get('unit', '')}";
            document.getElementById('resultValue').textContent = unit + result.toFixed(2);
            document.getElementById('result').style.display = 'block';
        }});
    </script>
</body>
</html>
"""
        return html
    
    def generate_asset(self, lead_magnet: Dict[str, Any], format: str = "pdf") -> BytesIO:
        """Generate asset based on lead magnet type"""
        lead_type = lead_magnet.get('type', 'checklist')
        
        if lead_type == 'checklist':
            return self.generate_checklist_pdf(lead_magnet)
        elif lead_type == 'template':
            return self.generate_template_file(lead_magnet)
        elif lead_type == 'report':
            return self.generate_report_pdf(lead_magnet)
        elif lead_type == 'calculator':
            # Return HTML as bytes for calculator
            html = self.generate_calculator_html(lead_magnet)
            buffer = BytesIO(html.encode('utf-8'))
            return buffer
        else:
            raise ValueError(f"Unknown lead magnet type: {lead_type}")