import asyncio
import json
from playwright.async_api import async_playwright
from typing import Dict, Any, List

from .test_generator import generate_basic_load_test

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
        # Extract inputs within the form
        for inp in await form.locator('input').all():
            form_details['inputs'].append({
                'type': await inp.get_attribute('type'),
                'name': await inp.get_attribute('name'),
                'id': await inp.get_attribute('id'),
                'placeholder': await inp.get_attribute('placeholder'),
            })
        # Extract buttons within the form
        for btn in await form.locator('button').all():
             form_details['buttons'].append({
                'type': await btn.get_attribute('type'),
                'id': await btn.get_attribute('id'),
                'text': await btn.inner_text(),
            })
        # Extract selects within the form
        for sel in await form.locator('select').all():
             form_details['selects'].append({
                'name': await sel.get_attribute('name'),
                'id': await sel.get_attribute('id'),
                'options': [await o.get_attribute('value') for o in await sel.locator('option').all()]
            })
        # Extract textareas within the form
        for ta in await form.locator('textarea').all():
             form_details['textareas'].append({
                'name': await ta.get_attribute('name'),
                'id': await ta.get_attribute('id'),
            })
        forms_data.append(form_details)
    return forms_data

async def extract_standalone_buttons(page) -> List[Dict[str, Any]]:
    buttons_data = []
    # Find buttons that are not inside a form
    for btn in await page.locator('button:not(form button)').all():
        buttons_data.append({
            'id': await btn.get_attribute('id'),
            'class': await btn.get_attribute('class'),
            'text': await btn.inner_text(),
        })
    return buttons_data

async def extract_nav_links(page) -> List[Dict[str, Any]]:
    links_data = []
    # Using a more specific selector for the category sidebar on books.toscrape.com
    for link in await page.locator('.side_categories ul li a').all():
        links_data.append({
            'href': await link.get_attribute('href'),
            'text': (await link.inner_text()).strip(),
            'id': await link.get_attribute('id'),
        })
    return links_data


async def analyze_page(url: str) -> Dict[str, Any]:
    """
    Launches a headless browser, navigates to the URL, extracts components,
    and returns them as a structured dictionary.
    """
    analysis_result = {'url': url, 'forms': [], 'buttons': [], 'nav_links': []}
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            print(f"Navigating to {url}...")
            await page.goto(url, timeout=60000)
            print("Page loaded. Starting component extraction...")

            analysis_result['forms'] = await extract_forms(page)
            analysis_result['buttons'] = await extract_standalone_buttons(page)
            analysis_result['nav_links'] = await extract_nav_links(page)

            print("Component extraction complete.")
            return analysis_result
        except Exception as e:
            print(f"An error occurred: {e}")
            return {'error': str(e)}
        finally:
            await browser.close()
            print("Browser closed.")

async def main():
    """
    Main function to test the page analysis and test generation logic.
    """
    url = "http://books.toscrape.com/"
    print(f"Starting to analyze page: {url}")
    analysis_data = await analyze_page(url)

    if 'error' in analysis_data:
        print(f"\\n--- Analysis Failed: {analysis_data['error']} ---")
        return

    print("\\n--- Analysis Successful ---")

    print("Generating test case from analysis...")
    test_case_data = generate_basic_load_test(analysis_data)
    print("Test case generation complete.")

    final_output = {
        "component_analysis": analysis_data,
        "generated_test_case": test_case_data
    }

    print("\\n--- Final Output ---")
    # Pretty print the combined JSON
    print(json.dumps(final_output, indent=2))
    print("----------------------")


if __name__ == "__main__":
    asyncio.run(main())
