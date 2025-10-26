"""
Prompt templates for market research and analysis
"""

from datetime import datetime


def get_perplexity_research_prompt(
    company_name: str,
    company_linkedin: str = None,
    company_website: str = None,
    country: str = None,
    city: str = None,
    sector: str = None,
    company_type: str = None
) -> str:
    """
    Generate the research prompt for Perplexity AI

    Args:
        company_name: Name of the company to analyze
        company_linkedin: LinkedIn URL of the company (optional)
        company_website: Company website URL (optional)
        country: Country where the company is based (optional)
        city: City where the company is based (optional)
        sector: Industry sector (optional)
        company_type: Type of company (startup, pmi, etc.) (optional)

    Returns:
        Formatted prompt string for Perplexity AI
    """
    # Build company context
    linkedin_context = (
        f"- Analyze {company_name}'s LinkedIn company page: {company_linkedin}"
        if company_linkedin
        else f"- Find and analyze {company_name}'s LinkedIn company page"
    )

    website_context = (
        f"- Analyze {company_name}'s website: {company_website}"
        if company_website
        else ""
    )

    location_context = ""
    if country and city:
        location_context = f"- Company location: {city}, {country}"
    elif country:
        location_context = f"- Company location: {country}"
    elif city:
        location_context = f"- Company location: {city}"

    sector_context = f"- Industry sector: {sector}" if sector else ""
    type_context = f"- Company type: {company_type}" if company_type else ""

    linkedin_instruction = (
        f"- Use {company_name}'s LinkedIn page ({company_linkedin}) as primary source for company context"
        if company_linkedin
        else f"- Search for and analyze {company_name}'s LinkedIn company page"
    )

    return f"""
Conduct a comprehensive MARKET TREND analysis focusing on investment opportunities that {company_name} should consider, structured as follows:

## 0. COMPANY CONTEXT RESEARCH - MANDATORY
{linkedin_context}
{website_context}
{location_context}
{sector_context}
{type_context}
- Research {company_name}'s current business focus, industry, products/services from any available sources
- Look for recent company updates, news, press releases, and announcements (LinkedIn, website, news articles)
- Identify {company_name}'s specific industry sector and business model
- Find company website, product pages, case studies, client information, and any public documentation
- IMPORTANT: Use ALL available information even if limited - focus on what you CAN find rather than what's missing
- Only state "ANALYSIS NOT POSSIBLE" if you literally cannot find ANY information about the company's business
- Proceed with analysis using whatever company data is available and clearly indicate confidence level
- Use all gathered context to tailor subsequent trend analysis to the company's actual business model

## 1. EMERGING MARKET TRENDS IDENTIFICATION
- Identify the fastest-growing market trends and technologies relevant to {company_name}'s industry
- Focus on NEW market opportunities, not existing company divisions
- Include market size and CAGR for each emerging trend (2024-2030)
- Provide investment potential and timeline for each trend

## 2. TECHNOLOGY & INNOVATION TRENDS (2024-2025)
For each emerging trend:
- Market size in USD billions and projected CAGR
- Key technological innovations driving growth
- Adoption rates and market penetration timelines
- Investment requirements and expected ROI
- Leading companies and startups in each trend
- Regulatory environment and government support

## 3. FUTURE GROWTH PROJECTIONS (2025-2035)
- Long-term market projections for each trend with quantified growth rates
- Expected market disruptions and their timeline
- Demographic and social changes driving adoption
- Sustainability and green technology opportunities
- Digital transformation and AI adoption trends
- New business models and revenue streams emerging

## 4. INVESTMENT OPPORTUNITY ANALYSIS
- Ranking of trends by investment attractiveness (market size × CAGR × feasibility)
- Entry barriers and competitive landscape for each trend
- Strategic fit with {company_name}'s existing capabilities
- Required investment levels and expected returns
- Timeline for market entry and break-even projections

## 5. MARKET TREND CHARTS AND DATA - MANDATORY REQUIREMENT
- MANDATORY: Find and include AT LEAST 2-3 HIGH-QUALITY market trend charts for the company's industry sector
- This is NON-NEGOTIABLE - you MUST search multiple times with different keywords until you find suitable charts

SEARCH STRATEGY - Execute these searches systematically:
1. Search "{company_name}'s industry + market size chart 2024"
2. Search "{company_name}'s sector + CAGR forecast graph"
3. Search "{company_name}'s market + growth projections statista"
4. Search specific industry keywords + "market research chart grandviewresearch"
5. Search industry + "market analysis precedenceresearch"

- PRIORITY 1 - PREFERRED SOURCES (search these first):
  1. Grand View Research (grandviewresearch.com)
  2. Precedence Research (precedenceresearch.com)
  3. Global Market Insights / GMInsights (gminsights.com)
  4. Future Market Insights (futuremarketinsights.com)
  5. Markets and Markets (marketsandmarkets.com)
  6. Zion Market Research (zionmarketresearch.com)
  7. Polaris Market Research (polarismarketresearch.com)
  8. Verified Market Research (verifiedmarketresearch.com)
  9. Statista (statista.com)
  10. Fortune Business Insights (fortunebusinessinsights.com)

- PRIORITY 2 - FALLBACK: If no images from Priority 1 after multiple searches, accept charts from:
  * Industry trade publications with market data
  * Business intelligence platforms (Mordor Intelligence, Research and Markets, etc.)
  * Financial research sites with sector analysis charts
  * Government/regulatory agency market reports with graphs

- ALWAYS REJECT: Company logos, product photos, executive portraits, generic stock images, conceptual illustrations without data

- REQUIRED chart types (find at least 2 of these):
  * Market size evolution charts showing growth over multiple years
  * CAGR growth rate visualizations by market segment
  * Market segmentation breakdown with percentages/dollar values
  * Regional growth distribution with quantitative data
  * Technology/service adoption curves with projections

- IMAGE VALIDATION: Each image MUST contain visible quantitative data (numbers, percentages, growth rates, market sizes in billions/millions)
- Each chart must include: descriptive title, source URL, description of metrics shown, strategic relevance

## 6. STRATEGIC INVESTMENT RECOMMENDATIONS
- Top 5 trends {company_name} should invest in immediately based on LinkedIn strategic direction
- Budget allocation suggestions across different trends
- Partnership and acquisition targets in each trend
- Risk mitigation strategies for each investment area
- KPIs and success metrics for trend monitoring

RESEARCH INSTRUCTIONS - CRITICAL:
{linkedin_instruction}
- Analyze the company's LinkedIn profile, recent posts, business description, and any available social media
- Search for company website, product pages, pricing, customer testimonials, case studies, blog posts
- Identify SPECIFIC products/services the company offers using all available sources
- PRAGMATIC APPROACH: Work with whatever information you can find - even partial data is valuable
- If you find at least 2 specific aspects of the company (business model, industry, products, services, target market), PROCEED with analysis
- Indicate clearly which information is confirmed vs. inferred from industry context
- Use all available insights to inform strategic fit assessments for trends
- Focus on MARKET TRENDS that align with company's business model based on available information
- Include specific CAGR figures, market sizes, and investment requirements from trusted research sources
- Find charts ONLY from: Grand View Research, Precedence Research, GMInsights, Future Market Insights, Markets and Markets, Zion Market Research, Polaris Market Research, Verified Market Research, Statista, Fortune Business Insights
- ABSOLUTELY NO company performance charts, logos, product images, corporate photos, or charts from consulting firms/blogs
- Tailor trend analysis to company's specific offerings - avoid purely generic industry overviews

IMAGE REQUIREMENTS - MANDATORY MINIMUM:
- MINIMUM REQUIRED: AT LEAST 2 market trend graphs/charts with real quantitative data
- TARGET: 3-5 high-quality charts if available
- PREFERRED: Images from the 10 trusted research domains listed above
- ACCEPTABLE: If preferred sources yield no results after multiple searches, use reputable industry publications or market research sites with real market data
- MANDATORY CONTENT: Each image MUST show quantitative market data (specific numbers, CAGR percentages, market size in billions, growth projections with years)
- ALWAYS REJECT: Corporate logos, executive photos, product images, generic icons, conceptual illustrations without data
- VALIDATION: Title and description must reference specific market metrics shown in the chart

CRITICAL: You MUST perform at least 5 different image searches with varied keywords for the industry sector.
Try searches like:
- "[industry] market size forecast"
- "[sector] CAGR projection chart"
- "[market] growth analysis graph statista"
- "[industry] market research grandviewresearch"
- "[sector] market outlook precedenceresearch"

DO NOT give up after one search - keep trying with different search terms until you find at least 2 suitable charts.
Only if you've exhausted all search variations and truly cannot find ANY market charts with data, then document the search attempts made.

IMPORTANT: The LinkedIn company profile analysis should provide crucial context for evaluating strategic fit of all identified trends and opportunities.
"""


def get_claude_analysis_prompt(company_name: str, research_data: dict, company_info=None) -> str:
    """
    Generate the analysis prompt for Claude AI

    Args:
        company_name: Name of the company to analyze
        research_data: Research data from Perplexity AI
        company_info: Additional company information (optional)

    Returns:
        Formatted prompt string for Claude AI
    """
    company_context = ""
    if company_info:
        company_context = f"""
**COMPANY INFORMATION:**
- Company: {company_info.name}
- LinkedIn: {company_info.url_linkedin}
- Website: {company_info.url_sito}
- Location: {company_info.citta}, {company_info.nazione}
- Sector: {company_info.settore}
- Type: {company_info.tipo_azienda.value}
"""

    return f"""
You are a senior business analyst. Based on the comprehensive market research provided below, create a structured analysis that transforms this data into actionable business intelligence.

{company_context}
**RESEARCH DATA:**
{research_data}

You must respond with a valid JSON object that follows this exact structure:

{{
  "company_name": "{company_name}",
  "analysis_date": "{datetime.now().strftime('%Y-%m-%d')}",
  "executive_summary": "ULTRA-CONCISE summary (max 40 words) highlighting the most promising market trends and investment opportunities",
  "investment_trends": [
    {{
      "trend_name": "Name of emerging market trend",
      "investment_priority": "High/Medium/Low",
      "market_size_usd_billions": 150.2,
      "cagr_percentage": 18.5,
      "time_period": "2024-2030",
      "investment_required_millions": 500,
      "expected_roi_percentage": 25.0,
      "description": "CONCISE 1-line trend description (max 20 words) explaining why it's a major opportunity",
      "market_drivers": ["driver1", "driver2", "driver3"],
      "key_players": ["Leading Company1", "Startup2", "TechCorp3"],
      "implementation_timeline": "BRIEF timeline (max 15 words)",
      "strategic_fit": "BRIEF fit with company capabilities (max 15 words)"
    }}
  ],
  "key_strategic_recommendations": [
    "CONCISE Recommendation 1 with timeline (max 25 words)",
    "CONCISE Recommendation 2 with investment focus (max 25 words)",
    "CONCISE Recommendation 3 with risk focus (max 25 words)"
  ],
  "implementation_priorities": [
    "Priority 1: BRIEF action (max 15 words) - 6 months",
    "Priority 2: BRIEF action (max 15 words) - 12 months",
    "Priority 3: BRIEF action (max 15 words) - 24 months"
  ],
  "visual_data": [
    {{
      "title": "Market Trend Chart Title (must contain growth/trend data)",
      "source_url": "ONLY real, verified TREND CHART URLs from research - NO logos/photos - MARKET DATA ONLY",
      "description": "BRIEF trend chart description showing CAGR/growth data (max 15 words)",
      "relevance": "BRIEF strategic relevance to market trends (max 12 words)"
    }}
  ]

  CRITICAL: visual_data array MUST contain AT LEAST 3 chart objects with different verified URLs from market research firms
}}

**CRITICAL INSTRUCTIONS:**
1. Extract all quantitative data (market sizes, CAGR rates, growth projections) from the research
2. Keep ALL text fields extremely concise - this must fit on ONE PowerPoint slide
3. Include CAGR data wherever available with specific time periods
4. Focus on actionable insights with numbers and timelines
5. Prioritize trends and recommendations by revenue impact
6. IMAGE STRATEGY - Two-tier approach:
   - FIRST: Search for charts from the 10 preferred sources (grandviewresearch.com, precedenceresearch.com, gminsights.com, futuremarketinsights.com, marketsandmarkets.com, zionmarketresearch.com, polarismarketresearch.com, verifiedmarketresearch.com, statista.com, fortunebusinessinsights.com)
   - IF NO RESULTS: Accept charts from other reputable sources that show quantitative market data
7. IMAGE VALIDATION: Each chart must show real market data (numbers, CAGR%, market size, growth rates) - NO logos, photos, generic illustrations
8. Include 3-5 chart URLs that display actual market trend data with visible metrics
9. DO NOT generate fictional image links - only include real URLs found in research data
10. Make sure all JSON is valid and properly formatted
11. Maximum brevity while maintaining all critical strategic information

Respond ONLY with the JSON structure - no additional text before or after.
"""
