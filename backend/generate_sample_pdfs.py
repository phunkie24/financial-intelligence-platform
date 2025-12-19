# Databricks notebook source
"""
Generate sample financial PDF documents for testing
Creates realistic-looking financial reports for each company
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
import os
import random

# Company data
COMPANIES = [
    {
        "name": "Tesla",
        "ticker": "TSLA",
        "revenue": "96.8B",
        "profit": "15.0B",
        "eps": "4.07",
        "sentiment": "Negative",
        "risk": "HIGH"
    },
    {
        "name": "Apple",
        "ticker": "AAPL",
        "revenue": "383.3B",
        "profit": "97.0B",
        "eps": "6.13",
        "sentiment": "Positive",
        "risk": "LOW"
    },
    {
        "name": "Microsoft",
        "ticker": "MSFT",
        "revenue": "211.9B",
        "profit": "72.4B",
        "eps": "9.68",
        "sentiment": "Positive",
        "risk": "LOW"
    },
    {
        "name": "Amazon",
        "ticker": "AMZN",
        "revenue": "574.8B",
        "profit": "30.4B",
        "eps": "2.90",
        "sentiment": "Neutral",
        "risk": "MEDIUM"
    },
    {
        "name": "Google",
        "ticker": "GOOGL",
        "revenue": "307.4B",
        "profit": "73.8B",
        "eps": "5.80",
        "sentiment": "Positive",
        "risk": "LOW"
    },
    {
        "name": "Meta",
        "ticker": "META",
        "revenue": "134.9B",
        "profit": "39.1B",
        "eps": "14.87",
        "sentiment": "Negative",
        "risk": "MEDIUM"
    },
    {
        "name": "Netflix",
        "ticker": "NFLX",
        "revenue": "33.7B",
        "profit": "5.4B",
        "eps": "12.55",
        "sentiment": "Positive",
        "risk": "LOW"
    },
    {
        "name": "Nvidia",
        "ticker": "NVDA",
        "revenue": "60.9B",
        "profit": "29.8B",
        "eps": "11.93",
        "sentiment": "Very Positive",
        "risk": "LOW"
    },
    {
        "name": "Intel",
        "ticker": "INTC",
        "revenue": "54.2B",
        "profit": "1.7B",
        "eps": "0.41",
        "sentiment": "Neutral",
        "risk": "MEDIUM"
    },
    {
        "name": "AMD",
        "ticker": "AMD",
        "revenue": "22.7B",
        "profit": "0.9B",
        "eps": "0.58",
        "sentiment": "Positive",
        "risk": "LOW"
    }
]

def create_financial_report(company_data, output_folder="./sample_pdfs"):
    """Create a realistic financial report PDF"""
    
    # Create output folder
    os.makedirs(output_folder, exist_ok=True)
    
    # Generate filename
    filename = f"{company_data['name']}_Q4_2024_Earnings_Report.pdf"
    filepath = os.path.join(output_folder, filename)
    
    # Create PDF
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    title = Paragraph(f"{company_data['name']} Inc.", title_style)
    story.append(title)
    
    subtitle = Paragraph(
        f"<b>Q4 2024 Earnings Report</b><br/>Ticker: {company_data['ticker']}<br/>{datetime.now().strftime('%B %d, %Y')}",
        styles['Normal']
    )
    story.append(subtitle)
    story.append(Spacer(1, 0.5*inch))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    summary_text = f"""
    {company_data['name']} reported strong financial results for Q4 2024, demonstrating 
    continued growth and operational excellence. The company achieved revenue of 
    ${company_data['revenue']}, reflecting robust demand across all business segments. 
    Market sentiment remains {company_data['sentiment'].lower()} with a risk level 
    classified as {company_data['risk']}.
    """
    story.append(Paragraph(summary_text, styles['BodyText']))
    story.append(Spacer(1, 0.3*inch))
    
    # Financial Highlights
    story.append(Paragraph("Financial Highlights", heading_style))
    
    financial_data = [
        ['Metric', 'Q4 2024', 'Q3 2024', 'Change'],
        ['Revenue', f"${company_data['revenue']}", f"${float(company_data['revenue'].replace('B', '')) * 0.95:.1f}B", '+5.3%'],
        ['Net Profit', f"${company_data['profit']}", f"${float(company_data['profit'].replace('B', '')) * 0.92:.1f}B", '+8.7%'],
        ['EPS', f"${company_data['eps']}", f"${float(company_data['eps']) * 0.94:.2f}", '+6.4%'],
        ['Operating Margin', '24.5%', '23.1%', '+1.4%'],
    ]
    
    financial_table = Table(financial_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1*inch])
    financial_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
    ]))
    
    story.append(financial_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Business Segments
    story.append(Paragraph("Business Segment Performance", heading_style))
    
    segments = [
        ['Segment', 'Revenue', 'YoY Growth', 'Margin'],
        ['Core Business', f"${float(company_data['revenue'].replace('B', '')) * 0.6:.1f}B", '+12%', '28%'],
        ['Cloud Services', f"${float(company_data['revenue'].replace('B', '')) * 0.25:.1f}B", '+25%', '35%'],
        ['Other Services', f"${float(company_data['revenue'].replace('B', '')) * 0.15:.1f}B", '+8%', '18%'],
    ]
    
    segment_table = Table(segments, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1*inch])
    segment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
    ]))
    
    story.append(segment_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Risk Assessment
    story.append(Paragraph("Risk Assessment", heading_style))
    
    risk_color = {
        "HIGH": colors.HexColor('#ef4444'),
        "MEDIUM": colors.HexColor('#f59e0b'),
        "LOW": colors.HexColor('#10b981')
    }[company_data['risk']]
    
    risk_text = f"""
    <b>Overall Risk Level: <font color="{risk_color.hexval()}">{company_data['risk']}</font></b><br/><br/>
    Market sentiment for {company_data['name']} is currently <b>{company_data['sentiment'].lower()}</b>. 
    The company faces typical industry challenges including regulatory scrutiny, competitive pressures, 
    and macroeconomic headwinds. However, strong fundamentals and market position provide resilience.
    Key risk factors include supply chain disruptions, currency fluctuations, and technology shifts.
    """
    story.append(Paragraph(risk_text, styles['BodyText']))
    story.append(Spacer(1, 0.3*inch))
    
    # Forward Guidance
    story.append(Paragraph("Forward Guidance", heading_style))
    forward_text = f"""
    Management expects continued strong performance in fiscal year 2025, with revenue growth 
    projected at 8-12% and operating margins expanding by 100-150 basis points. Strategic 
    investments in AI, cloud infrastructure, and international expansion are expected to 
    drive long-term value creation. The company maintains a strong balance sheet with 
    ${float(company_data['profit'].replace('B', '')) * 2:.1f}B in cash and equivalents.
    """
    story.append(Paragraph(forward_text, styles['BodyText']))
    story.append(Spacer(1, 0.5*inch))
    
    # Footer
    footer_text = f"""
    <i>This is a sample financial report generated for testing purposes. 
    All data is simulated and should not be used for investment decisions.<br/>
    Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>
    """
    story.append(Paragraph(footer_text, styles['Italic']))
    
    # Build PDF
    doc.build(story)
    print(f"✅ Created: {filename}")
    
    return filepath

def generate_all_reports():
    """Generate financial reports for all companies"""
    print("\n" + "="*60)
    print("📄 Generating Sample Financial Reports")
    print("="*60 + "\n")
    
    output_folder = "./sample_pdfs"
    os.makedirs(output_folder, exist_ok=True)
    
    generated_files = []
    
    for company in COMPANIES:
        filepath = create_financial_report(company, output_folder)
        generated_files.append(filepath)
    
    print("\n" + "="*60)
    print("✅ GENERATION COMPLETE!")
    print("="*60)
    print(f"\n📁 Location: {os.path.abspath(output_folder)}")
    print(f"📊 Generated {len(generated_files)} PDF files")
    print("\n💡 You can now upload these PDFs to test the platform:")
    print("   1. Start the server: uvicorn app:app --host 127.0.0.1 --port 8001 --reload")
    print("   2. Go to: http://localhost:5173/documents")
    print("   3. Upload the PDFs from the sample_pdfs/ folder")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    generate_all_reports()