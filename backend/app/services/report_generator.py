"""
Report generation and PDF conversion utilities
"""

import os
import markdown
import weasyprint
from typing import Dict, Tuple

from .utils import (
    clean_company_name,
    clean_linkedin_references,
    is_trusted_domain,
    is_generic_image,
    download_image
)


def clean_analysis_data(analysis_data: dict) -> dict:
    """
    Remove LinkedIn references from all string fields

    Args:
        analysis_data: Analysis dictionary

    Returns:
        Cleaned analysis dictionary
    """
    def clean_recursive(obj):
        if isinstance(obj, str):
            return clean_linkedin_references(obj)
        elif isinstance(obj, dict):
            return {key: clean_recursive(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [clean_recursive(item) for item in obj]
        else:
            return obj

    return clean_recursive(analysis_data)


def format_structured_output(
    analysis_data: dict,
    company_name: str,
    timestamp: str,
    output_dir: str = "."
) -> Tuple[str, Dict[str, str]]:
    """
    Format analysis data into PowerPoint slide format

    Args:
        analysis_data: Structured analysis dictionary
        company_name: Company name
        timestamp: Timestamp for file naming
        output_dir: Output directory

    Returns:
        Tuple of (formatted_markdown: str, downloaded_images: dict)
    """
    output = []
    downloaded_images = {}

    # Header
    clean_name = clean_company_name(company_name)
    output.append(f"# {clean_name} | Strategic Analysis")
    output.append(f"*{analysis_data['analysis_date']}*")

    # Executive Summary
    output.append(f"\n**KEY INSIGHT:** {analysis_data['executive_summary']}")

    # Investment Trends Table
    output.append("\n## Investment Opportunities")
    output.append("| Trend | Priority | Market Size | CAGR | ROI | Investment |")
    output.append("|-------|----------|-------------|------|-----|------------|")

    for trend in analysis_data.get('investment_trends', [])[:3]:
        priority = trend.get('investment_priority', 'N/A')
        size = (
            f"${trend.get('market_size_usd_billions', 0):.0f}B"
            if trend.get('market_size_usd_billions')
            else "N/A"
        )
        cagr = (
            f"{trend.get('cagr_percentage', 0):.0f}%"
            if trend.get('cagr_percentage')
            else "N/A"
        )
        roi = (
            f"{trend.get('expected_roi_percentage', 0):.0f}%"
            if trend.get('expected_roi_percentage')
            else "N/A"
        )
        investment = (
            f"${trend.get('investment_required_millions', 0):.0f}M"
            if trend.get('investment_required_millions')
            else "N/A"
        )

        output.append(
            f"| **{trend['trend_name']}** | {priority} | {size} | {cagr} | {roi} | {investment} |"
        )

    # Top Investment Opportunities
    output.append("\n## Top Investment Opportunities")
    for i, trend in enumerate(analysis_data.get('investment_trends', [])[:3], 1):
        cagr = (
            f"{trend.get('cagr_percentage', 0):.0f}% CAGR"
            if trend.get('cagr_percentage')
            else ""
        )
        output.append(
            f"**{i}.** **{trend['trend_name']}**: {trend['description']} ({cagr})"
        )

    # Strategic Priorities
    output.append("\n## Strategic Priorities")
    for i, rec in enumerate(analysis_data.get('key_strategic_recommendations', [])[:3], 1):
        output.append(f"**{i}.** {rec}")

    # Implementation Timeline
    output.append("\n## Implementation Timeline")
    for priority in analysis_data.get('implementation_priorities', [])[:3]:
        output.append(f"• {priority}")

    # Market Trend Charts
    if analysis_data.get('visual_data'):
        output.append("\n## Market Trend Charts")

        valid_trend_charts = 0
        for i, visual in enumerate(analysis_data['visual_data'], 1):
            title = visual.get('title', f'Trend Chart {i}')
            url = visual.get('source_url', '')
            description = visual.get('description', '')

            if not url:
                continue

            # Reject generic images
            if is_generic_image(url, title, description):
                continue

            # Check for market data indicators
            market_data_keywords = [
                'market size', 'cagr', 'forecast', 'revenue',
                'billion', 'million', '$', 'growth rate',
                'compound annual', 'market share', 'segmentation'
            ]
            has_market_data = any(
                keyword in (title + ' ' + description).lower()
                for keyword in market_data_keywords
            )

            from_trusted_source = is_trusted_domain(url)
            is_valid_chart = from_trusted_source or has_market_data

            if is_valid_chart:
                output.append(f"\n### {title}")

                # Download image for PDF
                local_image_path = download_image(url, output_dir, timestamp)
                if local_image_path:
                    rel_path = os.path.relpath(local_image_path, output_dir)
                    output.append(f"![{title}]({rel_path})")
                    downloaded_images[url] = local_image_path
                else:
                    output.append(f"![{title}]({url})")

                output.append(f"*{visual.get('description', 'Market trend chart')}*")
                valid_trend_charts += 1

        # Remove section header if no valid charts
        if valid_trend_charts == 0:
            output = output[:-1]

    # Key Numbers Summary
    output.append("\n---")
    total_market_size = sum([
        trend.get('market_size_usd_billions', 0)
        for trend in analysis_data.get('investment_trends', [])
    ])

    investment_trends = analysis_data.get('investment_trends', [])
    trends_with_cagr = [
        t for t in investment_trends
        if t.get('cagr_percentage')
    ]
    avg_cagr = (
        sum([t.get('cagr_percentage', 0) for t in trends_with_cagr]) / len(trends_with_cagr)
        if trends_with_cagr
        else 0
    )

    high_priority_trends = len([
        t for t in investment_trends
        if t.get('investment_priority') == 'High'
    ])

    output.append(
        f"**Total Market Size: ${total_market_size:.0f}B** | "
        f"**Avg CAGR: {avg_cagr:.1f}%** | "
        f"**High Priority Trends: {high_priority_trends}**"
    )

    # Clean LinkedIn references
    final_output = clean_linkedin_references("\n".join(output))

    return final_output, downloaded_images


def convert_markdown_to_pdf(
    markdown_content: str,
    output_path: str,
    company_name: str,
    images_dir: str = None
) -> bool:
    """
    Convert markdown to PDF using WeasyPrint

    Args:
        markdown_content: Markdown content
        output_path: Output PDF path
        company_name: Company name for title
        images_dir: Images directory (optional)

    Returns:
        True if successful, False otherwise
    """
    clean_name = clean_company_name(company_name)

    # Try markdown-pdf first (best for tables and images)
    try:
        from markdown_pdf import MarkdownPdf, Section

        pdf = MarkdownPdf(toc_level=2)

        if images_dir:
            pdf.meta["path"] = os.path.dirname(os.path.abspath(output_path))

        pdf.add_section(Section(markdown_content, toc=False))
        pdf.meta["title"] = f"{clean_name} - Strategic Analysis"
        pdf.meta["author"] = "BetterSurvey Analysis"

        pdf.save(output_path)
        print("✅ PDF created using markdown-pdf (optimal quality)")
        return True

    except Exception as e:
        print(f"⚠️  markdown-pdf failed: {e}")

    # Fallback to WeasyPrint
    try:
        md = markdown.Markdown(extensions=['tables', 'fenced_code', 'attr_list'])
        html_content = md.convert(markdown_content)

        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{clean_name} - Strategic Analysis</title>
    <style>
        @page {{
            size: A4;
            margin: 20mm;
            @top-center {{
                content: "{clean_name} - Strategic Analysis";
                font-size: 10px;
                color: #666;
            }}
            @bottom-center {{
                content: "Page " counter(page) " of " counter(pages);
                font-size: 10px;
                color: #666;
            }}
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: none;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            font-size: 28px;
        }}
        h2 {{
            color: #2980b9;
            margin-top: 30px;
            font-size: 22px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        h3 {{
            color: #34495e;
            font-size: 18px;
            margin-top: 25px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
            font-size: 12px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px 8px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        img {{
            max-width: 100%;
            height: auto;
            margin: 15px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
            display: block;
        }}
        strong {{
            color: #2c3e50;
        }}
        ul {{
            margin: 15px 0;
        }}
        li {{
            margin: 8px 0;
        }}
        em {{
            color: #7f8c8d;
            font-style: italic;
        }}
        hr {{
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 30px 0;
        }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
        """

        html_doc = weasyprint.HTML(
            string=html_template,
            base_url=os.path.dirname(os.path.abspath(output_path))
        )
        html_doc.write_pdf(output_path)

        print("✅ PDF created using WeasyPrint (good quality)")
        return True

    except Exception as e:
        print(f"⚠️  WeasyPrint conversion failed: {e}")
        print(f"❌ All PDF conversion methods failed")
        return False
