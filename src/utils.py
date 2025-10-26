"""
Utility functions for file handling, validation, and data cleaning
"""

import os
import re
import hashlib
import requests
from pathlib import Path
from urllib.parse import urlparse
from typing import Optional, Tuple


def make_filename_safe(name: str) -> str:
    """
    Convert company name to safe filename

    Args:
        name: Company name (may include pipe-separated LinkedIn URL)

    Returns:
        Safe filename string
    """
    # Extract company name if pipe-separated format
    if '|' in name:
        name = name.split('|')[0].strip()

    # Remove invalid filename characters
    invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    for char in invalid_chars:
        name = name.replace(char, '')

    # Replace spaces with underscores and convert to lowercase
    name = name.replace(' ', '_').lower()

    # Remove multiple underscores
    while '__' in name:
        name = name.replace('__', '_')

    return name.strip('_')


def get_company_linkedin(company_name: str) -> Optional[str]:
    """
    Extract LinkedIn URL for company from companies.txt or company name

    Args:
        company_name: Company name (may include pipe-separated LinkedIn URL)

    Returns:
        LinkedIn URL if found, None otherwise
    """
    # Check if LinkedIn URL is in company name
    if '|' in company_name and 'linkedin.com' in company_name.lower():
        parts = company_name.split('|')
        for part in parts:
            part = part.strip()
            if 'linkedin.com' in part.lower():
                return part

    # Check companies.txt
    try:
        with open('companies.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Extract company name without URL
        company_name_only = (
            company_name.split('|')[0].strip()
            if '|' in company_name
            else company_name
        )

        for line in lines:
            line = line.strip()
            if '|' in line and not line.startswith('#'):
                name, linkedin_url = line.split('|', 1)
                if name.strip().lower() == company_name_only.lower():
                    return linkedin_url.strip()

        return None
    except FileNotFoundError:
        return None


def clean_linkedin_references(text: str) -> str:
    """
    Remove LinkedIn URLs and references from text

    Args:
        text: Text containing LinkedIn references

    Returns:
        Cleaned text
    """
    linkedin_patterns = [
        r'https?://(?:www\.)?linkedin\.com/[^\s<>"{\[\]`]*',
        r'linkedin\.com/[^\s<>"{\[\]`]*',
        r'LinkedIn:?\s*https?://[^\s<>"{\[\]`]*',
        r'LinkedIn\s+page:?\s*https?://[^\s<>"{\[\]`]*',
        r'Company\s+LinkedIn:?\s*https?://[^\s<>"{\[\]`]*'
    ]

    for pattern in linkedin_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    # Clean up excessive whitespace
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)

    return text.strip()


def clean_company_name(name: str) -> str:
    """
    Clean company name for headers (remove LinkedIn references and pipes)

    Args:
        name: Company name with possible LinkedIn URL

    Returns:
        Cleaned company name
    """
    # Remove LinkedIn URLs
    name = clean_linkedin_references(name)

    # Remove pipes and everything after
    name = re.sub(r'\s*\|\s*.*$', '', name)
    name = re.sub(r'\s*\|\s*', '', name)
    name = re.sub(r' {2,}', ' ', name)

    return name.strip()


def is_trusted_domain(url: str) -> bool:
    """
    Verify if URL is from a trusted market research domain

    Args:
        url: URL to check

    Returns:
        True if from trusted domain, False otherwise
    """
    trusted_domains = [
        'grandviewresearch.com',
        'precedenceresearch.com',
        'gminsights.com',
        'futuremarketinsights.com',
        'marketsandmarkets.com',
        'zionmarketresearch.com',
        'polarismarketresearch.com',
        'verifiedmarketresearch.com',
        'statista.com',
        'fortunebusinessinsights.com'
    ]

    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower().replace('www.', '')
        return any(trusted_domain in domain for trusted_domain in trusted_domains)
    except:
        return False


def is_generic_image(url: str, title: str, description: str) -> bool:
    """
    Check if image is generic/non-data content

    Args:
        url: Image URL
        title: Image title
        description: Image description

    Returns:
        True if generic image, False otherwise
    """
    generic_sources = [
        'vecteezy.com', 'freepik.com', 'shutterstock.com',
        'istockphoto.com', 'depositphotos.com', 'gettyimages.com',
        'pexels.com', 'unsplash.com', 'youtube.com', 'youtu.be',
        'vimeo.com', 'economicsdiscussion.net', 'investopedia.com',
        'wikipedia.org', 'examples.com'
    ]

    generic_keywords = [
        'vector', 'illustration', 'concept', 'icon', 'template',
        'example', 'sample', 'puzzle', 'jigsaw', 'assembling',
        'matching-together', 'visualizing', 'problem-solving',
        'stock-photo', 'stock-illustration', 'diagram-theory',
        'introduction', 'overview', 'what-is', 'guide-to'
    ]

    url_lower = url.lower()
    title_lower = title.lower()
    desc_lower = description.lower()

    # Check generic sources
    if any(source in url_lower for source in generic_sources):
        return True

    # Check generic keywords
    combined_text = f"{url_lower} {title_lower} {desc_lower}"
    if any(keyword in combined_text for keyword in generic_keywords):
        return True

    return False


def download_image(url: str, output_dir: str, timestamp: str) -> Optional[str]:
    """
    Download image from URL

    Args:
        url: Image URL
        output_dir: Output directory
        timestamp: Timestamp for directory naming

    Returns:
        Local file path if successful, None otherwise
    """
    try:
        source_type = "trusted source" if is_trusted_domain(url) else "alternative source"

        # Create images directory
        images_dir = os.path.join(output_dir, f"images_{timestamp}")
        os.makedirs(images_dir, exist_ok=True)

        # Generate filename from URL hash
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        parsed_url = urlparse(url)
        extension = os.path.splitext(parsed_url.path)[1] or '.jpg'
        filename = f"chart_{url_hash}{extension}"
        filepath = os.path.join(images_dir, filename)

        # Download image
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        with open(filepath, 'wb') as f:
            f.write(response.content)

        print(f"Downloaded image from {source_type}: {filename}")
        return filepath

    except Exception as e:
        print(f"Failed to download image from {url}: {e}")
        return None


def detect_generic_analysis(analysis_data: dict) -> Tuple[bool, str]:
    """
    Detect if analysis is too generic and lacks company-specific insights

    Args:
        analysis_data: Structured analysis dictionary

    Returns:
        Tuple of (is_generic: bool, reason: str)
    """
    # Check executive summary for strong generic indicators
    exec_summary = analysis_data.get('executive_summary', '').lower()
    strong_generic_phrases = [
        'research data insufficient', 'unable to find specific',
        'no information available', 'cannot analyze', 'insufficient data'
    ]

    generic_count = sum(
        1 for phrase in strong_generic_phrases
        if phrase in exec_summary
    )
    if generic_count >= 2:
        return True, "Executive summary indicates insufficient company data"

    # Check if trends exist
    trends = analysis_data.get('investment_trends', [])
    if not trends:
        return True, "No investment trends identified"

    # Check if all trends lack market size
    total_market_size = sum(
        trend.get('market_size_usd_billions', 0)
        for trend in trends
    )
    if total_market_size == 0:
        return True, "All trends lack market size data"

    # Check for trends with quantitative data
    trends_with_data = sum(
        1 for trend in trends
        if trend.get('cagr_percentage') and trend.get('market_size_usd_billions')
    )

    if trends_with_data < 2:
        return True, "Most trends lack quantitative market data"

    return False, "Analysis appears to be company-specific"
