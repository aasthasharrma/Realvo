// List of tickers to process.
const tickers = ["SPG"];

// Define a constant for the User-Agent string.
const USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
	'AppleWebKit/537.36 (KHTML, like Gecko) ' +
	'Chrome/51.0.2704.103 Safari/537.36';

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
	try {
		// Send a HEAD request to check if the URL exists.
		const response = await fetch(url, {
			method: 'HEAD',
			headers: {
				'User-Agent': USER_AGENT
			}
		});
		// Log the status of the response. does the url exist?
		console.log(`Testing URL: ${url} - Status: ${response.status}`);
		return response.ok;
	} catch (err) {
		console.error(`Error validating URL ${url}:`, err);
		return false;
	}
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
			return testStandardizedName;
		} else {
			console.log(`Standardized name ${testStandardizedName} is not valid for ${ticker}.`);
		}
	}
	console.error(`No standardized name found for ${ticker} using ${standardizedName}`);
	return null;
}