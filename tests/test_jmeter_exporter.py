import pytest
import xml.etree.ElementTree as ET
from ai_engine.jmeter_exporter import export_to_jmx

@pytest.fixture
def sample_test_case_data():
    """Provides a sample generated test case for testing the exporter."""
    return {
        "test_case_name": "Sample Test Case",
        "test_type": "LoadTest",
        "target_application_url": "http://sample.com",
        "load_profile": {
            "concurrent_users": 50,
            "duration_seconds": 30,
            "ramp_up_seconds": 5,
        },
        "steps": [
            {"action": "GET", "target": "http://sample.com/home"},
            {"action": "GET", "target": "http://sample.com/about"},
        ]
    }

def test_exports_to_valid_jmx_structure(sample_test_case_data):
    """
    Tests that the exported JMX string is a well-formed XML and has the
    correct basic structure and values.
    """
    jmx_output = export_to_jmx(sample_test_case_data)

    # Check if it's valid XML by attempting to parse it
    try:
        root = ET.fromstring(jmx_output)
    except ET.ParseError as e:
        pytest.fail(f"JMX output is not well-formed XML: {e}\\nOutput was:\\n{jmx_output}")

    # Check for the root element
    assert root.tag == "jmeterTestPlan"

    # Find ThreadGroup and check its properties
    # The .// syntax means "find at any level below the current element"
    thread_group = root.find(".//ThreadGroup")
    assert thread_group is not None, "ThreadGroup element not found"

    num_threads = thread_group.find("./stringProp[@name='ThreadGroup.num_threads']")
    assert num_threads is not None and num_threads.text == "50"

    duration = thread_group.find("./stringProp[@name='ThreadGroup.duration']")
    assert duration is not None and duration.text == "30"

    ramp_time = thread_group.find("./stringProp[@name='ThreadGroup.ramp_time']")
    assert ramp_time is not None and ramp_time.text == "5"

    # Find HTTP Samplers and check their properties
    http_samplers = root.findall(".//HTTPSamplerProxy")
    assert len(http_samplers) == 2, "Incorrect number of HTTP Samplers found"

    # Check properties of the first sampler
    first_sampler = http_samplers[0]
    sampler_domain = first_sampler.find("./stringProp[@name='HTTPSampler.domain']")
    sampler_path = first_sampler.find("./stringProp[@name='HTTPSampler.path']")

    assert sampler_domain is not None and sampler_domain.text == "sample.com"
    assert sampler_path is not None and sampler_path.text == "/home"

    # Check properties of the second sampler
    second_sampler = http_samplers[1]
    sampler_domain_2 = second_sampler.find("./stringProp[@name='HTTPSampler.domain']")
    sampler_path_2 = second_sampler.find("./stringProp[@name='HTTPSampler.path']")

    assert sampler_domain_2 is not None and sampler_domain_2.text == "sample.com"
    assert sampler_path_2 is not None and sampler_path_2.text == "/about"
