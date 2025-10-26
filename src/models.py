"""
Pydantic models for structured data validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class MarketMetrics(BaseModel):
    """Market metrics for a trend or sector"""
    market_size_usd_billions: Optional[float] = Field(
        None,
        description="Market size in USD billions"
    )
    cagr_percentage: Optional[float] = Field(
        None,
        description="Compound Annual Growth Rate as percentage"
    )
    time_period: Optional[str] = Field(
        None,
        description="Time period for CAGR calculation"
    )
    growth_drivers: List[str] = Field(
        default_factory=list,
        description="Key factors driving growth"
    )


class TrendAnalysis(BaseModel):
    """Analysis of a market trend"""
    trend_name: str = Field(..., description="Name of the trend")
    description: str = Field(
        ...,
        description="1-2 line description of the trend and why it's interesting"
    )
    current_impact: str = Field(..., description="Current market impact")
    future_developments: str = Field(
        ...,
        description="Possible future developments and opportunities"
    )
    market_metrics: MarketMetrics
    key_players: List[str] = Field(
        default_factory=list,
        description="Key companies in this trend"
    )


class InvestmentTrend(BaseModel):
    """Investment opportunity trend"""
    trend_name: str = Field(..., description="Name of the investment trend")
    investment_priority: str = Field(
        ...,
        description="High/Medium/Low investment priority"
    )
    market_size_usd_billions: Optional[float] = Field(
        None,
        description="Market size in USD billions"
    )
    cagr_percentage: Optional[float] = Field(None, description="CAGR percentage")
    time_period: Optional[str] = Field(
        None,
        description="Time period for projections"
    )
    investment_required_millions: Optional[float] = Field(
        None,
        description="Required investment in millions"
    )
    expected_roi_percentage: Optional[float] = Field(
        None,
        description="Expected ROI percentage"
    )
    description: str = Field(..., description="Description of the trend")
    market_drivers: List[str] = Field(
        default_factory=list,
        description="Market drivers"
    )
    key_players: List[str] = Field(
        default_factory=list,
        description="Key players in the market"
    )
    implementation_timeline: Optional[str] = Field(
        None,
        description="Implementation timeline"
    )
    strategic_fit: Optional[str] = Field(
        None,
        description="Strategic fit assessment"
    )


class MarketSector(BaseModel):
    """Market sector analysis"""
    sector_name: str = Field(..., description="Name of the market sector")
    strategic_importance: str = Field(
        ...,
        description="High/Medium/Low strategic importance"
    )
    revenue_contribution_percentage: Optional[float] = Field(
        None,
        description="Revenue contribution as percentage"
    )
    market_metrics: MarketMetrics
    current_trends: List[TrendAnalysis] = Field(
        default_factory=list,
        description="Current trends in this sector"
    )
    opportunities: List[str] = Field(
        default_factory=list,
        description="Growth opportunities"
    )
    threats: List[str] = Field(
        default_factory=list,
        description="Potential threats"
    )
    competitive_position: Optional[str] = Field(
        None,
        description="Company's position in this sector"
    )


class VisualData(BaseModel):
    """Visual data (chart/graph) reference"""
    title: str = Field(..., description="Title/description of the visual")
    source_url: Optional[str] = Field(None, description="URL to the chart/graph")
    description: str = Field(
        ...,
        description="Description of what the visual shows"
    )
    relevance: str = Field(
        ...,
        description="How this visual relates to the company/trends"
    )


class StructuredAnalysis(BaseModel):
    """Complete structured analysis for a company"""
    company_name: str = Field(..., description="Name of the analyzed company")
    analysis_date: str = Field(..., description="Date of analysis")
    executive_summary: str = Field(
        ...,
        description="Brief executive summary of key findings"
    )
    investment_trends: List[InvestmentTrend] = Field(
        default_factory=list,
        description="All identified investment trends"
    )
    key_strategic_recommendations: List[str] = Field(
        default_factory=list,
        description="Top strategic recommendations"
    )
    implementation_priorities: List[str] = Field(
        default_factory=list,
        description="Implementation priorities with timeline"
    )
    visual_data: List[VisualData] = Field(
        default_factory=list,
        description="Charts, graphs and visual data"
    )
