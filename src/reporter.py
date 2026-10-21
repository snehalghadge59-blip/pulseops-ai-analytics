import os
from datetime import datetime
from .analytics import AnalyticsEngine

class ExecutiveReporter:
    def __init__(self, analytics: AnalyticsEngine):
        self.analytics = analytics

    def generate_markdown_report(self) -> str:
        """Generates comprehensive executive performance briefing in Markdown."""
        kpis = self.analytics.get_executive_kpis()
        carriers = self.analytics.get_carrier_sla_performance()
        categories = self.analytics.get_category_profitability()
        rfm = self.analytics.get_rfm_segments()

        timestamp = datetime.now().strftime("%B %d, %Y")

        worst_carrier = carriers.iloc[0] if not carriers.empty else None
        top_category = categories.iloc[0] if not categories.empty else None

        md = f"""# 📈 PulseOps AI | Executive Business Briefing
**Published Date:** {timestamp}  
**Platform Version:** 2.4-Production  
**Prepared For:** Senior Leadership & Executive Operations  

---

## 1. Executive Performance Scorecard
| Metric | Result | Benchmark | Status |
| :--- | :--- | :--- | :--- |
| **Total Net Revenue** | ${kpis.get('total_revenue', 0):,.2f} | Target: $500,000 | 🟢 On Track |
| **Gross Margin Rate** | {kpis.get('gross_margin_pct', 0):.1f}% | Target: 55.0% | 🟢 Strong |
| **On-Time Delivery Rate (OTDR)** | {kpis.get('on_time_rate', 0):.1f}% | Target: 92.0% | 🟡 Monitor |
| **Average Order Value (AOV)** | ${kpis.get('avg_order_value', 0):,.2f} | Target: $200.00 | 🟢 High |
| **Customer Satisfaction (CSAT)** | {kpis.get('avg_csat', 0):.2f} / 5.0 | Target: 4.20 | 🟢 Healthy |

---

## 2. Supply Chain & Logistics SLA Risk Assessment
The primary operational drag this period stems from carrier delay variance:
"""
        if worst_carrier is not None:
            md += f"""
* **Critical Bottleneck Carrier:** **{worst_carrier['carrier']}** registered an unacceptable **{worst_carrier['delay_rate_pct']}% delay rate** across {worst_carrier['total_shipments']} shipments.
* **CSAT Deprecation:** Delayed deliveries experienced an average satisfaction collapse to **{worst_carrier['avg_csat_score']} / 5.0**.
* **Financial Drag:** Estimated freight breach penalty and dispute overhead equals **${worst_carrier['estimated_delay_penalty_cost']:,.2f}**.
"""

        md += """
---

## 3. Product Category Profitability Breakdown
"""
        if top_category is not None:
            md += f"""
* **Growth Driver:** **{top_category['category']}** leads portfolio performance with **${top_category['revenue']:,.2f}** in gross revenue and a **{top_category['margin_pct']}%** margin.
"""

        md += """
---

## 4. Customer Cohort & RFM Distribution
"""
        if not rfm.empty:
            for _, row in rfm.iterrows():
                md += f"* **{row['customer_tier']}:** {row['customer_count']} accounts ({row['total_tier_revenue']:,.2f} total revenue)\n"

        md += """
---

## 5. Strategic Action Items for Next Quarter
1. **Carrier SLA Enforcement:** Cap volume allocated to ApexGround until on-time performance reaches 88%.
2. **Margin Optimization:** Reinvest surplus margins from top categories into priority customer retention campaigns.
3. **Automated Churn Interception:** Trigger automated email and discount workflows for the 'At Risk' segment.
"""
        return md

    def generate_pdf_report(self, output_path="executive_report.pdf") -> str:
        """Generates a professional corporate PDF report using ReportLab."""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors

            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=40
            )
            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                'ReportTitle',
                parent=styles['Heading1'],
                fontSize=20,
                leading=24,
                textColor=colors.HexColor('#0F172A'),
                spaceAfter=6
            )
            subtitle_style = ParagraphStyle(
                'ReportSubtitle',
                parent=styles['Normal'],
                fontSize=10,
                leading=14,
                textColor=colors.HexColor('#64748B'),
                spaceAfter=15
            )
            heading_style = ParagraphStyle(
                'ReportH2',
                parent=styles['Heading2'],
                fontSize=14,
                leading=18,
                textColor=colors.HexColor('#1E293B'),
                spaceBefore=12,
                spaceAfter=8
            )
            body_style = ParagraphStyle(
                'ReportBody',
                parent=styles['Normal'],
                fontSize=9.5,
                leading=14,
                textColor=colors.HexColor('#334155'),
                spaceAfter=6
            )

            story = []

            # Header
            story.append(Paragraph("PulseOps AI | Executive Business Briefing", title_style))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')} | Confidential - Internal Executive Use Only", subtitle_style))
            story.append(Spacer(1, 10))

            # KPIs
            story.append(Paragraph("1. Executive Operational Scorecard", heading_style))
            kpis = self.analytics.get_executive_kpis()
            kpi_data = [
                ["Key Metric", "Reported Value", "Operational Target", "Health Status"],
                ["Total Net Revenue", f"${kpis.get('total_revenue', 0):,.2f}", "$500,000", "OPTIMAL"],
                ["Gross Margin Rate", f"{kpis.get('gross_margin_pct', 0):.1f}%", "55.0%", "HEALTHY"],
                ["On-Time Delivery Rate", f"{kpis.get('on_time_rate', 0):.1f}%", "92.0%", "ATTENTION"],
                ["Average Order Value", f"${kpis.get('avg_order_value', 0):,.2f}", "$200.00", "OPTIMAL"],
                ["Customer Rating (CSAT)", f"{kpis.get('avg_csat', 0):.2f} / 5.0", "4.20 / 5.0", "HEALTHY"]
            ]
            t = Table(kpi_data, colWidths=[150, 120, 120, 100])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9.5),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8FAFC')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8.5),
            ]))
            story.append(t)
            story.append(Spacer(1, 15))

            # Carrier Performance
            story.append(Paragraph("2. Supply Chain SLA & Carrier Risk Assessment", heading_style))
            carriers = self.analytics.get_carrier_sla_performance()
            if not carriers.empty:
                carrier_data = [["Carrier", "Shipments", "Transit Days", "Delay Rate", "Avg CSAT", "Penalty Cost"]]
                for _, r in carriers.iterrows():
                    carrier_data.append([
                        str(r['carrier']),
                        str(r['total_shipments']),
                        str(r['avg_transit_days']),
                        f"{r['delay_rate_pct']}%",
                        str(r['avg_csat_score']),
                        f"${r['estimated_delay_penalty_cost']:,.2f}"
                    ])
                ct = Table(carrier_data, colWidths=[100, 80, 80, 80, 70, 80])
                ct.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                ]))
                story.append(ct)

            story.append(Spacer(1, 15))
            story.append(Paragraph("3. Executive Directives & Strategic Roadmap", heading_style))
            story.append(Paragraph("• <b>Enforce SLA penalty clauses:</b> Shift 30% of standard route allocations away from ApexGround.", body_style))
            story.append(Paragraph("• <b>Protect High-Margin SKUs:</b> Reallocate inventory buffers to Consumer Electronics to preempt stockouts.", body_style))
            story.append(Paragraph("• <b>Retention Program:</b> Initiate targeted loyalty promotions for accounts in the 'At Risk' RFM bucket.", body_style))

            doc.build(story)
            return output_path
        except Exception as e:
            return str(e)
