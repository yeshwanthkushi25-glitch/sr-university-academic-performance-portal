const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

async function capture() {
  const assetsDir = path.join(__dirname, '..', 'assets', 'screenshots');
  if (!fs.existsSync(assetsDir)) {
    fs.mkdirSync(assetsDir, { recursive: true });
  }

  console.log('Launching Chrome...');
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    defaultViewport: { width: 1440, height: 1000, deviceScaleFactor: 2 }
  });

  const page = await browser.newPage();

  // 1. Student Evaluation Form
  console.log('1. Navigating to Student Evaluation Form (http://127.0.0.1:5000/)...');
  await page.goto('http://127.0.0.1:5000/', { waitUntil: 'networkidle0', timeout: 30000 });
  await new Promise(r => setTimeout(r, 2000));
  
  const formPath = path.join(assetsDir, '01_student_evaluation_form.png');
  await page.screenshot({ path: formPath, fullPage: false });
  console.log('Saved 01_student_evaluation_form.png');

  // 2. Performance Analysis Dashboard
  console.log('2. Switching to Performance Analysis Dashboard...');
  await page.evaluate(() => {
    if (typeof switchTab === 'function') switchTab('dashboard');
  });
  await new Promise(r => setTimeout(r, 3000)); // wait for charts to animate

  const dashPath = path.join(assetsDir, '02_performance_analysis_dashboard.png');
  await page.screenshot({ path: dashPath, fullPage: false });
  console.log('Saved 02_performance_analysis_dashboard.png');

  // 3. Advisor & Faculty Portal
  console.log('3. Switching to Advisor & Faculty Portal...');
  await page.evaluate(() => {
    if (typeof switchTab === 'function') switchTab('faculty');
  });
  await new Promise(r => setTimeout(r, 3000)); // wait for charts & table to load

  const facultyPath = path.join(assetsDir, '03_advisor_faculty_portal.png');
  await page.screenshot({ path: facultyPath, fullPage: false });
  console.log('Saved 03_advisor_faculty_portal.png');

  // 4. Secure Auth Portal (Login)
  console.log('4. Navigating to Login Portal (http://127.0.0.1:5000/login)...');
  await page.goto('http://127.0.0.1:5000/login', { waitUntil: 'networkidle0', timeout: 30000 });
  await new Promise(r => setTimeout(r, 1500));

  const authPath = path.join(assetsDir, '04_secure_auth_portal.png');
  await page.screenshot({ path: authPath, fullPage: false });
  console.log('Saved 04_secure_auth_portal.png');

  await browser.close();
  console.log('All 4 demo screenshots captured successfully!');
}

capture().catch(err => {
  console.error('Error capturing screenshots:', err);
  process.exit(1);
});
