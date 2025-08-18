from typing import Dict, Any
from urllib.parse import urljoin

def generate_basic_load_test(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a basic load test case from the analysis data.

    The strategy is to create a simple load test that hits all
    discovered navigation links.
    """
    base_url = analysis_data.get("url")
    nav_links = analysis_data.get("nav_links", [])

    if not base_url or not nav_links:
        return {
            "test_case_name": "No test case generated",
            "reason": "Missing base URL or no navigation links found in analysis.",
        }

    test_steps = []
    for link in nav_links:
        href = link.get("href")
        if not href:
            continue
        # Ensure the link is absolute
        absolute_url = urljoin(base_url, href)
        test_steps.append({
            "action": "GET",
            "target": absolute_url,
            "text": link.get("text", "")
        })

    test_case = {
        "test_case_name": f"Basic Load Test for {base_url}",
        "test_type": "LoadTest",
        "target_application_url": base_url,
        "load_profile": {
            "concurrent_users": 100,
            "duration_seconds": 60,
            "ramp_up_seconds": 10,
        },
        "steps": test_steps
    }

    return test_case
