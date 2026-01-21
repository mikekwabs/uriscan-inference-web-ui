"""
Formatting utilities for the dashboard
"""

from datetime import datetime
from typing import Optional


def format_timestamp(timestamp_str: Optional[str]) -> str:
    """
    Format ISO timestamp to readable format
    
    Args:
        timestamp_str: ISO format timestamp string
        
    Returns:
        Formatted timestamp string
    """
    if not timestamp_str:
        return "N/A"
    
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp_str


def format_percentage(value: Optional[float], decimals: int = 1) -> str:
    """
    Format percentage value
    
    Args:
        value: Percentage value (0-100)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    if value is None:
        return "N/A"
    
    return f"{value:.{decimals}f}%"


def get_agreement_indicator(agreement_pct: float) -> str:
    """
    Get colored indicator based on agreement percentage
    
    Args:
        agreement_pct: Agreement percentage (0-100)
        
    Returns:
        Emoji indicator
    """
    if agreement_pct >= 80:
        return "🟢"
    elif agreement_pct >= 50:
        return "🟡"
    else:
        return "🔴"


def get_agreement_badge(agreement: bool) -> str:
    """
    Get badge for agreement status
    
    Args:
        agreement: Agreement boolean
        
    Returns:
        Badge string
    """
    return "✅" if agreement else "❌"


def get_status_badge(status: str) -> str:
    """
    Get badge for model status
    
    Args:
        status: Model status (production/shadow_mode)
        
    Returns:
        Badge emoji
    """
    if status == "production":
        return "🟦"  # Blue square for production
    elif status == "shadow_mode":
        return "🟨"  # Yellow square for shadow
    else:
        return "⬜"  # White square for unknown