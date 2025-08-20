import asyncio
import argparse
import os
from playwright.async_api import async_playwright
from typing import Dict, Any, List, Optional

from .test_generator import generate_basic_load_test
from .jmeter_exporter import export_to_jmx
from .loadrunner_exporter import export_to_loadrunner

async def extract_forms(page) -> List[Dict[str, Any]]:
    forms_data = []
    for form in await page.locator('form').all():
        form_details = {
            'id': await form.get_attribute('id'),
            'class': await form.get_attribute('class'),
            'action': await form.get_attribute('action'),
            'inputs': [],
            'buttons': [],
            'selects': [],
            'textareas': []
        }
        for inp in await form.locator('input').all():
            form_details['inputs'].append({
                'type': await inp.get_attribute('type'),
                'name': await inp.get_attribute('name'),
                'id': await inp.get_attribute('id'),
                'placeholder': await inp.get_attribute('placeholder'),
            })
        for btn in await form.locator('button').all():
             form_details['buttons'].append({
                'type': await btn.get_attribute('type'),
                'id': await btn.get_attribute('id'),
                'text': await btn.inner_text(),
            })
        for sel in await form.locator('select').all():
             form_details['selects'].append({
                'name': await sel.get_attribute('name'),
                'id': await sel.get_attribute('id'),
                'options': [await o.get_attribute('value') for o in await sel.locator('option').all()]
            })
        for ta in await form.locator('textarea').all():
             form_details['textareas'].append({
                'name': await ta.get_attribute('name'),
                'id': await ta.get_attribute('id'),
            })
        forms_data.append(form_details)
    return forms_data

async def extract_standalone_buttons(page) -> List[Dict[str, Any]]:
    buttons_data = []
    for btn in await page.locator('button:not(form button)').all():
        buttons_data.append({
            'id': await btn.get_attribute('id'),
            'class': await btn.get_attribute('class'),
            'text': await btn.inner_text(),
        })
    return buttons_data

async def extract_nav_links(page) -> List[Dict[str, Any]]:
    links_data = []
    for link in await page.locator('.side_categories ul li a').all():
        links_data.append({
            'href': await link.get_attribute('href'),
            'text': (await link.inner_text()).strip(),
            'id': await link.get_attribute('id'),
        })
    return links_data

async def analyze_page(url: str, browser = None) -> Dict[str, Any]:
    """
    Launches a headless browser if one isn't provided, navigates to the URL,
    extracts components, and returns them as a structured dictionary.
    """
    analysis_result = {'url': url, 'forms': [], 'buttons': [], 'nav_links': []}

    async def get_page_analysis(a_browser):
        page = await a_browser.new_page()
        try:
            print(f"Navigating to {url}...")
            await page.goto(url, timeout=60000)
            print("Page loaded. Starting component extraction...")
            analysis_result['forms'] = await extract_forms(page)
            analysis_result['buttons'] = await extract_standalone_buttons(page)
            analysis_result['nav_links'] = await extract_nav_links(page)
            print("Component extraction complete.")
            return analysis_result
        finally:
            # We only close the page, not the browser, as the browser might be shared
            await page.close()

    try:
        if browser:
            # Use the provided browser instance
            return await get_page_analysis(browser)
        else:
            # Create and manage a new browser instance
            async with async_playwright() as p:
                new_browser = await p.chromium.launch()
                try:
                    return await get_page_analysis(new_browser)
                finally:
                    await new_browser.close()
    except Exception as e:
        print(f"An error occurred during analysis: {e}")
        return {'error': str(e)}

async def main():
    parser = argparse.ArgumentParser(description="AI-Powered Performance Test Case Generator")
    parser.add_argument(
        '--format',
        type=str,
        choices=['jmeter', 'loadrunner'],
        default='jmeter',
        help='The output format for the generated test script.'
    )
    args = parser.parse_args()

    url = "http://books.toscrape.com/"

    print(f"Starting to analyze page: {url}")
    # Pass no browser instance to use the standalone mode
    analysis_data = await analyze_page(url=url)

    if 'error' in analysis_data:
        print(f"\\n--- Analysis Failed: {analysis_data['error']} ---")
        return

    print("Generating test case from analysis...")
    test_case_data = generate_basic_load_test(analysis_data)

    print(f"Exporting test case to {args.format.capitalize()} format...")

    if args.format == 'jmeter':
        jmx_content = export_to_jmx(test_case_data)
        output_filename = "test_plan.jmx"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(jmx_content)
        print(f"\\n--- Export Successful ---")
        print(f"JMeter test plan has been saved to: {os.path.abspath(output_filename)}")
        print("---------------------------")
    elif args.format == 'loadrunner':
        script_name = "GeneratedLRScript"
        export_to_loadrunner(test_case_data, script_name, output_dir=".")
        print("\\n--- Export Complete ---")

if __name__ == "__main__":
    asyncio.run(main())
