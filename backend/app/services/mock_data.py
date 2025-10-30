"""
Mock data for development mode - simulates API responses without making real calls
"""

def get_mock_perplexity_response(company_name: str, company_type: str = "startup") -> dict:
    """
    Returns mock Perplexity research results

    Args:
        company_name: Name of the company
        company_type: Type of company (startup, pmi, etc.)

    Returns:
        Mock Perplexity API response
    """
    return {
        "id": "mock-perplexity-id",
        "model": "sonar",
        "created": 1234567890,
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 500,
            "total_tokens": 600
        },
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "finish_reason": "stop",
                "message": {
                    "role": "assistant",
                    "content": f"""# Market Research Report: {company_name}

## Company Overview
{company_name} is a dynamic {company_type} operating in the technology sector. The company has shown significant growth potential and demonstrates strong market positioning within its niche.

## Market Analysis

### Industry Trends
The technology sector is experiencing rapid transformation driven by digital innovation, AI integration, and changing consumer behaviors. Key trends include:

- **Digital Transformation**: Accelerating adoption of cloud-based solutions and digital platforms
- **AI Integration**: Growing implementation of artificial intelligence and machine learning capabilities
- **Remote Work**: Continued shift towards distributed workforces and digital collaboration tools
- **Sustainability Focus**: Increasing emphasis on environmentally sustainable technology solutions

### Competitive Landscape
The competitive environment is characterized by:

1. **Established Players**: Large enterprise companies with significant market share
2. **Emerging Startups**: Innovative new entrants disrupting traditional business models
3. **Market Consolidation**: Ongoing M&A activity as companies seek strategic advantages
4. **Technology Differentiation**: Competition increasingly based on technological capabilities

### Market Size & Growth
- Current market size: Estimated at $15-20 billion
- Annual growth rate: 12-15% CAGR
- Projected market size (5 years): $25-35 billion
- Geographic expansion opportunities in emerging markets

## Customer Insights

### Target Demographics
- **Primary**: Enterprise customers (500+ employees)
- **Secondary**: Mid-market companies (50-500 employees)
- **Tertiary**: Small businesses and startups

### Customer Needs
Key customer requirements include:
- Scalable and reliable solutions
- Cost-effective pricing models
- Integration with existing systems
- Strong customer support and training
- Data security and compliance

### Pain Points
Common challenges faced by customers:
- Legacy system integration difficulties
- High implementation costs
- Limited technical expertise internally
- Concerns about data privacy and security
- Need for customization and flexibility

## Technology & Innovation

### Current Technology Stack
{company_name} leverages modern technology including:
- Cloud infrastructure (AWS/Azure/GCP)
- Microservices architecture
- API-first design principles
- Advanced data analytics and ML capabilities

### Innovation Focus Areas
- Artificial Intelligence and Machine Learning
- Process automation and efficiency
- Enhanced user experience and interface design
- Mobile-first solutions
- Integration capabilities

### R&D Investment
The company invests 15-20% of revenue in research and development, focusing on next-generation features and capabilities.

## Financial Outlook

### Revenue Projections
- Year 1: $5-8M
- Year 2: $12-18M
- Year 3: $25-35M
- Year 5: $50-75M

### Funding & Investment
- Recent funding rounds have attracted $10-15M in venture capital
- Strong investor interest from tier-1 VCs
- Potential for Series B funding within 18-24 months

### Key Financial Metrics
- Gross margins: 70-75%
- Customer acquisition cost: $5,000-8,000
- Lifetime value: $50,000-75,000
- Churn rate: 5-8% annually

## Strategic Recommendations

### Short-term Actions (0-12 months)
1. **Product Development**: Focus on core feature enhancement and user experience
2. **Market Penetration**: Expand sales and marketing efforts in key markets
3. **Customer Success**: Build robust customer support and success programs
4. **Strategic Partnerships**: Develop partnerships with complementary technology providers

### Medium-term Actions (12-36 months)
1. **Market Expansion**: Enter new geographic markets and customer segments
2. **Product Diversification**: Develop adjacent products and services
3. **Team Building**: Scale the organization with key hires in engineering, sales, and operations
4. **Infrastructure**: Invest in scalable infrastructure and operational systems

### Long-term Vision (3-5 years)
1. **Market Leadership**: Establish position as category leader
2. **Platform Strategy**: Evolve into a platform business model
3. **Ecosystem Development**: Build partner and developer ecosystems
4. **Strategic Exit Options**: Prepare for IPO or strategic acquisition

## Risk Factors

### Market Risks
- Competitive pressure from established players
- Rapid technology changes requiring continuous innovation
- Economic downturns affecting customer spending

### Operational Risks
- Scaling challenges as the organization grows
- Key person dependencies
- Technology infrastructure reliability

### Regulatory Risks
- Data privacy regulations (GDPR, CCPA, etc.)
- Industry-specific compliance requirements
- Changing regulatory landscape

## Conclusion

{company_name} demonstrates strong potential for growth and market success. The company operates in a expanding market with favorable trends, has a differentiated offering, and shows evidence of product-market fit. With continued execution and strategic focus, the company is well-positioned to capture significant market share and achieve sustainable growth.

Key success factors include:
- Maintaining technology leadership and innovation
- Building a scalable go-to-market engine
- Developing a strong company culture and team
- Securing adequate funding for growth initiatives
- Executing strategic partnerships and ecosystem development

**Overall Assessment**: Positive outlook with strong growth potential, manageable risks, and clear path to market leadership.
"""
                }
            }
        ]
    }


def get_mock_claude_response(company_name: str) -> str:
    """
    Returns mock Claude analysis results as JSON string

    Args:
        company_name: Name of the company

    Returns:
        JSON string with mock analysis
    """
    return """{
  "company_name": "%s",
  "executive_summary": {
    "overview": "Mock analysis for %s demonstrates strong market positioning with significant growth opportunities in the technology sector. The company shows promising indicators across multiple dimensions including market fit, competitive advantages, and financial viability.",
    "key_highlights": [
      "Strong product-market fit with growing customer base",
      "Experienced leadership team with proven track record",
      "Differentiated technology platform with competitive moats",
      "Large addressable market with favorable growth trends",
      "Clear path to profitability and sustainable unit economics"
    ],
    "overall_assessment": "The company presents a compelling investment opportunity with balanced risk-reward profile. Recommended for further due diligence and potential partnership discussions."
  },
  "market_opportunity": {
    "market_size": {
      "current_tam": "$20B",
      "projected_tam_5y": "$35B",
      "serviceable_market": "$8B",
      "target_market_share": "5-8%%"
    },
    "growth_drivers": [
      "Digital transformation accelerating across industries",
      "Increasing demand for automation and efficiency tools",
      "Shift to cloud-based and SaaS business models",
      "Growing investment in technology infrastructure"
    ],
    "market_trends": [
      {
        "trend": "AI and Machine Learning Integration",
        "impact": "High",
        "description": "Rapid adoption of AI capabilities creating new opportunities for differentiation and value creation"
      },
      {
        "trend": "Remote Work and Digital Collaboration",
        "impact": "Medium-High",
        "description": "Sustained shift to distributed work models driving demand for digital solutions"
      },
      {
        "trend": "Data Privacy and Security Focus",
        "impact": "Medium",
        "description": "Increasing regulatory requirements and customer concerns around data protection"
      }
    ]
  },
  "competitive_analysis": {
    "competitive_position": "Strong Challenger",
    "key_competitors": [
      {
        "name": "Enterprise Leader Corp",
        "market_share": "25%%",
        "strengths": ["Brand recognition", "Large customer base", "Extensive features"],
        "weaknesses": ["Legacy technology", "High pricing", "Slow innovation"]
      },
      {
        "name": "Growth Startup Inc",
        "market_share": "8%%",
        "strengths": ["Modern UX", "Rapid iteration", "Competitive pricing"],
        "weaknesses": ["Limited features", "Scale challenges", "Small team"]
      }
    ],
    "competitive_advantages": [
      "Superior user experience and product design",
      "Advanced technology stack and architecture",
      "Strong customer relationships and retention",
      "Flexible and customizable platform"
    ],
    "differentiation": "The company differentiates through a combination of superior technology, customer-centric design, and flexible implementation that addresses key market gaps left by legacy providers."
  },
  "business_model": {
    "revenue_model": "SaaS subscription with tiered pricing",
    "pricing_strategy": "Value-based pricing with emphasis on ROI",
    "customer_segments": [
      {
        "segment": "Enterprise",
        "percentage": 60,
        "avg_contract_value": "$75,000"
      },
      {
        "segment": "Mid-Market",
        "percentage": 30,
        "avg_contract_value": "$25,000"
      },
      {
        "segment": "SMB",
        "percentage": 10,
        "avg_contract_value": "$5,000"
      }
    ],
    "unit_economics": {
      "cac": "$8,000",
      "ltv": "$60,000",
      "ltv_cac_ratio": "7.5",
      "payback_period": "12 months",
      "gross_margin": "75%%"
    },
    "scalability_assessment": "High scalability potential with cloud infrastructure and automated operations. Marginal cost of serving additional customers is low."
  },
  "financial_projections": {
    "revenue_forecast": [
      {"year": "Year 1", "revenue": "$6M", "growth": "150%%"},
      {"year": "Year 2", "revenue": "$15M", "growth": "150%%"},
      {"year": "Year 3", "revenue": "$30M", "growth": "100%%"},
      {"year": "Year 5", "revenue": "$75M", "growth": "60%%"}
    ],
    "profitability_timeline": "Expected to reach profitability by end of Year 3 with positive unit economics throughout",
    "funding_requirements": {
      "amount_needed": "$15-20M",
      "use_of_funds": "60%% sales/marketing, 25%% product development, 15%% operations",
      "runway": "24-30 months"
    },
    "key_metrics": {
      "arr": "$4M",
      "mrr_growth": "15%% MoM",
      "customer_count": 85,
      "nrr": "120%%",
      "cac_payback": "12 months"
    }
  },
  "product_technology": {
    "product_description": "Cloud-based platform providing enterprise-grade solutions with modern architecture and user experience",
    "technology_stack": ["Cloud Infrastructure", "Microservices", "React/Node.js", "AI/ML capabilities", "API-first design"],
    "innovation_focus": [
      "AI-powered automation and insights",
      "Enhanced integration capabilities",
      "Mobile-first user experience",
      "Advanced analytics and reporting"
    ],
    "technical_moats": [
      "Proprietary algorithms and data models",
      "Extensive integration ecosystem",
      "Network effects from user base",
      "Accumulated customer data and insights"
    ],
    "product_roadmap": [
      {
        "feature": "AI Assistant",
        "timeline": "Q2 2025",
        "impact": "High"
      },
      {
        "feature": "Mobile App V2",
        "timeline": "Q3 2025",
        "impact": "Medium"
      },
      {
        "feature": "Enterprise API Suite",
        "timeline": "Q4 2025",
        "impact": "High"
      }
    ]
  },
  "team_organization": {
    "leadership_assessment": "Strong and experienced team with complementary skills and proven track records in scaling technology companies",
    "key_team_members": [
      {
        "role": "CEO/Founder",
        "background": "15 years experience, previous successful exit",
        "strength": "Vision and strategy"
      },
      {
        "role": "CTO",
        "background": "Former engineering leader at major tech company",
        "strength": "Technical excellence and architecture"
      },
      {
        "role": "VP Sales",
        "background": "Track record of building $50M+ sales organizations",
        "strength": "Go-to-market execution"
      }
    ],
    "organizational_strengths": [
      "Deep domain expertise",
      "Customer-centric culture",
      "Strong execution track record",
      "Balanced technical and business acumen"
    ],
    "hiring_needs": [
      "VP Marketing (Q1 2025)",
      "Head of Customer Success (Q2 2025)",
      "Senior Engineers (ongoing)"
    ]
  },
  "growth_strategy": {
    "go_to_market": {
      "primary_channels": ["Direct sales", "Partner channel", "Digital marketing"],
      "sales_strategy": "Enterprise-focused with land-and-expand approach",
      "marketing_approach": "Content-driven with strong thought leadership"
    },
    "expansion_plans": [
      {
        "initiative": "Geographic Expansion - Europe",
        "timeline": "Year 2",
        "investment": "$3M"
      },
      {
        "initiative": "New Product Line",
        "timeline": "Year 3",
        "investment": "$5M"
      }
    ],
    "partnership_strategy": [
      "Technology partnerships with major cloud providers",
      "Integration partnerships with complementary platforms",
      "Reseller partnerships for geographic expansion"
    ],
    "customer_acquisition": {
      "strategy": "Multi-channel approach combining inbound and outbound",
      "key_tactics": ["Content marketing", "SEO/SEM", "Events and conferences", "Partner referrals"],
      "success_metrics": ["Pipeline generation", "Conversion rates", "CAC trends"]
    }
  },
  "risks_challenges": {
    "market_risks": [
      {
        "risk": "Increased Competition",
        "severity": "Medium",
        "mitigation": "Continuous innovation and strong customer relationships"
      },
      {
        "risk": "Market Downturn",
        "severity": "Medium",
        "mitigation": "Diversified customer base and flexible cost structure"
      }
    ],
    "operational_risks": [
      {
        "risk": "Scaling Challenges",
        "severity": "Medium-High",
        "mitigation": "Invest in infrastructure and experienced leadership"
      },
      {
        "risk": "Key Person Risk",
        "severity": "Medium",
        "mitigation": "Build strong team and succession planning"
      }
    ],
    "technology_risks": [
      {
        "risk": "System Reliability",
        "severity": "Low-Medium",
        "mitigation": "Robust architecture and monitoring"
      }
    ],
    "regulatory_risks": [
      {
        "risk": "Data Privacy Regulations",
        "severity": "Medium",
        "mitigation": "Compliance-first approach and legal expertise"
      }
    ]
  },
  "investment_highlights": {
    "strengths": [
      "Large and growing addressable market",
      "Differentiated product with strong customer traction",
      "Experienced and proven leadership team",
      "Healthy unit economics and clear path to profitability",
      "Multiple expansion vectors for growth"
    ],
    "opportunities": [
      "Market leadership potential in emerging category",
      "Platform expansion opportunities",
      "Strategic partnership possibilities",
      "Geographic expansion potential"
    ],
    "concerns": [
      "Competitive intensity requiring sustained innovation",
      "Execution risk in scaling operations",
      "Market timing and adoption rate uncertainties"
    ]
  },
  "strategic_recommendations": {
    "immediate_priorities": [
      "Accelerate product development on key differentiators",
      "Scale sales and marketing engine",
      "Build customer success organization",
      "Secure Series B funding"
    ],
    "medium_term_focus": [
      "Expand into adjacent markets",
      "Develop partner ecosystem",
      "Invest in brand building",
      "Geographic expansion"
    ],
    "success_factors": [
      "Maintaining product innovation leadership",
      "Executing scalable go-to-market strategy",
      "Building exceptional team and culture",
      "Managing cash efficiently to extend runway"
    ],
    "exit_scenarios": [
      {
        "scenario": "Strategic Acquisition",
        "timeline": "3-5 years",
        "probability": "Medium-High"
      },
      {
        "scenario": "IPO",
        "timeline": "5-7 years",
        "probability": "Medium"
      }
    ]
  },
  "charts_visualizations": [
    {
      "title": "Revenue Growth Projection",
      "type": "bar_chart",
      "description": "5-year revenue forecast showing exponential growth trajectory",
      "data_summary": "Revenue growing from $6M to $75M over 5 years",
      "key_insight": "Strong growth trajectory with improving unit economics",
      "image_url": "https://via.placeholder.com/800x400/4F46E5/FFFFFF?text=Revenue+Growth+Chart"
    },
    {
      "title": "Market Share Analysis",
      "type": "pie_chart",
      "description": "Current competitive landscape and market positioning",
      "data_summary": "Market leader at 25%%, challenger positions at 8-12%%",
      "key_insight": "Significant opportunity to capture share from fragmented market",
      "image_url": "https://via.placeholder.com/800x400/10B981/FFFFFF?text=Market+Share+Analysis"
    },
    {
      "title": "Customer Acquisition Trends",
      "type": "line_chart",
      "description": "Monthly customer acquisition and churn rates",
      "data_summary": "Accelerating acquisition with improving retention metrics",
      "key_insight": "Product-market fit evidenced by strong retention and NPS",
      "image_url": "https://via.placeholder.com/800x400/F59E0B/FFFFFF?text=Customer+Growth+Trends"
    }
  ]
}""" % (company_name, company_name)
