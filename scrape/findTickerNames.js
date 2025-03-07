// List of tickers to process.
const tickers = ["SPG"];

// Define a constant for the User-Agent string.
const USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
  'AppleWebKit/537.36 (KHTML, like Gecko) ' +
  'Chrome/51.0.2704.103 Safari/537.36';

// Set up your proxy endpoint and API key.
const PROXY_BASE_URL = "https://finned-proxy.mac-48b.workers.dev/";
const API_KEY = "INSERT_API_KEY_HERE"; // Replace with your actual API key

/**
 * Converts a company name into a URL-friendly slug.
 * Example: "Simon Property Group" -> "simon-property-group"
 *
 * @param {string} companySlug
 * @returns {string} 
 */
function companySlugToName(companySlug) {
  return companySlug
    .toLowerCase()               // Convert to lowercase.
    .replace(/[^\w\s]/g, '')     // Remove non-alphanumeric characters.
    .trim()                      // Remove leading/trailing spaces.
    .replace(/\s+/g, '-');       // Replace spaces with hyphens.
}

/**
 * Helper function that routes a fetch call through your Cloudflare proxy.
 *
 * @param {string} targetUrl - The URL you actually want to fetch.
 * @param {Object} options - Fetch options.
 * @returns {Promise<Response>}
 */
async function fetchThroughProxy(targetUrl, options = {}) {
  // Build the proxy URL by encoding the API key and target URL as query parameters.
  const proxyUrl = `${PROXY_BASE_URL}?auth=${encodeURIComponent(API_KEY)}&url=${encodeURIComponent(targetUrl)}`;
  return fetch(proxyUrl, options);
}

/**
 * Validates whether a Macrotrends URL exists by sending a HEAD request.
 * The URL pattern is:
 *   https://www.macrotrends.net/stocks/charts/{ticker}/{slug}/market-cap
 *
 * @param {string} ticker - The stock ticker symbol.
 * @param {string} standardizedName - The standardized name to test.
 * @returns {Promise<boolean>} True if the URL exists (response.ok), false otherwise.
 */
async function validateMacrotrendsSlug(ticker, standardizedName) {
  const targetUrl = `https://www.macrotrends.net/stocks/charts/${ticker}/${standardizedName}/market-cap`;
  try {
    // Send a HEAD request via the proxy.
    const response = await fetchThroughProxy(targetUrl, {
      method: 'HEAD',
      headers: { 'User-Agent': USER_AGENT }
    });
    console.log(`Testing URL: ${targetUrl} - Status: ${response.status}`);
    return response.ok;
  } catch (err) {
    console.error(`Error validating URL ${targetUrl}:`, err);
    return false;
  }
}

/** 
 * Given a ticker and a full slug from Yahoo Finance, iteratively try shorter slugs
 * until a valid Macrotrends URL is found.
 *
 * @param {string} ticker - The stock ticker symbol.
 * @param {string} standardizedName - The full slug generated from the company name.
 * @returns {Promise<string|null>} A valid standardized name if found; otherwise, null.
 */
async function getValidMacrotrendsSlug(ticker, standardizedName) {
  // Split the full slug into words.
  const words = standardizedName.split('-');
  // Try from the full slug down to one word.
  for (let i = words.length; i >= 1; i--) {
    const testStandardizedName = words.slice(0, i).join('-');
    if (await validateMacrotrendsSlug(ticker, testStandardizedName)) {
      console.log(`Valid standardized name found for ${ticker}: ${testStandardizedName}`);
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
 *
 * @param {string} ticker - The stock ticker symbol.
 * @returns {Promise<string|null>} A valid name for Macrotrends, or null if not found.
 */
async function findTickerNameFromYahoo(ticker) {
  const targetUrl = `https://query1.finance.yahoo.com/v1/finance/search?q=${ticker}`;
  console.log(`Fetching Yahoo Finance data for ${ticker}...`);
  try {
    // Fetch data via the proxy.
    const response = await fetchThroughProxy(targetUrl, {
      headers: { 'User-Agent': USER_AGENT }
    });
    const json = await response.json();
    if (json.quotes && json.quotes.length > 0) {
      const quote = json.quotes[0];
      if (!quote.shortname) {
        console.error(`No company name found for ${ticker} from Yahoo Finance.`);
        return null;
      }
      // Convert the company name into a slug.
      const standardizedName = companySlugToName(quote.shortname);
      console.log(`Standardized name from Yahoo for ${ticker}: ${standardizedName}`);
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

(async () => {
  // Find the valid ticker names.
  const result = await findTickerNames(tickers);
  console.log('Result:', result);
})();




// STRUCTURE
// 1. file that gets the ticker names from yahoo finance
// 2. file that gets the data for a ticker (ticker agnostic)
//      - create rules for a common standardize data format for returnig scraped data
// 3. file that gets data for our specific tickers by calling the first and second file