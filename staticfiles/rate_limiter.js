// Rate Limiting Utility for External API Calls
// Implements exponential backoff for 429 (Too Many Requests) errors

/**
 * Sleep utility for async delays
 * @param {number} ms - Milliseconds to sleep
 * @returns {Promise}
 */
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Make a rate-limited API request with exponential backoff
 * @param {Function} apiCall - Async function that makes the API call
 * @param {Object} options - Configuration options
 * @param {number} options.maxRetries - Maximum number of retries (default: 5)
 * @param {number} options.initialDelay - Initial delay in ms (default: 61000)
 * @param {number} options.maxDelay - Maximum delay in ms (default: 300000)
 * @param {Function} options.onRetry - Callback on retry (receives retry count and delay)
 * @returns {Promise} - Result of the API call
 */
async function makeRateLimitedRequest(apiCall, options = {}) {
    const {
        maxRetries = 5,
        initialDelay = 61000, // 61 seconds (for 5 requests/300s limit)
        maxDelay = 300000,    // 5 minutes max
        onRetry = null
    } = options;

    let retries = 0;
    let delay = initialDelay;
    
    while (retries < maxRetries) {
        try {
            const result = await apiCall();
            
            // Reset delay on success
            if (retries > 0) {
                console.log(`✅ Rate-limited request succeeded after ${retries} retries`);
            }
            
            return result;
        } catch (error) {
            // Check if it's a rate limit error
            const isRateLimit = 
                error.response?.status === 429 || 
                error.status === 429 ||
                (error.message && error.message.toLowerCase().includes('rate limit'));
            
            if (isRateLimit && retries < maxRetries) {
                retries++;
                
                console.warn(`⚠️ Rate limit hit. Retry ${retries}/${maxRetries} after ${delay}ms`);
                
                // Call retry callback if provided
                if (onRetry) {
                    onRetry(retries, delay);
                }
                
                // Wait before retrying
                await sleep(delay);
                
                // Exponential backoff with cap
                delay = Math.min(delay * 2, maxDelay);
            } else {
                // Not a rate limit error or max retries exceeded
                if (retries >= maxRetries) {
                    console.error(`❌ Max retries (${maxRetries}) exceeded for rate-limited request`);
                }
                throw error;
            }
        }
    }
    
    throw new Error('Max retries exceeded for rate-limited request');
}

/**
 * Rate limiter for fetch API calls
 * @param {string} url - URL to fetch
 * @param {Object} options - Fetch options
 * @param {Object} rateLimitOptions - Rate limit options
 * @returns {Promise<Response>}
 */
async function rateLimitedFetch(url, options = {}, rateLimitOptions = {}) {
    return makeRateLimitedRequest(
        () => fetch(url, options).then(response => {
            if (response.status === 429) {
                throw { response, status: 429, message: 'Rate limit exceeded' };
            }
            return response;
        }),
        rateLimitOptions
    );
}

/**
 * Rate limiter for Axios requests
 * @param {Object} axiosInstance - Axios instance
 * @param {Object} config - Axios request config
 * @param {Object} rateLimitOptions - Rate limit options
 * @returns {Promise}
 */
async function rateLimitedAxios(axiosInstance, config, rateLimitOptions = {}) {
    return makeRateLimitedRequest(
        () => axiosInstance(config),
        rateLimitOptions
    );
}

/**
 * Simple request queue to prevent overwhelming external APIs
 */
class RequestQueue {
    constructor(maxConcurrent = 3, minInterval = 1000) {
        this.queue = [];
        this.running = 0;
        this.maxConcurrent = maxConcurrent;
        this.minInterval = minInterval;
        this.lastRequestTime = 0;
    }

    async add(requestFn) {
        return new Promise((resolve, reject) => {
            this.queue.push({ requestFn, resolve, reject });
            this.process();
        });
    }

    async process() {
        if (this.running >= this.maxConcurrent || this.queue.length === 0) {
            return;
        }

        const now = Date.now();
        const timeSinceLastRequest = now - this.lastRequestTime;
        
        if (timeSinceLastRequest < this.minInterval) {
            setTimeout(() => this.process(), this.minInterval - timeSinceLastRequest);
            return;
        }

        const { requestFn, resolve, reject } = this.queue.shift();
        this.running++;
        this.lastRequestTime = Date.now();

        try {
            const result = await requestFn();
            resolve(result);
        } catch (error) {
            reject(error);
        } finally {
            this.running--;
            this.process();
        }
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        makeRateLimitedRequest,
        rateLimitedFetch,
        rateLimitedAxios,
        RequestQueue,
        sleep
    };
}

// Export for browser usage
if (typeof window !== 'undefined') {
    window.RateLimiter = {
        makeRateLimitedRequest,
        rateLimitedFetch,
        rateLimitedAxios,
        RequestQueue,
        sleep
    };
}

console.log('✅ Rate limiter utility loaded');
