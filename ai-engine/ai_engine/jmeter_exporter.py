import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Dict, Any
from urllib.parse import urlparse

def _pretty_print_xml(elem) -> str:
    """Returns a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def _create_string_prop(name: str, value: str) -> ET.Element:
    """Helper to create a JMeter stringProp element."""
    el = ET.Element("stringProp", {"name": name})
    el.text = value
    return el

def _create_bool_prop(name: str, value: bool) -> ET.Element:
    """Helper to create a JMeter boolProp element."""
    el = ET.Element("boolProp", {"name": name})
    el.text = str(value).lower()
    return el

def export_to_jmx(test_case_data: Dict[str, Any]) -> str:
    """
    Exports a test case dictionary to a JMeter .jmx file format (XML string).
    """
    # Root element
    jmeter_test_plan = ET.Element("jmeterTestPlan", {"version": "1.2", "properties": "5.0", "jmeter": "5.5"})
    hash_tree = ET.SubElement(jmeter_test_plan, "hashTree")

    # Test Plan
    test_plan = ET.SubElement(hash_tree, "TestPlan", {"guiclass": "TestPlanGui", "testclass": "TestPlan", "testname": test_case_data.get("test_case_name", "Generated Test Plan"), "enabled": "true"})
    test_plan.append(_create_bool_prop("TestPlan.functional_mode", False))
    test_plan.append(_create_bool_prop("TestPlan.serialize_threadgroups", False))

    # Main HashTree for the Test Plan
    test_plan_hash_tree = ET.SubElement(hash_tree, "hashTree")

    # Thread Group
    load_profile = test_case_data.get("load_profile", {})
    thread_group = ET.SubElement(test_plan_hash_tree, "ThreadGroup", {"guiclass": "ThreadGroupGui", "testclass": "ThreadGroup", "testname": "Load Test Users", "enabled": "true"})
    thread_group.append(_create_string_prop("ThreadGroup.on_sample_error", "continue"))

    # Loop controller for thread group
    loop_controller = ET.SubElement(thread_group, "elementProp", {"name": "ThreadGroup.main_controller", "elementType": "LoopController", "guiclass": "LoopControlPanel", "testclass": "LoopController", "testname": "Loop Controller", "enabled": "true"})
    loop_controller.append(_create_bool_prop("LoopController.continue_forever", False))
    loop_controller.append(_create_string_prop("LoopController.loops", "1"))

    # Thread group properties
    thread_group.append(_create_string_prop("ThreadGroup.num_threads", str(load_profile.get("concurrent_users", 1))))
    thread_group.append(_create_string_prop("ThreadGroup.ramp_time", str(load_profile.get("ramp_up_seconds", 1))))
    thread_group.append(_create_bool_prop("ThreadGroup.scheduler", True))
    thread_group.append(_create_string_prop("ThreadGroup.duration", str(load_profile.get("duration_seconds", 60))))

    # HashTree for the Thread Group
    thread_group_hash_tree = ET.SubElement(test_plan_hash_tree, "hashTree")

    # HTTP Samplers for each step
    for i, step in enumerate(test_case_data.get("steps", [])):
        url = urlparse(step.get("target", ""))

        http_sampler = ET.SubElement(thread_group_hash_tree, "HTTPSamplerProxy", {"guiclass": "HttpTestSampleGui", "testclass": "HTTPSamplerProxy", "testname": f"Request {i+1} - {step.get('text', url.path)}", "enabled": "true"})

        sampler_args = ET.SubElement(http_sampler, "elementProp", {"name": "HTTPsampler.Arguments", "elementType": "Arguments", "guiclass": "HTTPArgumentsPanel", "testclass": "Arguments", "enabled": "true"})
        ET.SubElement(sampler_args, "collectionProp", {"name": "Arguments.arguments"})

        http_sampler.append(_create_string_prop("HTTPSampler.domain", url.hostname or ""))
        http_sampler.append(_create_string_prop("HTTPSampler.port", str(url.port or (443 if url.scheme == 'https' else 80))))
        http_sampler.append(_create_string_prop("HTTPSampler.protocol", url.scheme or "http"))
        http_sampler.append(_create_string_prop("HTTPSampler.path", url.path or "/"))
        http_sampler.append(_create_string_prop("HTTPSampler.method", step.get("action", "GET")))
        http_sampler.append(_create_bool_prop("HTTPSampler.follow_redirects", True))
        http_sampler.append(_create_bool_prop("HTTPSampler.auto_redirects", False))
        http_sampler.append(_create_bool_prop("HTTPSampler.use_keepalive", True))
        http_sampler.append(_create_bool_prop("HTTPSampler.DO_MULTIPART_POST", False))
        http_sampler.append(_create_string_prop("HTTPSampler.embedded_url_re", ""))
        http_sampler.append(_create_string_prop("HTTPSampler.connect_timeout", ""))
        http_sampler.append(_create_string_prop("HTTPSampler.response_timeout", ""))

        # HashTree for the sampler
        ET.SubElement(thread_group_hash_tree, "hashTree")

    return _pretty_print_xml(jmeter_test_plan)
