# Databricks notebook source
"""
Advanced Table Extraction for Financial Documents
"""

import pdfplumber
import pandas as pd
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class TableExtractor:
    def __init__(self):
        self.settings = {
            'vertical_strategy': 'lines',
            'horizontal_strategy': 'lines',
            'snap_tolerance': 3,
            'join_tolerance': 3,
            'edge_min_length': 3,
            'min_words_vertical': 3,
            'min_words_horizontal': 1,
        }
    
    def extract_tables_from_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Extract tables from PDF using pdfplumber
        More accurate than OCR for native PDFs
        """
        tables = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables(self.settings)
                    
                    for table_num, table in enumerate(page_tables):
                        if table and len(table) > 1:  # At least header + 1 row
                            # Convert to DataFrame
                            df = pd.DataFrame(table[1:], columns=table[0])
                            
                            # Clean data
                            df = df.dropna(how='all')  # Remove empty rows
                            df = df.fillna('')  # Fill NaN with empty string
                            
                            tables.append({
                                'page': page_num + 1,
                                'table_number': table_num + 1,
                                'data': df.to_dict('records'),
                                'dataframe': df,
                                'rows': len(df),
                                'cols': len(df.columns),
                                'headers': list(df.columns)
                            })
                            
                            logger.info(f"  Table {table_num + 1} on page {page_num + 1}: {len(df)} rows × {len(df.columns)} cols")
        
        except Exception as e:
            logger.error(f"Table extraction error: {e}")
        
        return tables
    
    def format_table_as_text(self, table: Dict) -> str:
        """Format table as readable text"""
        df = table['dataframe']
        return df.to_string(index=False)
    
    def extract_financial_metrics(self, tables: List[Dict]) -> Dict:
        """
        Extract common financial metrics from tables
        Looks for keywords: Revenue, Profit, EPS, etc.
        """
        metrics = {
            'revenue': [],
            'profit': [],
            'eps': [],
            'assets': [],
            'liabilities': [],
            'equity': []
        }
        
        keywords = {
            'revenue': ['revenue', 'sales', 'total revenue'],
            'profit': ['net income', 'profit', 'earnings'],
            'eps': ['eps', 'earnings per share'],
            'assets': ['total assets', 'assets'],
            'liabilities': ['total liabilities', 'liabilities'],
            'equity': ['shareholders equity', "stockholders' equity", 'equity']
        }
        
        for table in tables:
            df = table['dataframe']
            
            for metric, search_terms in keywords.items():
                for term in search_terms:
                    # Search in first column (usually labels)
                    if len(df.columns) >= 2:
                        matches = df[df.iloc[:, 0].str.lower().str.contains(term, na=False)]
                        
                        if not matches.empty:
                            # Extract values from subsequent columns
                            for col in df.columns[1:]:
                                value = matches[col].iloc[0]
                                if value and str(value).strip():
                                    metrics[metric].append({
                                        'label': matches.iloc[0, 0],
                                        'value': value,
                                        'column': col,
                                        'page': table['page']
                                    })
        
        return metrics