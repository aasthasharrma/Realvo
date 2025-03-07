const fs = require("fs");
const path = require("path");
const axios = require("axios");
const cheerio = require("cheerio");
// const { findTickerNames } = require("./archive/findTickerNames.js");

const tickers = ["INVH"];
const USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
	'AppleWebKit/537.36 (KHTML, like Gecko) ' +
	'Chrome/51.0.2704.103 Safari/537.36';
const PROXY_URL = 'https://finned-proxy.mac-48b.workers.dev/?auth=$6nb9%@Su2KQrfQ@!P55&url=';

async function fetchData(url) {
  try {
      console.log(`Fetching data from ${url}`);
      const response = await axios.get(`${PROXY_URL}${encodeURIComponent(url)}`, {
          headers: { "User-Agent": USER_AGENT }
      });
      return response.data;
  } catch (error) {
      console.error(`Error fetching data from ${url}:`, error.message);
      return null;
  }
}

/**
 * Fetches total assets data, converts millions to billions, and saves as CSV.
 */
async function fetchAssets(ticker, companyName, tickerDir) {
  const url = `https://www.macrotrends.net/stocks/charts/${ticker}/${companyName}/total-assets`;
  console.log(`Fetching assets data from ${url}`);
  const html = await fetchData(url);
  if (!html) {
    console.log("No data found.");
    return;
  }
  const $ = cheerio.load(html);
  
  let csvContent = "date,assets\n";
  $("#style-1 > div:nth-child(2) > table > tbody tr").each((i, row) => {
    const date = $(row).find("td").eq(0).text().trim();
    const rawAmount = $(row).find("td").eq(1).text().trim();
    if (date && rawAmount) {
      const millionsValue = parseFloat(rawAmount.replace('$', '').replace(',', ''));
      const billionsValue = (millionsValue / 1000).toFixed(4);
      csvContent += `${date},${billionsValue}\n`;
    }
  });

  const filename = `${ticker}_assets.csv`;
  const filePath = path.join(tickerDir, filename);
  fs.writeFileSync(filePath, csvContent);
  console.log(`Saved ${filename}`);
}

/**
 * Fetches debt to equity ratio data and saves as CSV.
 */
async function fetchDebtToEquity(ticker, companyName, tickerDir) {
  const url = `https://www.macrotrends.net/stocks/charts/${ticker}/${companyName}/debt-equity-ratio`;
  console.log(`Fetching debt-to-equity data from ${url}`);
  const html = await fetchData(url);
  if (!html) {
    console.log("No data found.");
    return;
  }
  const $ = cheerio.load(html);
  
  let csvContent = "date,debttoequityratio\n";
  $("#style-1 > table > tbody tr").each((i, row) => {
    const date = $(row).find("td").eq(0).text().trim();
    const ratio = $(row).find("td").eq(3).text().trim();
    if (date && ratio) {
      csvContent += `${date},${ratio}\n`;
    }
  });

  const filename = `${ticker}_debt_to_equity.csv`;
  const filePath = path.join(tickerDir, filename);
  fs.writeFileSync(filePath, csvContent);
  console.log(`Saved ${filename}`);
}

/**
 * Fetches NOI, converts millions to billions, and saves as CSV.
 */
async function fetchNOI(ticker, companyName, tickerDir) {
  const url = `https://www.macrotrends.net/stocks/charts/${ticker}/${companyName}/operating-income`;
  console.log(`Fetching NOI data from ${url}`);
  const html = await fetchData(url);
  if (!html) {
    console.log("No data found.");
    return;
  }
  const $ = cheerio.load(html);
  
  let csvContent = "date,NOI\n";
  $("#style-1 > div:nth-child(2) > table tr").each((i, row) => {
    if (i === 0) return; // skip header row
    const date = $(row).find("td").eq(0).text().trim();
    const rawAmount = $(row).find("td").eq(1).text().trim();
    if (date && rawAmount) {
      const millionsValue = parseFloat(rawAmount.replace('$', '').replace(',', ''));
      const billionsValue = (millionsValue / 1000).toFixed(4);
      csvContent += `${date},${billionsValue}\n`;
    }
  });

  const filename = `${ticker}_NOI.csv`;
  const filePath = path.join(tickerDir, filename);
  fs.writeFileSync(filePath, csvContent);
  console.log(`Saved ${filename}`);
}

/**
 * Fetches market cap data using regex extraction and writes CSV.
 */
async function fetchMarketCap(ticker, tickerDir) {
  const url = `https://www.macrotrends.net/assets/php/market_cap.php?t=${ticker}`;
  console.log(`Fetching market cap data from ${url}`);
  const data = await fetchData(url);
  if (!data) {
    console.log("No data found.");
    return;
  }
  const match = data.match(/var chartData = (\[.*?\]);/s);
  if (!match) {
    console.log("Chart data not found.");
    return;
  }
  try {
      const chartData = JSON.parse(match[1]);
      let csvContent = Object.keys(chartData[0]).join(",") + "\n";
      chartData.forEach(row => {
          csvContent += Object.values(row).join(",") + "\n";
      });
      fs.writeFileSync(path.join(tickerDir, `${ticker}_market_cap.csv`), csvContent);
      console.log(`Saved ${ticker}_market_cap.csv`);
  } catch (error) {
      console.error("Error parsing chart data JSON:", error);
  } 
}
  /**
 * Calculates cap rate for the ticker by merging the NOI and assets CSVs.
 * Cap rate is calculated as NOI / assets.
 */
function calculateCapRate(ticker, tickerDir) {
    const noiFile = path.join(tickerDir, `${ticker}_NOI.csv`);
    const assetsFile = path.join(tickerDir, `${ticker}_assets.csv`);
  
    // Read and parse the NOI CSV file
    const noiData = fs.readFileSync(noiFile, "utf8");
    const noiLines = noiData.trim().split("\n");
    noiLines.shift(); // Remove header ("date,NOI")
    const noiMap = {};
    noiLines.forEach((line) => {
      const [date, noiValue] = line.split(",");
      if (date && noiValue) {
        noiMap[date] = parseFloat(noiValue);
      }
    });
  
    // Read and parse the assets CSV file
    const assetsData = fs.readFileSync(assetsFile, "utf8");
    const assetsLines = assetsData.trim().split("\n");
    assetsLines.shift(); // Remove header ("date,assets")
    const assetsMap = {};
    assetsLines.forEach((line) => {
      const [date, assetsValue] = line.split(",");
      if (date && assetsValue) {
        assetsMap[date] = parseFloat(assetsValue);
      }
    });
  
    // Merge data and calculate cap rate for dates present in both files
    let csvContent = "date,cap_rate\n";
    Object.keys(noiMap).forEach((date) => {
      if (assetsMap[date] !== undefined && assetsMap[date] !== 0) {
        const capRate = noiMap[date] / assetsMap[date];
        csvContent += `${date},${capRate}\n`;
      }
    });
  
    // Write the cap rate CSV file
    const capRateFile = path.join(tickerDir, `${ticker}_cap_rate.csv`);
    fs.writeFileSync(capRateFile, csvContent);
    console.log(`Cap rate data saved to ${capRateFile}`);
  }

/**
 * Main processing loop. For each ticker:
 *   1. Get the company name.
 *   2. Create a directory for CSV files.
 *   3. Call each endpoint function.
 */
(async () => {
  for (const ticker of tickers) {
    // const result = await findTickerNames([ticker]);
    const companyName = "null"; // this works?????????
    
    // Create directory for ticker if it doesn't exist
    const tickerDir = path.join(__dirname, ticker);
    if (!fs.existsSync(tickerDir)) {
      fs.mkdirSync(tickerDir, { recursive: true });
    }
    
    // Call each endpoint
    await fetchAssets(ticker, companyName, tickerDir);
    await fetchDebtToEquity(ticker, companyName, tickerDir);
    await fetchNOI(ticker, companyName, tickerDir);
    await fetchMarketCap(ticker, tickerDir);

    // Merge certain data
    calculateCapRate(ticker, tickerDir);
  }
})();
