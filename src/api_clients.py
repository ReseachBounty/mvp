"""
API clients for Perplexity AI and Anthropic Claude
"""

import os
import json
import requests
import anthropic
import time
import logging
from typing import Dict, Any
from requests.exceptions import RequestException, Timeout, ConnectionError

from .prompts import get_perplexity_research_prompt, get_claude_analysis_prompt
from .logging_config import get_context_logger

# Configure module logger
logger = logging.getLogger("analysis_service")


class PerplexityClient:
    """Client for Perplexity AI API"""

    def __init__(self, api_key: str = None, timeout: int = None, max_retries: int = None):
        """
        Initialize Perplexity client

        Args:
            api_key: Perplexity API key (defaults to env variable)
            timeout: Request timeout in seconds (defaults to PERPLEXITY_TIMEOUT env var or 120)
            max_retries: Maximum number of retry attempts (defaults to PERPLEXITY_MAX_RETRIES env var or 3)
        """
        self.api_key = api_key or os.getenv('PERPLEXITY_API_KEY')
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not found")

        self.url = "https://api.perplexity.ai/chat/completions"
        self.model = "sonar-reasoning-pro"

        # Read timeout from env var or use provided/default value
        if timeout is None:
            self.timeout = int(os.getenv('PERPLEXITY_TIMEOUT', '120'))
        else:
            self.timeout = timeout

        # Read max_retries from env var or use provided/default value
        if max_retries is None:
            self.max_retries = int(os.getenv('PERPLEXITY_MAX_RETRIES', '3'))
        else:
            self.max_retries = max_retries

        logger.info(f"Perplexity client initialized with timeout={self.timeout}s, max_retries={self.max_retries}")

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
        log = get_context_logger(company_name=company_name)
        log.info("Starting Perplexity API research", api_name="perplexity", step="research_start")

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

        log.info("Payload prepared",
                 api_name="perplexity",
                 model=self.model,
                 prompt_length=len(prompt),
                 timeout=self.timeout)

        # Retry logic with exponential backoff
        last_exception = None
        for attempt in range(1, self.max_retries + 1):
            try:
                start_time = time.time()

                log.info(f"API call attempt {attempt}/{self.max_retries}",
                        api_name="perplexity",
                        attempt=attempt,
                        max_retries=self.max_retries)

                response = requests.post(
                    self.url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout  # CRITICAL: Add timeout to prevent hanging
                )

                duration_ms = int((time.time() - start_time) * 1000)

                # Log response details
                log.info("Received API response",
                        api_name="perplexity",
                        status_code=response.status_code,
                        duration_ms=duration_ms,
                        response_size=len(response.content))

                response.raise_for_status()

                result = response.json()

                # Log successful completion
                log.info("Perplexity research completed successfully",
                        api_name="perplexity",
                        duration_ms=duration_ms,
                        attempt=attempt,
                        step="research_complete")

                return result

            except Timeout as e:
                last_exception = e
                log.error(f"Timeout on attempt {attempt}/{self.max_retries}",
                         api_name="perplexity",
                         error_type="timeout",
                         attempt=attempt,
                         timeout=self.timeout,
                         exc_info=True)

            except ConnectionError as e:
                last_exception = e
                log.error(f"Connection error on attempt {attempt}/{self.max_retries}",
                         api_name="perplexity",
                         error_type="connection_error",
                         attempt=attempt,
                         exc_info=True)

            except RequestException as e:
                last_exception = e
                log.error(f"Request exception on attempt {attempt}/{self.max_retries}",
                         api_name="perplexity",
                         error_type="request_exception",
                         attempt=attempt,
                         status_code=getattr(e.response, 'status_code', None),
                         exc_info=True)

            except Exception as e:
                last_exception = e
                log.error(f"Unexpected error on attempt {attempt}/{self.max_retries}",
                         api_name="perplexity",
                         error_type=type(e).__name__,
                         attempt=attempt,
                         exc_info=True)

            # Exponential backoff before retry (except on last attempt)
            if attempt < self.max_retries:
                backoff_time = min(2 ** attempt, 30)  # Max 30 seconds
                log.info(f"Retrying in {backoff_time} seconds",
                        api_name="perplexity",
                        backoff_seconds=backoff_time,
                        attempt=attempt)
                time.sleep(backoff_time)

        # All retries failed
        log.error("All retry attempts failed for Perplexity API",
                 api_name="perplexity",
                 total_attempts=self.max_retries,
                 step="research_failed")
        raise last_exception


class ClaudeClient:
    """Client for Anthropic Claude API"""

    def __init__(self, api_key: str = None, timeout: float = None, max_retries: int = None):
        """
        Initialize Claude client

        Args:
            api_key: Anthropic API key (defaults to env variable)
            timeout: Request timeout in seconds (defaults to CLAUDE_TIMEOUT env var or 180.0)
            max_retries: Maximum number of retry attempts (defaults to CLAUDE_MAX_RETRIES env var or 3)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found")

        # Read timeout from env var or use provided/default value
        if timeout is None:
            self.timeout = float(os.getenv('CLAUDE_TIMEOUT', '180.0'))
        else:
            self.timeout = timeout

        # Read max_retries from env var or use provided/default value
        if max_retries is None:
            self.max_retries = int(os.getenv('CLAUDE_MAX_RETRIES', '3'))
        else:
            self.max_retries = max_retries

        # Initialize with timeout configuration
        self.client = anthropic.Anthropic(
            api_key=self.api_key,
            timeout=self.timeout,
            max_retries=self.max_retries
        )
        self.model = "claude-sonnet-4-20250514"
        self.max_tokens = 15000

        logger.info(f"Claude client initialized with timeout={self.timeout}s, max_retries={self.max_retries}")

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
        log = get_context_logger(company_name=company_name)
        log.info("Starting Claude API analysis", api_name="claude", step="analysis_start")

        prompt = get_claude_analysis_prompt(company_name, research_data, company_info)

        log.info("Analysis prompt prepared",
                 api_name="claude",
                 model=self.model,
                 max_tokens=self.max_tokens,
                 prompt_length=len(prompt))

        start_time = time.time()

        try:
            log.info("Calling Claude API", api_name="claude")

            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            duration_ms = int((time.time() - start_time) * 1000)

            # Extract response text
            response_text = self._extract_text(message.content)

            # Log success metrics
            log.info("Claude analysis completed successfully",
                    api_name="claude",
                    duration_ms=duration_ms,
                    response_length=len(response_text),
                    input_tokens=getattr(message.usage, 'input_tokens', None),
                    output_tokens=getattr(message.usage, 'output_tokens', None),
                    step="analysis_complete")

            return response_text

        except anthropic.APITimeoutError as e:
            duration_ms = int((time.time() - start_time) * 1000)
            log.error("Claude API timeout",
                     api_name="claude",
                     error_type="timeout",
                     duration_ms=duration_ms,
                     timeout=self.timeout,
                     exc_info=True)
            raise

        except anthropic.APIConnectionError as e:
            duration_ms = int((time.time() - start_time) * 1000)
            log.error("Claude API connection error",
                     api_name="claude",
                     error_type="connection_error",
                     duration_ms=duration_ms,
                     exc_info=True)
            raise

        except anthropic.RateLimitError as e:
            duration_ms = int((time.time() - start_time) * 1000)
            log.error("Claude API rate limit exceeded",
                     api_name="claude",
                     error_type="rate_limit",
                     duration_ms=duration_ms,
                     exc_info=True)
            raise

        except anthropic.APIError as e:
            duration_ms = int((time.time() - start_time) * 1000)
            log.error("Claude API error",
                     api_name="claude",
                     error_type="api_error",
                     duration_ms=duration_ms,
                     status_code=getattr(e, 'status_code', None),
                     exc_info=True)
            raise

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            log.error("Unexpected error during Claude analysis",
                     api_name="claude",
                     error_type=type(e).__name__,
                     duration_ms=duration_ms,
                     exc_info=True)
            raise

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
