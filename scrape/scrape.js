const fs = require("fs");
const path = require("path");
const axios = require("axios");
const cheerio = require("cheerio");
// const { findTickerNames } = require("./archive/findTickerNames.js");

const tickers = ["SPG"];
const USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
	'AppleWebKit/537.36 (KHTML, like Gecko) ' +
	'Chrome/51.0.2704.103 Safari/537.36';

const PROXY_1 = `https://finned-proxy.mac-48b.workers.dev/?auth=Wm8hdBSbUA558q9M2Hmn&url=`;
const PROXY_2 = `https://finned-proxy-1.mac-48b.workers.dev/?auth=FgUpD3Wch5EkReWvfVD5&url=`;
const PROXY_3 = `https://finned-proxy-2.mac-48b.workers.dev/?auth=gVVA5ajGHtebKBjJ7WL6&url=`;
const PROXY_LIST = [PROXY_1, PROXY_2, PROXY_3];
let PROXY_INDEX = 0;

async function fetchData(url) {
  const PROXY_URL = PROXY_LIST[PROXY_INDEX];
  PROXY_INDEX = (PROXY_INDEX + 1) % PROXY_LIST.length;
  try {
      console.log(`Fetching data from ${PROXY_URL}${encodeURIComponent(url)}`);
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
  const filename = `${ticker}_assets.csv`;
  const filePath = path.join(tickerDir, filename);
  
  // Skip if file already exists
  if (fs.existsSync(filePath)) {
    console.log(`File ${filename} already exists. Skipping...`);
    return;
  }
  
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

  fs.writeFileSync(filePath, csvContent);
  console.log(`Saved ${filename}`);
}

/**
 * Fetches debt to equity ratio data and saves as CSV.
 */
async function fetchDebtToEquity(ticker, companyName, tickerDir) {
  const filename = `${ticker}_debt_to_equity.csv`;
  const filePath = path.join(tickerDir, filename);
  
  // Skip if file already exists
  if (fs.existsSync(filePath)) {
    console.log(`File ${filename} already exists. Skipping...`);
    return;
  }
  
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

  fs.writeFileSync(filePath, csvContent);
  console.log(`Saved ${filename}`);
}

/**
 * Fetches NOI, converts millions to billions, and saves as CSV.
 */
async function fetchNOI(ticker, companyName, tickerDir) {
  const filename = `${ticker}_NOI.csv`;
  const filePath = path.join(tickerDir, filename);
  
  // Skip if file already exists
  if (fs.existsSync(filePath)) {
    console.log(`File ${filename} already exists. Skipping...`);
    return;
  }
  
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

  fs.writeFileSync(filePath, csvContent);
  console.log(`Saved ${filename}`);
}

/**
 * Fetches market cap data using regex extraction and writes CSV.
 */
async function fetchMarketCap(ticker, companyName, tickerDir) {
  const filename = `${ticker}_market_cap.csv`;
  const filePath = path.join(tickerDir, filename);
  
  // Skip if file already exists
  if (fs.existsSync(filePath)) {
    console.log(`File ${filename} already exists. Skipping...`);
    return;
  }
  
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
      fs.writeFileSync(filePath, csvContent);
      console.log(`Saved ${filename}`);
  } catch (error) {
      console.error("Error parsing chart data JSON:", error);
  } 
}

async function fetchGrossProfit(ticker, companyName, tickerDir) {
  const filename = `${ticker}_gross_profit.csv`;
  const filePath = path.join(tickerDir, filename);
  
  // Skip if file already exists
  if (fs.existsSync(filePath)) {
    console.log(`File ${filename} already exists. Skipping...`);
    return;
  }
  
  const url = `https://www.macrotrends.net/stocks/charts/${ticker}/${companyName}/gross-profit`;
  console.log(`Fetching gross profit data from ${url}`);
  const html = await fetchData(url);
  if (!html) {
    console.log("No data found.");
    return;
  }
  const $ = cheerio.load(html);

  let csvContent = "date,grossprofit\n";
  $("#style-1 > div:nth-child(2) > table > tbody tr").each((i, row) => {
    const date = $(row).find("td").eq(0).text().trim();
    const rawAmount = $(row).find("td").eq(1).text().trim();
    if (date && rawAmount) {
      const millionsValue = parseFloat(rawAmount.replace('$', '').replace(',', ''));
      const billionsValue = (millionsValue / 1000).toFixed(4);
      csvContent += `${date},${billionsValue}\n`;
    }
  });

  fs.writeFileSync(filePath, csvContent);
  console.log(`Saved ${filename}`);
}

async function fetchRevenue(ticker, companyName, tickerDir) {
  const filename = `${ticker}_revenue.csv`;
  const filePath = path.join(tickerDir, filename);
  
  // Skip if file already exists
  if (fs.existsSync(filePath)) {
    console.log(`File ${filename} already exists. Skipping...`);
    return;
  }
  
  const url = `https://www.macrotrends.net/stocks/charts/${ticker}/${companyName}/revenue`;
  console.log(`Fetching revenue data from ${url}`);
  const html = await fetchData(url);
  if (!html) {
    console.log("No data found.");
    return;
  }
  const $ = cheerio.load(html);

  let csvContent = "date,revenue\n";
  $("#style-1 > div:nth-child(2) > table > tbody tr").each((i, row) => {
    const date = $(row).find("td").eq(0).text().trim();
    const rawAmount = $(row).find("td").eq(1).text().trim();
    if (date && rawAmount) {
      const millionsValue = parseFloat(rawAmount.replace('$', '').replace(',', ''));
      const billionsValue = (millionsValue / 1000).toFixed(4);
      csvContent += `${date},${billionsValue}\n`;
    }
  });

  fs.writeFileSync(filePath, csvContent);
  console.log(`Saved ${filename}`);
}

async function fetchEbitda(ticker, companyName, tickerDir) {
  const filename = `${ticker}_ebitda.csv`;
  const filePath = path.join(tickerDir, filename);
  
  // Skip if file already exists
  if (fs.existsSync(filePath)) {
    console.log(`File ${filename} already exists. Skipping...`);
    return;
  }
  
  const url = `https://www.macrotrends.net/stocks/charts/${ticker}/${companyName}/ebitda`;
  console.log(`Fetching EBITDA data from ${url}`);
  const html = await fetchData(url);
  if (!html) {
    console.log("No data found.");
    return;
  }
  const $ = cheerio.load(html);

  let csvContent = "date,ebitda\n";
  $("#style-1 > div:nth-child(2) > table > tbody tr").each((i, row) => {
    const date = $(row).find("td").eq(0).text().trim();
    const rawAmount = $(row).find("td").eq(1).text().trim();
    if (date && rawAmount) {
      const millionsValue = parseFloat(rawAmount.replace('$', '').replace(',', ''));
      const billionsValue = (millionsValue / 1000).toFixed(4);
      csvContent += `${date},${billionsValue}\n`;
    }
  });

  fs.writeFileSync(filePath, csvContent);
  console.log(`Saved ${filename}`);
}

async function fetchNetIncome(ticker, companyName, tickerDir) {
  const filename = `${ticker}_net_income.csv`;
  const filePath = path.join(tickerDir, filename);
  
  // Skip if file already exists
  if (fs.existsSync(filePath)) {
    console.log(`File ${filename} already exists. Skipping...`);
    return;
  }
  
  const url = `https://www.macrotrends.net/stocks/charts/${ticker}/${companyName}/net-income`;
  console.log(`Fetching net income data from ${url}`);
  const html = await fetchData(url);
  if (!html) {
    console.log("No data found.");
    return;
  }
  const $ = cheerio.load(html);

  let csvContent = "date,netincome\n";
  $("#style-1 > div:nth-child(2) > table > tbody tr").each((i, row) => {
    const date = $(row).find("td").eq(0).text().trim();
    const rawAmount = $(row).find("td").eq(1).text().trim();
    if (date && rawAmount) {
      const millionsValue = parseFloat(rawAmount.replace('$', '').replace(',', ''));
      const billionsValue = (millionsValue / 1000).toFixed(4);
      csvContent += `${date},${billionsValue}\n`;
    }
  });

  fs.writeFileSync(filePath, csvContent);
  console.log(`Saved ${filename}`);
}

async function fetchEps(ticker, companyName, tickerDir) {
  const filename = `${ticker}_eps.csv`;
  const filePath = path.join(tickerDir, filename);
  
  // Skip if file already exists
  if (fs.existsSync(filePath)) {
    console.log(`File ${filename} already exists. Skipping...`);
    return;
  }
  
  const url = `https://www.macrotrends.net/stocks/charts/${ticker}/${companyName}/eps-earnings-per-share-diluted`;
  console.log(`Fetching EPS data from ${url}`);
  const html = await fetchData(url);
  if (!html) {
    console.log("No data found.");
    return;
  }
  const $ = cheerio.load(html);

  let csvContent = "date,eps\n";
  $("#style-1 > div:nth-child(2) > table > tbody tr").each((i, row) => {
    const date = $(row).find("td").eq(0).text().trim();
    const rawAmount = $(row).find("td").eq(1).text().trim();
    if (date && rawAmount) {
      csvContent += `${date},${rawAmount}\n`;
    }
  });

  fs.writeFileSync(filePath, csvContent);
  console.log(`Saved ${filename}`);
}

async function fetchCashOnHand(ticker, companyName, tickerDir) {
  const filename = `${ticker}_cash_on_hand.csv`;
  const filePath = path.join(tickerDir, filename);
  
  // Skip if file already exists
  if (fs.existsSync(filePath)) {
    console.log(`File ${filename} already exists. Skipping...`);
    return;
  }
  
  const url = `https://www.macrotrends.net/stocks/charts/${ticker}/${companyName}/cash-on-hand`;
  console.log(`Fetching cash on hand data from ${url}`);
  const html = await fetchData(url);
  if (!html) {
    console.log("No data found.");
    return;
  }
  const $ = cheerio.load(html);

  let csvContent = "date,cashonhand\n";
  $("#style-1 > div:nth-child(2) > table > tbody tr").each((i, row) => {
    const date = $(row).find("td").eq(0).text().trim();
    const rawAmount = $(row).find("td").eq(1).text().trim();
    if (date && rawAmount) {
      const millionsValue = parseFloat(rawAmount.replace('$', '').replace(',', ''));
      const billionsValue = (millionsValue / 1000).toFixed(4);
      csvContent += `${date},${billionsValue}\n`;
    }
  });

  fs.writeFileSync(filePath, csvContent);
  console.log(`Saved ${filename}`);
}

async function fetchLongTermDebt(ticker, companyName, tickerDir) {
  const filename = `${ticker}_long_term_debt.csv`;
  const filePath = path.join(tickerDir, filename);
  
  // Skip if file already exists
  if (fs.existsSync(filePath)) {
    console.log(`File ${filename} already exists. Skipping...`);
    return;
  }
  
  const url = `https://www.macrotrends.net/stocks/charts/${ticker}/${companyName}/long-term-debt`;
  console.log(`Fetching long-term debt data from ${url}`);
  const html = await fetchData(url);
  if (!html) {
    console.log("No data found.");
    return;
  }
  const $ = cheerio.load(html);

  let csvContent = "date,longtermdebt\n";
  $("#style-1 > div:nth-child(2) > table > tbody tr").each((i, row) => {
    const date = $(row).find("td").eq(0).text().trim();
    const rawAmount = $(row).find("td").eq(1).text().trim();
    if (date && rawAmount) {
      const millionsValue = parseFloat(rawAmount.replace('$', '').replace(',', ''));
      const billionsValue = (millionsValue / 1000).toFixed(4);
      csvContent += `${date},${billionsValue}\n`;
    }
  });

  fs.writeFileSync(filePath, csvContent);
  console.log(`Saved ${filename}`);
}

async function fetchTotalLiabilities(ticker, companyName, tickerDir) {
  const filename = `${ticker}_total_liabilities.csv`;
  const filePath = path.join(tickerDir, filename);
  
  // Skip if file already exists
  if (fs.existsSync(filePath)) {
    console.log(`File ${filename} already exists. Skipping...`);
    return;
  }
  
  const url = `https://www.macrotrends.net/stocks/charts/${ticker}/${companyName}/total-liabilities`;
  console.log(`Fetching total liabilities data from ${url}`);
  const html = await fetchData(url);
  if (!html) {
    console.log("No data found.");
    return;
  }
  const $ = cheerio.load(html);

  let csvContent = "date,totalliabilities\n";
  $("#style-1 > div:nth-child(2) > table > tbody tr").each((i, row) => {
    const date = $(row).find("td").eq(0).text().trim();
    const rawAmount = $(row).find("td").eq(1).text().trim();
    if (date && rawAmount) {
      const millionsValue = parseFloat(rawAmount.replace('$', '').replace(',', ''));
      const billionsValue = (millionsValue / 1000).toFixed(4);
      csvContent += `${date},${billionsValue}\n`;
    }
  });

  fs.writeFileSync(filePath, csvContent);
  console.log(`Saved ${filename}`);
}

async function fetchTotalShareholderEquity(ticker, companyName, tickerDir) {
  const filename = `${ticker}_total_shareholder_equity.csv`;
  const filePath = path.join(tickerDir, filename);
  
  // Skip if file already exists
  if (fs.existsSync(filePath)) {
    console.log(`File ${filename} already exists. Skipping...`);
    return;
  }
  
  const url = `https://www.macrotrends.net/stocks/charts/${ticker}/${companyName}/total-share-holder-equity`;
  console.log(`Fetching total shareholder equity data from ${url}`);
  const html = await fetchData(url);
  if (!html) {
    console.log("No data found.");
    return;
  }
  const $ = cheerio.load(html);

  let csvContent = "date,totalshareholderequity\n";
  $("#style-1 > div:nth-child(2) > table > tbody tr").each((i, row) => {
    const date = $(row).find("td").eq(0).text().trim();
    const rawAmount = $(row).find("td").eq(1).text().trim();
    if (date && rawAmount) {
      const millionsValue = parseFloat(rawAmount.replace('$', '').replace(',', ''));
      const billionsValue = (millionsValue / 1000).toFixed(4);
      csvContent += `${date},${billionsValue}\n`;
    }
  });

  fs.writeFileSync(filePath, csvContent);
  console.log(`Saved ${filename}`);
}

/**
 * Calculates cap rate for the ticker by merging the NOI and assets CSVs.
 * Cap rate is calculated as NOI / assets.
 */
function calculateCapRate(ticker, tickerDir) {
    const capRateFile = path.join(tickerDir, `${ticker}_cap_rate.csv`);
    
    // Skip if file already exists
    if (fs.existsSync(capRateFile)) {
      console.log(`File ${ticker}_cap_rate.csv already exists. Skipping...`);
      return;
    }
    
    const noiFile = path.join(tickerDir, `${ticker}_NOI.csv`);
    const assetsFile = path.join(tickerDir, `${ticker}_assets.csv`);
    
    // Check if required files exist
    if (!fs.existsSync(noiFile) || !fs.existsSync(assetsFile)) {
      console.log(`Required files for cap rate calculation missing. Skipping...`);
      return;
    }
  
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
    
    // Call each endpoint with a 5000 ms delay
    const endpoints = [
      fetchAssets,
      fetchDebtToEquity,
      fetchNOI,
      fetchMarketCap,
      fetchGrossProfit,
      fetchRevenue,
      fetchEbitda,
      fetchNetIncome,
      fetchEps,
      fetchCashOnHand,
      fetchLongTermDebt,
      fetchTotalLiabilities,
      fetchTotalShareholderEquity
    ];
    for (const endpoint of endpoints) {
      await endpoint(ticker, companyName, tickerDir);
      await new Promise((resolve) => setTimeout(resolve, 5000));
    }

    // Merge certain data
    calculateCapRate(ticker, tickerDir);
  }
})();