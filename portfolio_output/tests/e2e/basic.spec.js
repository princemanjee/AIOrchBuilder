// File: tests/e2e/basic.spec.js
const { test, expect } = require('@playwright/test');

test('homepage has title and login button', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await expect(page).toHaveTitle(/p_r_prince_rehman_manjee,_ee,_mis_portfolio/i);
  
  const loginButton = page.getByRole('button', { name: /sign in/i });
  await expect(loginButton).toBeVisible();
});
