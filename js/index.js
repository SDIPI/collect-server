/*
This file is part of wdf-server.
*/
const puppeteer = require('puppeteer');

let url = process.argv[2];

if (!url) {
    console.error("Error: You should provide an URL to load as an argument.");
    process.exit(1);
}

(async() => {
    try {
        const browser = await puppeteer.launch();
        const page = await browser.newPage();
        page.setViewport({width: 1366, height: 768, deviceScaleFactor: 1});
        await page.goto(url, {waitUntil: 'networkidle2'});
        await page.waitFor(2000);

        let bodyHTML = await page.evaluate(() => document.documentElement.outerHTML);

        console.log(bodyHTML);
        browser.close();
    } catch (e) {
        console.error(e);
        process.exit(1);
        browser.close();
    }
})();