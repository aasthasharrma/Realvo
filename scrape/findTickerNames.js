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
