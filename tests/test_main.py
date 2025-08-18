import pytest
from playwright.async_api import async_playwright
from ai_engine.main import extract_forms, extract_standalone_buttons, extract_nav_links

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio

async def test_extract_nav_links():
    html_content = """
    <html>
        <body>
            <div class="side_categories">
                <ul>
                    <li><a href="cat1.html">Category 1</a></li>
                    <li><a href="cat2.html">Category 2 </a></li>
                </ul>
            </div>
            <a href="lonely.html">Lonely Link</a>
        </body>
    </html>
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html_content)
        links = await extract_nav_links(page)
        await browser.close()

    assert len(links) == 2
    assert links[0]['text'] == 'Category 1'
    assert links[0]['href'] == 'cat1.html'
    assert links[1]['text'] == 'Category 2'

async def test_extract_forms():
    html_content = """
    <html>
        <body>
            <form id="loginForm" action="/login">
                <input type="text" name="username" placeholder="User" />
                <input type="password" name="password" />
                <button type="submit">Login</button>
            </form>
        </body>
    </html>
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html_content)
        forms = await extract_forms(page)
        await browser.close()

    assert len(forms) == 1
    form = forms[0]
    assert form['id'] == 'loginForm'
    assert form['action'] == '/login'

    assert len(form['inputs']) == 2
    assert form['inputs'][0]['name'] == 'username'
    assert form['inputs'][0]['placeholder'] == 'User'
    assert form['inputs'][1]['type'] == 'password'

    assert len(form['buttons']) == 1
    assert form['buttons'][0]['text'] == 'Login'

async def test_extract_standalone_buttons():
    html_content = """
    <html>
        <body>
            <button id="btn1">Click Me</button>
            <form>
                <button id="btn2">Submit</button>
            </form>
        </body>
    </html>
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html_content)
        buttons = await extract_standalone_buttons(page)
        await browser.close()

    assert len(buttons) == 1
    assert buttons[0]['id'] == 'btn1'
    assert buttons[0]['text'] == 'Click Me'
