# agents/scraping_agent/sec_scraper.py

from sec_edgar_downloader import Downloader
from pathlib import Path
import re
from bs4 import BeautifulSoup
import os
import glob
import json
from typing import Dict, List, Optional
from datetime import datetime

def extract_main_filing_text(filepath, filing_type="10-K") -> str:
    """
    Extracts the main filing text block from an SEC .txt file (e.g., 10-K, 10-Q).
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Break the file into <DOCUMENT> blocks
    documents = re.findall(r"<DOCUMENT>(.*?)</DOCUMENT>", content, re.DOTALL)

    for doc in documents:
        # Check if this block is the one we want (10-K, 10-Q)
        type_match = re.search(r"<TYPE>(.*)", doc)
        if type_match and type_match.group(1).strip() == filing_type:
            # Extract the <TEXT> block
            text_match = re.search(r"<TEXT>(.*?)$", doc, re.DOTALL)
            if text_match:
                html_text = text_match.group(1)
                soup = BeautifulSoup(html_text, "html.parser")
                return soup.get_text()

    return "Filing section not found or unsupported format"

class FinancialExtractor:
    """Extract key financial information from SEC filings"""
    
    def __init__(self):
        # Key sections to look for in filings
        self.key_sections = {
            "10-K": [
                "Business Overview",
                "Risk Factors",
                "Selected Financial Data",
                "Management's Discussion and Analysis",
                "Financial Statements",
                "Market Risk"
            ],
            "10-Q": [
                "Financial Statements",
                "Management's Discussion and Analysis",
                "Quantitative and Qualitative Disclosures"
            ]
        }
        
        # Financial metrics patterns
        self.financial_patterns = {
            'revenue': [
                r'(?:total\s+)?(?:net\s+)?(?:revenues?|sales)\s*(?:were|was|of|:)?\s*\$?([\d,]+\.?\d*)\s*(?:million|billion)?',
                r'(?:total\s+)?(?:net\s+)?(?:revenues?|sales)\s*(?:increased|decreased|grew)\s*(?:by\s*)?\$?([\d,]+\.?\d*)\s*(?:million|billion)?'
            ],
            'net_income': [
                r'net\s+(?:income|earnings?)\s*(?:were|was|of|:)?\s*\$?([\d,]+\.?\d*)\s*(?:million|billion)?',
                r'net\s+(?:loss)\s*(?:were|was|of|:)?\s*\$?([\d,]+\.?\d*)\s*(?:million|billion)?'
            ],
            'cash': [
                r'cash\s+and\s+cash\s+equivalents?\s*(?:were|was|of|:)?\s*\$?([\d,]+\.?\d*)\s*(?:million|billion)?'
            ],
            'earnings_per_share': [
                r'(?:basic\s+)?(?:diluted\s+)?earnings?\s+per\s+share\s*(?:were|was|of|:)?\s*\$?([\d,]+\.?\d*)'
            ]
        }
    
    def extract_sections(self, text: str, filing_type: str) -> Dict[str, str]:
        """Extract key sections from filing text"""
        sections = {}
        
        # Common section patterns
        section_patterns = [
            r'Item\s+\d+[A-Z]?\.\s*(.*?)(?=Item\s+\d+[A-Z]?\.|\Z)',
            r'(?:^|\n)([A-Z\s]+(?:DISCUSSION|ANALYSIS|FACTORS|STATEMENTS|OVERVIEW).*?)(?=\n[A-Z\s]+(?:DISCUSSION|ANALYSIS|FACTORS|STATEMENTS|OVERVIEW)|\Z)'
        ]
        
        for pattern in section_patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple):
                    section_title = match[0].strip()[:100]  # First 100 chars as title
                    section_content = match[0] if len(match) == 1 else match[1]
                else:
                    section_title = match.strip()[:100]
                    section_content = match
                
                # Only keep sections that are substantial
                if len(section_content) > 500:
                    sections[section_title] = section_content[:5000]  # Limit section size
        
        return sections
    
    def extract_financial_metrics(self, text: str) -> Dict[str, any]:
        """Extract key financial metrics from text"""
        metrics = {}
        
        # Normalize text for better matching
        normalized_text = text.replace('\n', ' ').replace('\t', ' ')
        normalized_text = ' '.join(normalized_text.split())  # Multiple spaces to single
        
        for metric, patterns in self.financial_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, normalized_text, re.IGNORECASE)
                if matches:
                    # Take the first match and clean it
                    value = matches[0].replace(',', '')
                    try:
                        metrics[metric] = float(value)
                    except:
                        metrics[metric] = value
                    break
        
        return metrics
    
    def extract_key_insights(self, text: str, filing_type: str) -> Dict[str, any]:
        """Extract structured insights from filing"""
        
        # Extract sections
        sections = self.extract_sections(text, filing_type)
        
        # Extract financial metrics
        metrics = self.extract_financial_metrics(text)
        
        # Extract risk factors (first 3)
        risk_factors = []
        risk_pattern = r'(?:•|·|\d+\.)\s*([^•·\n]{50,300}(?:risk|uncertain|adverse|negatively|could harm).*?[.!?])'
        risk_matches = re.findall(risk_pattern, text, re.IGNORECASE)
        risk_factors = risk_matches[:3] if risk_matches else []
        
        # Extract business highlights
        highlights = []
        highlight_patterns = [
            r'(?:increased|grew|improved|achieved|reached|exceeded).*?(?:revenue|sales|income|earnings).*?[.!?]',
            r'(?:launched|introduced|developed|acquired|expanded).*?(?:product|service|market|business).*?[.!?]'
        ]
        
        for pattern in highlight_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            highlights.extend(matches[:2])  # Take first 2 matches per pattern
        
        # Create summary
        summary = {
            "filing_type": filing_type,
            "extraction_date": datetime.now().isoformat(),
            "financial_metrics": metrics,
            "risk_factors": risk_factors[:3],
            "business_highlights": highlights[:4],
            "key_sections": {k: v[:1000] for k, v in list(sections.items())[:5]}  # First 1000 chars of top 5 sections
        }
        
        return summary

class SECScrapingAgent:
    def __init__(self, email="rithikmotupalli@gmail.com"):
        self.download_dir = Path(__file__).resolve().parents[2] / "data_ingestion" / "sec_filings"
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.downloader = Downloader("Rithik Sai", email, download_folder=str(self.download_dir))
        self.extractor = FinancialExtractor()

    def _find_latest_txt_file(self, ticker: str, filing_type: str) -> str:
        """Find the most recently downloaded .txt file for the given ticker and filing type."""
        folder = self.download_dir / "sec-edgar-filings" / ticker.upper() / filing_type
        txt_files = sorted(folder.glob("*/full-submission.txt"), key=os.path.getmtime, reverse=True)
        if not txt_files:
            raise FileNotFoundError("No filing text file found for given ticker and filing type.")
        return str(txt_files[0])

    def download_filing(self, ticker: str, filing_type: str = "10-K"):
        """Download the latest SEC filing and extract main text."""
        try:
            self.downloader.get(filing_type, ticker, limit=1)

            txt_path = self._find_latest_txt_file(ticker, filing_type)
            clean_text = extract_main_filing_text(txt_path, filing_type)

            cleaned_file_path = self.download_dir / f"{ticker.upper()}_cleaned_{filing_type}.txt"
            with open(cleaned_file_path, "w", encoding="utf-8") as f:
                f.write(clean_text)

            return {
                "status": "success",
                "message": f"{filing_type} filing for {ticker} downloaded and cleaned.",
                "path": str(cleaned_file_path),
                "text_length": len(clean_text)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def extract_insights(self, ticker: str, filing_type: str = "10-K") -> Dict[str, any]:
        """Download filing and extract key insights"""
        try:
            # First, download the filing
            download_result = self.download_filing(ticker, filing_type)
            
            if download_result["status"] != "success":
                return download_result
            
            # Read the cleaned text
            with open(download_result["path"], 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Extract insights
            insights = self.extractor.extract_key_insights(text, filing_type)
            insights["ticker"] = ticker.upper()
            
            # Save insights to JSON
            insights_path = self.download_dir / f"{ticker.upper()}_insights_{filing_type}.json"
            with open(insights_path, 'w', encoding='utf-8') as f:
                json.dump(insights, f, indent=2)
            
            # Also create a markdown summary for LLM consumption
            summary_text = self._create_llm_summary(insights)
            summary_path = self.download_dir / f"{ticker.upper()}_summary_{filing_type}.md"
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary_text)
            
            return {
                "status": "success",
                "ticker": ticker.upper(),
                "filing_type": filing_type,
                "insights": insights,
                "insights_path": str(insights_path),
                "summary_path": str(summary_path),
                "full_text_path": download_result["path"]
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _create_llm_summary(self, insights: Dict) -> str:
        """Create a concise summary for LLM consumption"""
        summary = f"""# {insights['ticker']} {insights['filing_type']} Summary

        ## Financial Metrics
        """
        
        for metric, value in insights['financial_metrics'].items():
            summary += f"- **{metric.replace('_', ' ').title()}**: ${value:,.2f}\n" if isinstance(value, (int, float)) else f"- **{metric.replace('_', ' ').title()}**: {value}\n"
        
        summary += "\n## Key Risk Factors\n"
        for i, risk in enumerate(insights['risk_factors'], 1):
            summary += f"{i}. {risk}\n"
        
        summary += "\n## Business Highlights\n"
        for highlight in insights['business_highlights']:
            summary += f"- {highlight}\n"
        
        summary += f"\n*Extracted on: {insights['extraction_date']}*"
        
        return summary
    
    def prepare_for_vector_db(self, ticker: str, filing_type: str = "10-K") -> List[Dict]:
        """Prepare filing data as chunks for vector database"""
        try:
            # Get insights first
            result = self.extract_insights(ticker, filing_type)
            
            if result["status"] != "success":
                return []
            
            chunks = []
            
            # Create chunks from different sections
            # 1. Summary chunk
            chunks.append({
                "doc_id": f"{ticker}_{filing_type}_summary",
                "text": open(result["summary_path"], 'r', encoding='utf-8').read(),
                "metadata": {
                    "ticker": ticker,
                    "filing_type": filing_type,
                    "chunk_type": "summary",
                    "date": result["insights"]["extraction_date"]
                }
            })
            
            # 2. Create chunks from key sections
            for section_name, section_text in result["insights"]["key_sections"].items():
                chunk_id = f"{ticker}_{filing_type}_{section_name[:50].replace(' ', '_')}"
                chunks.append({
                    "doc_id": chunk_id,
                    "text": f"## {section_name}\n\n{section_text}",
                    "metadata": {
                        "ticker": ticker,
                        "filing_type": filing_type,
                        "chunk_type": "section",
                        "section": section_name,
                        "date": result["insights"]["extraction_date"]
                    }
                })
            
            # 3. Risk factors as individual chunks
            for i, risk in enumerate(result["insights"]["risk_factors"]):
                chunks.append({
                    "doc_id": f"{ticker}_{filing_type}_risk_{i+1}",
                    "text": f"Risk Factor: {risk}",
                    "metadata": {
                        "ticker": ticker,
                        "filing_type": filing_type,
                        "chunk_type": "risk_factor",
                        "date": result["insights"]["extraction_date"]
                    }
                })
            
            return chunks
            
        except Exception as e:
            print(f"Error preparing vector DB chunks: {e}")
            return []

# Temporary test
if __name__ == "__main__":
    agent = SECScrapingAgent()
    
    # Test extraction
    result = agent.extract_insights("AAPL", "10-K")
    
    if result["status"] == "success":
        print(f"✅ Successfully extracted insights for {result['ticker']}")
        print(f"📊 Financial Metrics: {result['insights']['financial_metrics']}")
        print(f"📄 Summary saved to: {result['summary_path']}")
        
        # Test vector DB preparation
        chunks = agent.prepare_for_vector_db("AAPL", "10-K")
        print(f"\n📦 Prepared {len(chunks)} chunks for vector database")
        for chunk in chunks[:3]:  # Show first 3 chunks
            print(f"  - {chunk['doc_id']}: {chunk['text'][:100]}...")
    else:
        print(f"❌ Error: {result['message']}")