import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .oauth_whoop import get_valid_token
from .config import load_env, get_env


class WhoopAPI:
    """Client for WHOOP API"""
    
    def __init__(self):
        load_env()
        self.base_url = get_env("WHOOP_API_URL", "https://api.prod.whoop.com/developer")
        self.access_token = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        if not self.access_token:
            self.access_token = get_valid_token()
        
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def _refresh_token_if_needed(self):
        """Refresh token if needed"""
        try:
            # Test current token
            test_response = requests.get(
                f"{self.base_url}/v1/user/profile/basic",
                headers=self._get_headers(),
                timeout=10
            )
            if test_response.status_code == 401:
                self.access_token = get_valid_token()
        except Exception:
            self.access_token = get_valid_token()
    
    def get_user_profile(self) -> Dict[str, Any]:
        """Get basic user profile"""
        self._refresh_token_if_needed()
        url = f"{self.base_url}/v1/user/profile/basic"
        response = requests.get(url, headers=self._get_headers(), timeout=30)
        response.raise_for_status()
        return response.json()
    
    def get_sleep_data(self, 
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get sleep data for date range"""
        self._refresh_token_if_needed()
        url = f"{self.base_url}/v1/cycle/sleep"
        
        params = {}
        if start_date:
            params["start"] = start_date
        if end_date:
            params["end"] = end_date
            
        response = requests.get(url, headers=self._get_headers(), params=params, timeout=30)
        response.raise_for_status()
        return response.json().get("sleep", [])
    
    def get_recovery_data(self,
                          start_date: Optional[str] = None,
                          end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recovery data for date range"""
        self._refresh_token_if_needed()
        url = f"{self.base_url}/v1/cycle/recovery"
        
        params = {}
        if start_date:
            params["start"] = start_date
        if end_date:
            params["end"] = end_date
            
        response = requests.get(url, headers=self._get_headers(), params=params, timeout=30)
        response.raise_for_status()
        return response.json().get("recovery", [])
    
    def get_workout_data(self,
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get workout data for date range"""
        self._refresh_token_if_needed()
        url = f"{self.base_url}/v1/cycle/workout"
        
        params = {}
        if start_date:
            params["start"] = start_date
        if end_date:
            params["end"] = end_date
            
        response = requests.get(url, headers=self._get_headers(), params=params, timeout=30)
        response.raise_for_status()
        return response.json().get("workout", [])
    
    def get_cycle_data(self,
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get cycle data for date range"""
        self._refresh_token_if_needed()
        url = f"{self.base_url}/v1/cycle"
        
        params = {}
        if start_date:
            params["start"] = start_date
        if end_date:
            params["end"] = end_date
            
        response = requests.get(url, headers=self._get_headers(), params=params, timeout=30)
        response.raise_for_status()
        return response.json().get("cycle", [])
    
    def get_metrics_summary(self,
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None) -> Dict[str, Any]:
        """Get summary metrics for date range"""
        self._refresh_token_if_needed()
        url = f"{self.base_url}/v1/cycle/metrics"
        
        params = {}
        if start_date:
            params["start"] = start_date
        if end_date:
            params["end"] = end_date
            
        response = requests.get(url, headers=self._get_headers(), params=params, timeout=30)
        response.raise_for_status()
        return response.json()


def get_whoop_client() -> WhoopAPI:
    """Get a configured WHOOP API client"""
    return WhoopAPI()
