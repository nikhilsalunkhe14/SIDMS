#!/usr/bin/env python3
"""
PDF Export Service for SIDMS - Professional student data export
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io

class PDFExportService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom styles for the PDF with theme matching"""
        # Title style with gradient effect
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            spaceAfter=30,
            spaceBefore=20,
            textColor=colors.whitesmoke,
            alignment=TA_CENTER,
            borderWidth=2,
            borderColor=colors.HexColor('#6366f1'),
            borderPadding=15,
            backColor=colors.HexColor('#1e293b'),
            borderRadius=10
        ))
        
        # Header style with theme color (not selected look)
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=15,
            spaceBefore=25,
            textColor=colors.HexColor('#f1f5f9'),
            borderWidth=0,
            borderBottomWidth=2,
            borderBottomColor=colors.HexColor('#6366f1'),
            backColor=colors.HexColor('#1e293b'),
            padding=10,
            borderRadius=5,
            fontName='Helvetica-Bold'
        ))
        
        # Normal style with better spacing and theme
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            leading=15,
            textColor=colors.HexColor('#e2e8f0'),
            backColor=colors.HexColor('#1e293b'),
            padding=8,
            borderRadius=3,
            borderWidth=1,
            borderColor=colors.HexColor('#475569')
        ))
        
        # Highlight style for important info
        self.styles.add(ParagraphStyle(
            name='HighlightText',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=6,
            leading=14,
            textColor=colors.HexColor('#a5b4fc'),
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#312e81'),
            padding=6,
            borderRadius=3,
            borderWidth=1,
            borderColor=colors.HexColor('#6366f1')
        ))
        
        # Metadata style
        self.styles.add(ParagraphStyle(
            name='MetadataText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            leading=12,
            textColor=colors.HexColor('#94a3b8'),
            backColor=colors.HexColor('#0f172a'),
            padding=5,
            borderRadius=2
        ))
    
    def create_student_data_pdf(self, export_data):
        """Create a professional PDF with student data"""
        
        # Create a buffer for the PDF with dark background
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Set background color for pages
        from reportlab.platypus import Frame, PageTemplate
        from reportlab.lib.colors import Color
        
        # Build the story (content)
        story = []
        
        # Add background color
        story.append(Spacer(1, 20))
        
        # Add title page content
        story.extend(self.create_title_page_content(export_data))
        story.append(PageBreak())
        
        # Add student information section
        story.extend(self.create_student_info_content(export_data))
        
        # Add account information section
        story.extend(self.create_account_info_content(export_data))
        
        # Add audit trail section
        story.extend(self.create_audit_trail_content(export_data))
        
        # Add footer
        story.extend(self.create_footer_content())
        
        # Build the PDF
        doc.build(story, onFirstPage=self.add_background, onLaterPages=self.add_background)
        
        # Get the PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
    
    def add_background(self, canvas, doc):
        """Add dark background to pages"""
        canvas.saveState()
        canvas.setFillColor(colors.HexColor('#0f172a'))
        canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=True, stroke=False)
        canvas.restoreState()
    
    def create_title_page_content(self, export_data):
        """Create the title page content"""
        content = []
        
        # Main title
        content.append(Paragraph("STUDENT DATA EXPORT REPORT", self.styles['CustomTitle']))
        content.append(Spacer(1, 30))
        
        # Export metadata
        metadata = export_data.get('export_metadata', {})
        
        # Metadata table
        metadata_data = [
            ['Export Date:', metadata.get('export_date', 'N/A')],
            ['Exported By:', metadata.get('exported_by', 'N/A')],
            ['Purpose:', metadata.get('purpose', 'N/A')],
            ['Format:', 'PDF Document'],
            ['System:', 'SIDMS - Secure IAC Data Management System']
        ]
        
        # Metadata table with theme colors
        metadata_table = Table(metadata_data, colWidths=[2.5*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#475569')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#94a3b8')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#e2e8f0')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#6366f1'))
        ]))
        
        content.append(metadata_table)
        content.append(Spacer(1, 50))
        
        # Disclaimer
        disclaimer_text = """
        <b>CONFIDENTIALITY NOTICE:</b><br/>
        This document contains sensitive personal information and is intended for authorized administrative use only. 
        This export was performed in compliance with GDPR data portability requirements. 
        Unauthorized distribution or use of this information is strictly prohibited.
        """
        
        content.append(Paragraph(disclaimer_text, self.styles['CustomNormal']))
        
        return content
    
    def create_student_info_content(self, export_data):
        """Create student information section content"""
        content = []
        
        content.append(Paragraph("STUDENT PROFILE INFORMATION", self.styles['SectionHeader']))
        
        profile_info = export_data.get('profile_information', {})
        
        # Profile data table
        profile_data = [
            ['Full Name:', profile_info.get('full_name', 'N/A')],
            ['Email Address:', profile_info.get('email', 'N/A')],
            ['Phone Number:', profile_info.get('phone_number', 'N/A')],
            ['Address:', profile_info.get('address', 'N/A')],
            ['Degree/Program:', profile_info.get('degree', 'N/A')],
            ['Student ID:', profile_info.get('student_id', 'N/A')],
            ['Resume URL:', profile_info.get('resume_url', 'N/A')],
            ['Profile Status:', profile_info.get('profile_status', 'N/A')],
            ['Profile Created:', self.format_date(profile_info.get('profile_created'))],
            ['Profile Updated:', self.format_date(profile_info.get('profile_updated'))]
        ]
        
        # Profile data table with theme colors
        profile_table = Table(profile_data, colWidths=[2.5*inch, 4*inch])
        profile_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#475569')),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#334155')),
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#94a3b8')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#e2e8f0')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#6366f1'))
        ]))
        
        content.append(profile_table)
        content.append(Spacer(1, 20))
        
        return content
    
    def create_account_info_content(self, export_data):
        """Create account information section content"""
        content = []
        
        content.append(Paragraph("ACCOUNT SECURITY INFORMATION", self.styles['SectionHeader']))
        
        account_info = export_data.get('user_account', {})
        
        # Account data table with theme colors
        account_data = [
            ['Username:', account_info.get('username', 'N/A')],
            ['Email Address:', account_info.get('email', 'N/A')],
            ['User Role:', account_info.get('role', 'N/A')],
            ['Account Status:', 'Active' if account_info.get('enabled') else 'Disabled'],
            ['MFA Status:', 'Enabled' if account_info.get('mfa_enabled') else 'Disabled'],
            ['Account Created:', self.format_date(account_info.get('account_created'))],
            ['Account Updated:', self.format_date(account_info.get('account_updated'))]
        ]
        
        account_table = Table(account_data, colWidths=[2.5*inch, 4*inch])
        account_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#475569')),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#334155')),
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#94a3b8')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#e2e8f0')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#6366f1'))
        ]))
        
        content.append(account_table)
        content.append(Spacer(1, 20))
        
        return content
    
    def create_audit_trail_content(self, export_data):
        """Create audit trail section content"""
        content = []
        
        content.append(Paragraph("AUDIT TRAIL", self.styles['SectionHeader']))
        
        audit_trail = export_data.get('audit_trail', [])
        
        if audit_trail:
            # Audit trail table headers
            audit_data = [['Timestamp', 'Action', 'Details', 'IP Address']]
            
            # Add audit entries
            for entry in audit_trail[:50]:  # Limit to 50 entries
                timestamp = self.format_date(entry.get('timestamp'))
                action = entry.get('action', 'N/A')
                
                # Handle details safely
                details = 'N/A'
                details_obj = entry.get('details')
                if details_obj:
                    if isinstance(details_obj, dict):
                        details = details_obj.get('description', 'N/A')
                    elif isinstance(details_obj, str):
                        details = details_obj
                    else:
                        details = str(details_obj)
                
                ip_address = entry.get('ip_address', 'N/A')
                
                audit_data.append([timestamp, action, details, ip_address])
            
            audit_table = Table(audit_data, colWidths=[1.5*inch, 1.5*inch, 2.5*inch, 1.2*inch])
            audit_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#475569')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#1e293b')),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#e2e8f0')),
                ('WORDWRAP', (0, 0), (-1, -1), True),
                ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#6366f1'))
            ]))
            
            content.append(audit_table)
        else:
            content.append(Paragraph("No audit trail entries found.", self.styles['CustomNormal']))
        
        content.append(Spacer(1, 20))
        
        return content
    
    def create_footer_content(self):
        """Create footer section content"""
        content = []
        
        footer_text = f"""
        <br/><br/>
        <center>
        <b>End of Report</b><br/>
        Generated by SIDMS - Secure IAC Data Management System<br/>
        Export completed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        This document is GDPR compliant and contains complete student data as requested.
        </center>
        """
        
        content.append(Paragraph(footer_text, self.styles['CustomNormal']))
        
        return content
    
    def format_date(self, date_string):
        """Format date string for display"""
        if not date_string:
            return 'N/A'
        
        try:
            if isinstance(date_string, str):
                date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            else:
                date_obj = date_string
            
            return date_obj.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return str(date_string)

# Create a global instance
pdf_export_service = PDFExportService()
