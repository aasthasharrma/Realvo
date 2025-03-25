const fs = require("fs");
const path = require("path");
const axios = require("axios");

// List of tickers to process.
const tickers = ["SPG"];

// Define a constant for the User-Agent string.
const USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
	'AppleWebKit/537.36 (KHTML, like Gecko) ' +
	'Chrome/51.0.2704.103 Safari/537.36';

const PROXY_URL = 'https://finned-proxy.mac-48b.workers.dev/?auth=$6nb9%@Su2KQrfQ@!P55&url=';

// Define a path to the cache file.
const CACHE_FILE = path.join(__dirname, "ticker_cache.txt");

async function fetchData(url) {
  try {
	  console.log(`Fetching data from ${url}`);
	  const response = await axios.get(`${PROXY_URL}${encodeURIComponent(url)}`, {
		  headers: { "User-Agent": USER_AGENT }
	  });
	  return response;
  } catch (error) {
	  console.error(`Error fetching data from ${url}:`, error.message);
	  return null;
  }
}

// Load cache from file
function loadCache() {
	if (fs.existsSync(CACHE_FILE)) {
		const data = fs.readFileSync(CACHE_FILE, "utf8");
		return JSON.parse(data);
	}
	return {};
}

// Save cache to file
function saveCache(cache) {
	fs.writeFileSync(CACHE_FILE, JSON.stringify(cache, null, 2), "utf8");
}

// Actually load the cache from the file.
const cache = loadCache();

/**
 * Converts a company name into a URL-friendly slug.
 * Example: "Simon Property Group" -> "simon-property-group"
 *
 * @param {string} companySlug
 * @returns {string} 
 */
function companySlugToName(companySlug) { // why did i even write this function?
	return companySlug
		.toLowerCase() // Convert to lowercase.
		.replace(/[^\w\s]/g, '') // Remove non-alphanumeric characters.
		.trim() // Remove leading/trailing spaces.
		.replace(/\s+/g, '-'); // Replace spaces with hyphens.
}

/**
 * Validates whether a Macrotrends URL exists by sending a HEAD request.
 * The URL pattern is:
 *   https://www.macrotrends.net/stocks/charts/{ticker}/{slug}/market-cap
 *
 * @param {string} ticker - The stock ticker symbol.
 * @param {string} standardizedName - The standardizedName to test.
 * @returns {Promise<boolean>} True if the URL exists (response.ok), false otherwise.
 */
async function validateMacrotrendsSlug(ticker, standardizedName) {
	const url = `https://www.macrotrends.net/stocks/charts/${ticker}/${standardizedName}/market-cap`;
	const response = await fetchData(url);
	return response && response.status >= 200 && response.status < 300;
}

/** 
 * Given a ticker and a full slug from Yahoo Finance, iteratively try shorter slugs
 * until a valid Macrotrends URL is found. For example, if the full slug is
 * "simon-property-group", we’ll try:
 *   "simon-property-group" -> if not valid, then "simon-property" -> if not, then "simon".
 *
 * @param {string} ticker - The stock ticker symbol.
 * @param {string} standardizedName - The full slug generated from the company name.
 * @returns {Promise<string|null>} A validStandardizedName if found; otherwise, null.
 */
async function getValidMacrotrendsSlug(ticker, standardizedName) {
	// Split the full slug into words.
	const words = standardizedName.split('-');
	// Try from the full slug down to one word
	for (let i = words.length; i >= 1; i--) {
		const testStandardizedName = words.slice(0, i).join('-');
		if (await validateMacrotrendsSlug(ticker, testStandardizedName)) {
			console.log(`Valid standardized name found for ${ticker}: ${testStandardizedName}`);
			cache[ticker] = testStandardizedName;
			saveCache(cache);
			return testStandardizedName;
		} else {
			console.log(`Standardized name ${testStandardizedName} is not valid for ${ticker}.`);
		}
	}
	console.error(`No standardized name found for ${ticker} using ${standardizedName}`);
	return null;
}

/**
 * Uses Yahoo Finance to fetch the company’s short name for a ticker, converts it into a slug,
 * and then finds the valid Macrotrends slug by trimming the full slug as needed. 
 * "simon-property-group", we’ll try:
 *   "simon-property-group" -> if not valid, then "simon-property" -> if not, then "simon".
 *
 * @param {string} ticker - The stock ticker symbol.
 * @returns {Promise<string|null>} A validName for Macrotrends, or null if not found.
 */
async function findTickerNameFromYahoo(ticker) {
	if (cache[ticker]) {
		console.log(`Cache hit for ${ticker}: ${cache[ticker]}`);
		return cache[ticker];
	}

	const url = `https://query1.finance.yahoo.com/v1/finance/search?q=${ticker}`;
	console.log(`Fetching Yahoo Finance data for ${ticker}...`);
	try {
		// Fetch data from Yahoo Finance.
		const response = await fetchData(url);
		// Parse the JSON response.
		const json = await response.json();
		if (json.quotes && json.quotes.length > 0) {
			const quote = json.quotes[0];
			if (!quote.shortname) {
				console.error(`No company name found for ${ticker} from Yahoo Finance.`);
				return null;
			}
			// Convert the company name into a slug. we do this
			const standardizedName = companySlugToName(quote.shortname);
			console.log(`standardizedName from Yahoo for ${ticker}: ${standardizedName}`);
			const validName = await getValidMacrotrendsSlug(ticker, standardizedName);
			return validName;
		} else {
			console.error(`No quotes found for ${ticker}`);
			return null;
		}
	} catch (err) {
		console.error(`Error fetching Yahoo Finance data for ${ticker}:`, err);
		return null;
	}
}

/**
 * Processes a list of tickers to find their corresponding valid slugs (ticker names) for Macrotrends.
 *
 * @param {string[]} tickerList - Array of ticker symbols.
 * @returns {Promise<Object>} An object mapping tickers to their valid slugs.
 */
async function findTickerNames(tickerList) {
	const result = {};
	for (const ticker of tickerList) {
		const slug = await findTickerNameFromYahoo(ticker);
		result[ticker] = slug;
	}
	return result;
}

// (async () => {
// 	// find the valid ticker names.
// 	const result = await findTickerNames(tickers);
// 	console.log('Result:', result);
// })();

module.exports = { findTickerNames };
// export { findTickerNames };