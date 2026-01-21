"""
API client for communicating with the inference backend
"""

import requests
from typing import Dict, List, Optional, Any
from datetime import datetime


class InferenceAPIClient:
    """Client for Uriscan Inference API"""
    
    def __init__(self, base_url: str):
        """
        Initialize API client
        
        Args:
            base_url: Base URL of the inference API
        """
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api/v1"
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check API health status
        
        Returns:
            Health status dictionary
        """
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_recent_submissions_from_knoxxi(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent submission details from Knoxxi API
        
        Args:
            limit: Number of recent submissions to fetch
            
        Returns:
            List of submission dictionaries with id and timestamp
        """
        try:
            response = requests.get(
                f"{self.api_base}/submissions/recent",
                params={"limit": limit},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Return full submission objects
            submissions = data.get('submissions', [])
            
            # Format: [{"id": "abc123...", "createdAt": "2026-01-20T16:08:59"}, ...]
            return submissions
            
        except Exception as e:
            print(f"Error fetching recent submissions: {e}")
            return []
        
    def run_inference(self, submission_id: str) -> Dict[str, Any]:
        """
        Run inference on a submission
        
        Args:
            submission_id: Submission ID to run inference on
            
        Returns:
            Inference results dictionary
        """
        try:
            response = requests.post(
                f"{self.api_base}/inference/{submission_id}",
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Submission {submission_id} not found")
            raise
        except Exception as e:
            raise Exception(f"Inference failed: {str(e)}")
    
    def get_submissions(
        self,
        limit: int = 50,
        offset: int = 0,
        min_agreement: Optional[float] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        sort_by: str = "timestamp",
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        """
        Get list of tracked submissions
        
        Args:
            limit: Maximum results to return
            offset: Number of results to skip
            min_agreement: Minimum agreement percentage filter
            start_date: Start date filter (ISO format)
            end_date: End date filter (ISO format)
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            
        Returns:
            Dictionary with submissions list and pagination info
        """
        try:
            params = {
                "limit": limit,
                "offset": offset,
                "sort_by": sort_by,
                "sort_order": sort_order
            }
            
            if min_agreement is not None:
                params["min_agreement"] = min_agreement
            
            if start_date:
                params["start_date"] = start_date
            
            if end_date:
                params["end_date"] = end_date
            
            response = requests.get(
                f"{self.api_base}/tracking/submissions",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to fetch submissions: {str(e)}")
    
    def get_submission_detail(self, submission_id: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific submission
        
        Args:
            submission_id: Submission ID
            
        Returns:
            Detailed submission dictionary
        """
        try:
            response = requests.get(
                f"{self.api_base}/tracking/submissions/{submission_id}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Submission {submission_id} not found in tracking database")
            raise
        except Exception as e:
            raise Exception(f"Failed to fetch submission details: {str(e)}")