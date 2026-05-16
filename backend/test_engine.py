# File: backend/test_engine.py
from typing import List, Dict, Any

class TestEngine:
    """
    AGENT_TEST core logic.
    Handles Unit Tests and E2E Browser Test generation.
    """
    
    def generate_unit_tests(self, table_name: str) -> str:
        name = table_name.capitalize().rstrip('s')
        return f"""# File: tests/test_{table_name}.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_{table_name}_list():
    response = client.get("/{table_name}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_{table_name}_unauthorized():
    response = client.post("/{table_name}", json={{"name": "test"}})
    # Expecting 401 since we have auth middleware
    assert response.status_code == 401
"""

    def generate_e2e_tests(self, project_name: str) -> str:
        return f"""// File: tests/e2e/basic.spec.js
const {{ test, expect }} = require('@playwright/test');

test('homepage has title and login button', async ({{ page }}) => {{
  await page.goto('http://localhost:3000');
  await expect(page).toHaveTitle(/{project_name}/i);
  
  const loginButton = page.getByRole('button', {{ name: /sign in/i }});
  await expect(loginButton).toBeVisible();
}});
"""

    def generate_github_workflow(self) -> str:
        return """# File: .github/workflows/e2e.yml
name: Playwright Tests
on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-node@v3
      with:
        node-version: 18
    - name: Install dependencies
      run: npm install
    - name: Install Playwright Browsers
      run: npx playwright install --with-deps
    - name: Run Playwright tests
      run: npx playwright test
    - uses: actions/upload-artifact@v3
      if: always()
      with:
        name: playwright-report
        path: playwright-report/
        retention-days: 30
"""

agent_test = TestEngine()
