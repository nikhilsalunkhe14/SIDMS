const BASE_URL = "http://localhost:5000";

/**
 * Build headers with an Authorization Bearer token (if available).
 * @param {HeadersInit} [extra] – additional headers to merge
 * @returns {Headers}
 */
function buildHeaders(extra = {}) {
    const headers = new Headers({
        "Content-Type": "application/json",
        ...extra,
    });

    const token = localStorage.getItem("token");
    if (token) {
        headers.set("Authorization", `Bearer ${token}`);
    }

    return headers;
}

/**
 * Reusable GET request.
 * @param {string} endpoint – path starting with `/`, e.g. `/api/users`
 * @param {HeadersInit} [extraHeaders]
 * @returns {Promise<Response>}
 */
export async function get(endpoint, extraHeaders) {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
        method: "GET",
        headers: buildHeaders(extraHeaders),
    });
    return response;
}

/**
 * Reusable POST request.
 * @param {string} endpoint – path starting with `/`, e.g. `/api/data`
 * @param {object}  body – will be JSON-stringified automatically
 * @param {HeadersInit} [extraHeaders]
 * @returns {Promise<Response>}
 */
export async function post(endpoint, body, extraHeaders) {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
        method: "POST",
        headers: buildHeaders(extraHeaders),
        body: JSON.stringify(body),
    });
    return response;
}
