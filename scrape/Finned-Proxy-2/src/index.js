// simple cloudflare worker to request a url and return the response
addEventListener('fetch', event => {
	event.respondWith(handleRequest(event.request));
});

const isAuthenticated = (apiKey) => {
	return apiKey === API_KEY;
}

async function streamToString(stream) {
	const reader = stream.getReader();
	const decoder = new TextDecoder();
  
	let result = '';
	while (true) {
	  const { done, value } = await reader.read();
  
	  if (done) {
		// End of the stream
		break;
	  }
  
	  // Convert the chunk (Uint8Array) to string and append to the result
	  result += decoder.decode(value, { stream: true });
	}
  
	// Close the reader
	reader.releaseLock();
  
	return result;
}

class memcache {
	constructor() {
		this.objects = {}
		this.maxAge = 43200
	}
	contains(item) {
		return this.objects.hasOwnProperty(item)
	}
	get(item) {
		return this.objects[item]
	}
	new(item, body) {
		this.objects[item] = {
			expires: (new Date() / 1000) + this.maxAge,
			// body is a ReadableStream, so we need to convert it to a string
			body: body.toString(),
			status: 200
		}
	}
	isValid(item) {
		const sSinceEpoch = new Date() / 1000;
		if (this.objects[item].expires < sSinceEpoch) {
			delete this.objects[item];
			return false
		}
		return true
	}
}

const reqHeaders = {
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
	'Accept-Language': 'en-US,en;q=0.9',
	'Accept-Encoding': 'gzip, deflate, br',
	'Connection': 'keep-alive',
	'Upgrade-Insecure-Requests': '1',
}

const resHeaders = {
	'Content-Type': 'text/html',
	'Access-Control-Allow-Origin': '*',
	'Access-Control-Allow-Methods': 'GET,HEAD,PUT,PATCH,POST,DELETE',
	'Access-Control-Allow-Headers': 'Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With',
}

const CACHE = new memcache()

const handleRequest = async (request) => {
	// extract the url from the request
	const url = new URL(request.url);
	const auth = url.searchParams.get('auth');
	if (!isAuthenticated(auth)) return new Response('unauthorized', { status: 403 });

	const target = url.searchParams.get('url');
	if (!target) return new Response('no url provided', { status: 400 });

	// fetch the url
	let response, result;
	let usedCache = false;
	if (CACHE.contains(target) && CACHE.isValid(target)) {
		response = CACHE.get(target);
		result = response.body;
		usedCache = true;
	} else {
		response = await fetch(target, {
			headers: reqHeaders
		});
		result = await streamToString(response.body);
		CACHE.new(target, result.toString())
	}

	// return the response HTML
	return new Response(result, {
		status: response.status,
		headers: {...resHeaders, usedCache: usedCache}
	});
}