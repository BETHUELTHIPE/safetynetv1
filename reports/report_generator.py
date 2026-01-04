import os
import io
import datetime
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from django.conf import settings
from django.utils import timezone
from django.db.models import Count
from .models import CrimeReport

class MonthlyReportGenerator:
    """
    Class to generate monthly crime report PDF with statistics and visualizations
    """
    def __init__(self, month=None, year=None):
        """Initialize with optional month and year parameters"""
        if month and year:
            self.date = datetime.date(year, month, 1)
        else:
            # Get previous month if not specified
            today = timezone.now().date()
            if today.month == 1:
                self.date = datetime.date(today.year - 1, 12, 1)
            else:
                self.date = datetime.date(today.year, today.month - 1, 1)
        
        self.month_name = self.date.strftime("%B")
        self.year = self.date.year
        self.report_title = f"KingsPark Crime Report - {self.month_name} {self.year}"
        
        # Get start and end dates
        self.start_date = self.date
        if self.date.month == 12:
            self.end_date = datetime.date(self.date.year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            self.end_date = datetime.date(self.date.year, self.date.month + 1, 1) - datetime.timedelta(days=1)
        
    def get_crime_data(self):
        """Query database for crime data in the specified month"""
        crime_data = CrimeReport.objects.filter(
            date_reported__gte=self.start_date,
            date_reported__lte=self.end_date + datetime.timedelta(days=1)  # Include whole day
        )
        
        # Get total count
        self.total_crimes = crime_data.count()
        
        # Get crime by category
        self.crimes_by_category = list(crime_data.values('category').annotate(
            count=Count('category')).order_by('-count'))
        
        # Get crime by status
        self.crimes_by_status = list(crime_data.values('status').annotate(
            count=Count('status')).order_by('-count'))
        
        # Get crime by day of month
        self.crimes_by_date = {}
        for day in range(1, self.end_date.day + 1):
            date = datetime.date(self.year, self.date.month, day)
            count = crime_data.filter(date_reported__date=date).count()
            self.crimes_by_date[day] = count
        
        # Get crime by location
        self.crimes_by_location = list(crime_data.values('location').annotate(
            count=Count('location')).order_by('-count')[:10])  # Top 10 locations
        
        return crime_data
    
    def create_charts(self):
        """Create all charts needed for the report"""
        charts = {}
        
        # Categories pie chart
        plt.figure(figsize=(8, 5))
        if self.crimes_by_category:
            labels = [item['category'].replace('_', ' ').title() for item in self.crimes_by_category]
            counts = [item['count'] for item in self.crimes_by_category]
            plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=140)
            plt.axis('equal')
            plt.title('Crime Categories')
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
            buf.seek(0)
            charts['categories_pie'] = buf
            plt.close()
        
        # Status bar chart
        plt.figure(figsize=(8, 5))
        if self.crimes_by_status:
            labels = [item['status'].replace('_', ' ').title() for item in self.crimes_by_status]
            counts = [item['count'] for item in self.crimes_by_status]
            plt.bar(labels, counts, color='skyblue')
            plt.xlabel('Status')
            plt.ylabel('Number of Crimes')
            plt.title('Crime Status')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
            buf.seek(0)
            charts['status_bar'] = buf
            plt.close()
        
        # Daily trend line chart
        plt.figure(figsize=(10, 5))
        days = list(self.crimes_by_date.keys())
        counts = list(self.crimes_by_date.values())
        plt.plot(days, counts, marker='o', linestyle='-', color='green')
        plt.xlabel('Day of Month')
        plt.ylabel('Number of Crimes')
        plt.title('Daily Crime Trend')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
        buf.seek(0)
        charts['daily_trend'] = buf
        plt.close()
        
        return charts
    
    def generate_pdf(self, output_path=None):
        """Generate the PDF report"""
        # Default path if not specified
        if not output_path:
            reports_dir = os.path.join(settings.MEDIA_ROOT, 'crime_reports')
            os.makedirs(reports_dir, exist_ok=True)
            output_path = os.path.join(reports_dir, f"crime_report_{self.date.strftime('%Y_%m')}.pdf")
        
        # Get data and charts
        crime_data = self.get_crime_data()
        charts = self.create_charts()
        
        # Create PDF
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []
        
        # Create title style
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Title'],
            fontSize=24,
            textColor=colors.darkblue,
            spaceAfter=12,
            alignment=1  # center aligned
        )
        
        # Add title
        elements.append(Paragraph(self.report_title, title_style))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Add report generation date
        date_text = f"Report Generated: {timezone.now().strftime('%d %B %Y')}"
        elements.append(Paragraph(date_text, styles["Normal"]))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Add summary information
        summary = f"This report provides an overview of crimes reported in the Kings Park area during {self.month_name} {self.year}. " \
                 f"A total of <b>{self.total_crimes}</b> crimes were reported during this period."
        elements.append(Paragraph(summary, styles["Normal"]))
        elements.append(Spacer(1, 0.4 * inch))
        
        # Section: Crime by Category
        elements.append(Paragraph("Crimes by Category", styles["Heading2"]))
        if 'categories_pie' in charts:
            img = Image(charts['categories_pie'], width=400, height=250)
            elements.append(img)
        
        # Create a table with category data
        if self.crimes_by_category:
            cat_data = [['Category', 'Count', 'Percentage']]
            for item in self.crimes_by_category:
                category = item['category'].replace('_', ' ').title()
                count = item['count']
                percentage = f"{(count / self.total_crimes * 100):.1f}%" if self.total_crimes else "0%"
                cat_data.append([category, count, percentage])
            
            table = Table(cat_data, colWidths=[2.5*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(table)
        
        elements.append(Spacer(1, 0.3 * inch))
        
        # Section: Crime Status
        elements.append(Paragraph("Crime Status", styles["Heading2"]))
        if 'status_bar' in charts:
            img = Image(charts['status_bar'], width=400, height=250)
            elements.append(img)
        
        # Create a table with status data
        if self.crimes_by_status:
            status_data = [['Status', 'Count', 'Percentage']]
            for item in self.crimes_by_status:
                status = item['status'].replace('_', ' ').title()
                count = item['count']
                percentage = f"{(count / self.total_crimes * 100):.1f}%" if self.total_crimes else "0%"
                status_data.append([status, count, percentage])
            
            table = Table(status_data, colWidths=[2.5*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(table)
            
        elements.append(Spacer(1, 0.3 * inch))
        
        # Section: Daily Crime Trend
        elements.append(Paragraph("Daily Crime Trend", styles["Heading2"]))
        if 'daily_trend' in charts:
            img = Image(charts['daily_trend'], width=450, height=250)
            elements.append(img)
        
        # Section: Hotspots (Top Locations)
        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph("Crime Hotspots", styles["Heading2"]))
        
        if self.crimes_by_location:
            hotspot_data = [['Location', 'Number of Reports']]
            for item in self.crimes_by_location:
                hotspot_data.append([item['location'], item['count']])
            
            table = Table(hotspot_data, colWidths=[3.5*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("No location data available", styles["Normal"]))
            
        # Add footer with safety tips
        elements.append(Spacer(1, 0.5 * inch))
        safety_tips = ParagraphStyle(
            'SafetyTips',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.gray,
            backColor=colors.lightgrey,
            borderPadding=5,
            borderWidth=0.5,
            borderColor=colors.grey,
        )
        
        elements.append(Paragraph("<b>Safety Tips:</b> Stay vigilant in your community. Report suspicious activities. " \
                               "Keep emergency numbers handy. Install adequate lighting around your property. " \
                               "Join or form a neighborhood watch group.", safety_tips))
        
        # Build the PDF
        doc.build(elements)
        
        return output_path
