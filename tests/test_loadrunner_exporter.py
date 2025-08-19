import pytest
import os
import xml.etree.ElementTree as ET
from ai_engine.loadrunner_exporter import export_to_loadrunner

@pytest.fixture
def sample_test_case_data():
    """Provides a sample generated test case for testing the exporter."""
    return {
        "test_case_name": "Sample LR Test Case",
        "steps": [
            {"action": "GET", "target": "http://sample.com/home", "text": "Homepage"},
            {"action": "GET", "target": "http://sample.com/about", "text": "About Us"},
        ]
    }

def test_exports_to_valid_loadrunner_structure(sample_test_case_data, tmp_path):
    """
    Tests that the exporter creates the correct directory structure and that
    the file contents are as expected.
    """
    script_name = "TestScript1"
    output_dir = tmp_path

    export_to_loadrunner(sample_test_case_data, script_name, output_dir)

    script_path = output_dir / script_name

    # 1. Assert that the directory and all files were created
    assert script_path.is_dir()

    expected_files = [
        "Action.c",
        "vuser_init.c",
        "vuser_end.c",
        "globals.h",
        "default.cfg",
        "default.usp",
        f"{script_name}.usr",
        "ScriptUploadMetadata.xml",
        "Bookmarks.xml",
        "Breakpoints.xml",
    ]

    for filename in expected_files:
        assert (script_path / filename).is_file(), f"{filename} was not created"

    # 2. Assert the content of Action.c
    action_c_content = (script_path / "Action.c").read_text()
    assert 'web_url("Request 1_Homepage"' in action_c_content
    assert '"URL=http://sample.com/home"' in action_c_content
    assert 'web_url("Request 2_About Us"' in action_c_content
    assert '"URL=http://sample.com/about"' in action_c_content

    # 3. Assert the content of the metadata XML
    metadata_content = (script_path / "ScriptUploadMetadata.xml").read_text()
    try:
        root = ET.fromstring(metadata_content)
    except ET.ParseError as e:
        pytest.fail(f"ScriptUploadMetadata.xml is not well-formed XML: {e}")

    assert root.find(".//ScriptName").text == script_name
    action_files = root.findall(".//ActionFiles/FileEntry")
    assert len(action_files) == 3

    general_files = root.findall(".//GeneralFiles/FileEntry")
    # Check for a few key files
    assert any(f.get("Name") == f"{script_name}.usr" for f in general_files)
    assert any(f.get("Name") == "default.cfg" for f in general_files)
