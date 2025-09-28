import json
import os
from datetime import datetime
from typing import List, Dict, Any

# For now, we'll use JSON files as a simple database
# In production, you'd use a proper database like PostgreSQL or MongoDB

LOGS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'analysis_logs.json')
USERS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'users.json')

def ensure_data_dir():
    """Ensure data directory exists"""
    data_dir = os.path.dirname(LOGS_FILE)
    os.makedirs(data_dir, exist_ok=True)

def load_logs() -> List[Dict[str, Any]]:
    """Load logs from file"""
    ensure_data_dir()
    if not os.path.exists(LOGS_FILE):
        return []
    
    try:
        with open(LOGS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_logs(logs: List[Dict[str, Any]]):
    """Save logs to file"""
    ensure_data_dir()
    with open(LOGS_FILE, 'w') as f:
        json.dump(logs, f, indent=2, default=str)

def create_analysis_log(user_id: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new analysis log entry"""
    logs = load_logs()
    
    log_entry = {
        'id': len(logs) + 1,
        'user_id': user_id,
        'timestamp': datetime.now().isoformat(),
        'file_name': analysis_data.get('filename', 'Unknown'),
        'file_type': analysis_data.get('file_type', 'Unknown'),
        'analysis_type': analysis_data.get('analysis_type', 'comprehensive'),
        'authenticity_score': analysis_data.get('authenticity_score', 0),
        'ai_detection_score': analysis_data.get('ai_detection', {}).get('ai_generated_score', 0),
        'domain_classification': analysis_data.get('domain_classification', {}),
        'status': 'completed',
        'results': analysis_data
    }
    
    logs.append(log_entry)
    save_logs(logs)
    
    return log_entry

def get_user_analysis_logs(user_id: str) -> List[Dict[str, Any]]:
    """Get all analysis logs for a specific user"""
    logs = load_logs()
    return [log for log in logs if log.get('user_id') == user_id]

def get_all_analysis_logs() -> List[Dict[str, Any]]:
    """Get all analysis logs (admin only)"""
    return load_logs()

def get_user_stats(user_id: str) -> Dict[str, Any]:
    """Get statistics for a user"""
    user_logs = get_user_analysis_logs(user_id)
    
    if not user_logs:
        return {
            'total_analyses': 0,
            'avg_authenticity_score': 0,
            'avg_ai_detection_score': 0,
            'most_common_domain': 'None',
            'analysis_history': []
        }
    
    total_analyses = len(user_logs)
    avg_authenticity = sum(log.get('authenticity_score', 0) for log in user_logs) / total_analyses
    avg_ai_detection = sum(log.get('ai_detection_score', 0) for log in user_logs) / total_analyses
    
    # Find most common domain
    domains = [log.get('domain_classification', {}).get('category', 'Unknown') for log in user_logs]
    most_common_domain = max(set(domains), key=domains.count) if domains else 'Unknown'
    
    return {
        'total_analyses': total_analyses,
        'avg_authenticity_score': round(avg_authenticity, 2),
        'avg_ai_detection_score': round(avg_ai_detection, 2),
        'most_common_domain': most_common_domain,
        'analysis_history': user_logs[-10:]  # Last 10 analyses
    }
