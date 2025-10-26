"""
API clients for Perplexity AI and Anthropic Claude
"""

import os
import json
import requests
import anthropic
from typing import Dict, Any

from .prompts import get_perplexity_research_prompt, get_claude_analysis_prompt


class PerplexityClient:
    """Client for Perplexity AI API"""

    def __init__(self, api_key: str = None):
        """
        Initialize Perplexity client

        Args:
            api_key: Perplexity API key (defaults to env variable)
        """
        self.api_key = api_key or os.getenv('PERPLEXITY_API_KEY')
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not found")

        self.url = "https://api.perplexity.ai/chat/completions"
        self.model = "sonar-reasoning-pro"

    def research_company(
        self,
        company_name: str,
        company_linkedin: str = None,
        company_website: str = None,
        country: str = None,
        city: str = None,
        sector: str = None,
        company_type: str = None
    ) -> Dict[str, Any]:
        """
        Conduct market research for a company

        Args:
            company_name: Name of the company to research
            company_linkedin: LinkedIn URL (optional)
            company_website: Company website URL (optional)
            country: Country where the company is based (optional)
            city: City where the company is based (optional)
            sector: Industry sector (optional)
            company_type: Type of company (startup, pmi, etc.) (optional)

        Returns:
            Research results as dictionary
        """
        prompt = get_perplexity_research_prompt(
            company_name,
            company_linkedin,
            company_website,
            country,
            city,
            sector,
            company_type
        )

        payload = {
            "model": self.model,
            "return_images": True,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(self.url, json=payload, headers=headers)
        response.raise_for_status()

        return response.json()


class ClaudeClient:
    """Client for Anthropic Claude API"""

    def __init__(self, api_key: str = None):
        """
        Initialize Claude client

        Args:
            api_key: Anthropic API key (defaults to env variable)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"
        self.max_tokens = 15000

    def analyze_research(
        self,
        company_name: str,
        research_data: Dict[str, Any],
        company_info = None
    ) -> str:
        """
        Analyze research data and generate structured insights

        Args:
            company_name: Name of the company
            research_data: Research data from Perplexity
            company_info: Additional company information (optional)

        Returns:
            Structured analysis as JSON string
        """
        prompt = get_claude_analysis_prompt(company_name, research_data, company_info)

        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return self._extract_text(message.content)

    @staticmethod
    def _extract_text(content) -> str:
        """
        Extract text from Claude response content

        Args:
            content: Response content from Claude

        Returns:
            Extracted text
        """
        if isinstance(content, list):
            text = "".join([
                block.text for block in content
                if hasattr(block, 'text') and block.text
            ])
        else:
            text = getattr(content, 'text', str(content))

        # Handle JSON wrapped in markdown code blocks
        text = text.strip()
        if text.startswith('```json'):
            lines = text.split('\n')
            if lines[0].startswith('```') and lines[-1].strip() == '```':
                return '\n'.join(lines[1:-1])
        elif text.startswith('```'):
            lines = text.split('\n')
            if lines[0].startswith('```') and lines[-1].strip() == '```':
                return '\n'.join(lines[1:-1])

        return text
