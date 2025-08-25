import os
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import requests

from .config import load_env, get_env, read_tokens, write_tokens


class CopilotMoneyAPI:
    """Client for Copilot Money API"""
    
    def __init__(self):
        load_env()
        self.base_url = get_env("COPILOT_API_URL", "https://api.copilot.money")
        self.api_key = get_env("COPILOT_API_KEY")
        
        if not self.api_key:
            raise RuntimeError("COPILOT_API_KEY must be set in environment or .env")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_accounts(self) -> List[Dict[str, Any]]:
        """Get all financial accounts"""
        url = f"{self.base_url}/v1/accounts"
        response = requests.get(url, headers=self._get_headers(), timeout=30)
        response.raise_for_status()
        return response.json().get("accounts", [])
    
    def get_transactions(self, 
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None,
                        account_id: Optional[str] = None,
                        limit: int = 100) -> List[Dict[str, Any]]:
        """Get transactions with optional filtering"""
        url = f"{self.base_url}/v1/transactions"
        
        params = {"limit": limit}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if account_id:
            params["account_id"] = account_id
            
        response = requests.get(url, headers=self._get_headers(), params=params, timeout=30)
        response.raise_for_status()
        return response.json().get("transactions", [])
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get transaction categories"""
        url = f"{self.base_url}/v1/categories"
        response = requests.get(url, headers=self._get_headers(), timeout=30)
        response.raise_for_status()
        return response.json().get("categories", [])
    
    def get_insights(self, 
                     start_date: Optional[str] = None,
                     end_date: Optional[str] = None) -> Dict[str, Any]:
        """Get spending insights and analytics"""
        url = f"{self.base_url}/v1/insights"
        
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
            
        response = requests.get(url, headers=self._get_headers(), params=params, timeout=30)
        response.raise_for_status()
        return response.json()


def get_copilot_client() -> CopilotMoneyAPI:
    """Get a configured Copilot Money API client"""
    return CopilotMoneyAPI()
