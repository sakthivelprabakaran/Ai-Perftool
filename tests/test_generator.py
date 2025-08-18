import pytest
from ai_engine.test_generator import generate_basic_load_test

@pytest.fixture
def sample_analysis_data():
    """Provides a sample analysis JSON for testing."""
    return {
        "url": "http://testsite.com/",
        "nav_links": [
            {"href": "/page1", "text": "Page 1"},
            {"href": "page2.html", "text": "Page 2"},
            {"href": "http://externalsite.com/page3", "text": "Page 3"},
            {"href": None, "text": "Invalid Link"},
        ]
    }

def test_generates_basic_load_test_from_nav_links(sample_analysis_data):
    """
    Tests the happy path where analysis data is complete and well-formed.
    """
    test_case = generate_basic_load_test(sample_analysis_data)

    assert "test_case_name" in test_case
    assert test_case["test_type"] == "LoadTest"
    assert "load_profile" in test_case

    # It should generate 3 steps, skipping the one with a null href
    assert len(test_case["steps"]) == 3

    steps = test_case["steps"]
    assert steps[0]["target"] == "http://testsite.com/page1"
    assert steps[1]["target"] == "http://testsite.com/page2.html"
    assert steps[2]["target"] == "http://externalsite.com/page3"

def test_handles_missing_data_gracefully():
    """
    Tests that the generator handles incomplete or empty analysis data
    without crashing.
    """
    # Test with no nav_links key
    no_links_data = {"url": "http://testsite.com"}
    test_case_no_links = generate_basic_load_test(no_links_data)
    assert "No test case generated" in test_case_no_links["test_case_name"]

    # Test with empty nav_links list
    empty_links_data = {"url": "http://testsite.com", "nav_links": []}
    test_case_empty_links = generate_basic_load_test(empty_links_data)
    assert "No test case generated" in test_case_empty_links["test_case_name"]

    # Test with no URL key
    no_url_data = {"nav_links": [{"href": "/page1", "text": "Page 1"}]}
    test_case_no_url = generate_basic_load_test(no_url_data)
    assert "No test case generated" in test_case_no_url["test_case_name"]
