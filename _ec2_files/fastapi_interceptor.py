"""
FastAPI Interceptor for Mitmproxy
Minimal interceptor - just captures and forwards everything to FastAPI
ALL logic happens in the FastAPI service
Control via cookies only (mitm-* cookies)
"""
from mitmproxy import http
import json
import asyncio
from datetime import datetime
from typing import Dict, Tuple, Optional

# For HTTP calls
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor

# Configuration
FASTAPI_BASE_URL = "https://mitmproxy-api.dev.mgraph.ai"
# on local docker use this (note: at the moment this is done manually during development)
FASTAPI_BASE_URL  = "http://host.docker.internal:10016"     # todo: make this work with env vars

REQUEST_ENDPOINT     = "/proxy/process-request"
RESPONSE_ENDPOINT    = "/proxy/process-response"
TIMEOUT              = 5.0
VERSION__INTERCEPTOR = "v0.2.1"  # cookies only, no path params

# Stats tracking
request_count = 0
response_count = 0
errors_count = 0

# Thread pool for non-blocking HTTP calls
executor = ThreadPoolExecutor(max_workers=10)


def call_fastapi_sync(endpoint: str, data: dict) -> dict:
    """Synchronous FastAPI call for use in thread pool"""
    url = f"{FASTAPI_BASE_URL}{endpoint}"

    try:
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=json_data, headers={'content-type': 'application/json'})

        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            if response.status == 200:
                response_data = response.read()
                return json.loads(response_data)
    except Exception as e:
        return None


async def call_fastapi_async(endpoint: str, data: dict) -> dict:
    """Async wrapper that runs sync call in thread pool"""
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(executor, call_fastapi_sync, endpoint, data)
        return result
    except Exception:
        return None


def prepare_request_data(flow: http.HTTPFlow) -> Dict:
    """
    Prepare request data for FastAPI
    Just capture everything - no path parsing, no cookie parsing

    NOTE: headers dict includes Cookie header - FastAPI will parse it
    """
    return {
        "method": flow.request.method,
        "host": flow.request.pretty_host,
        "path": flow.request.path,
        "original_path": flow.request.path,  # No path modification anymore
        "debug_params": {},  # Empty - FastAPI will extract from cookies
        "headers": dict(flow.request.headers),  # Includes Cookie header
        "stats": {
            "request_count": request_count,
            "errors_count": errors_count,
            "timestamp": datetime.utcnow().isoformat()
        },
        "version": VERSION__INTERCEPTOR
    }


def apply_request_modifications(flow: http.HTTPFlow, modifications: Dict) -> bool:
    """
    Apply modifications from FastAPI to the request
    Returns: True if request should be blocked
    """
    if not modifications:
        return False

    if "headers_to_add" in modifications:
        for key, value in modifications["headers_to_add"].items():
            flow.request.headers[key] = str(value)

    if "headers_to_remove" in modifications:
        for key in modifications["headers_to_remove"]:
            if key in flow.request.headers:
                del flow.request.headers[key]

    if modifications.get("block_request"):
        flow.response = http.Response.make(
            modifications.get("block_status", 403),
            modifications.get("block_message", "Blocked by proxy").encode(),
            {"content-type": "text/plain", "x-blocked-by": "MGraph-Proxy"}
        )
        return True

    return False


async def request(flow: http.HTTPFlow) -> None:
    """Request handler - capture and forward to FastAPI"""
    global request_count, errors_count
    request_count += 1

    print(f"[REQUEST #{request_count}] {flow.request.method} {flow.request.pretty_host}{flow.request.path}")

    # Add tracking header
    flow.request.headers["x-proxy-request-count"] = str(request_count)

    # Prepare and send to FastAPI
    request_data = prepare_request_data(flow)
    modifications = await call_fastapi_async(REQUEST_ENDPOINT, request_data)

    if modifications:
        # Check for cached response
        if modifications.get("cached_response"):
            cached = modifications["cached_response"]
            flow.response = http.Response.make(
                cached.get("status_code", 200),
                cached.get("body", "").encode('utf-8') if isinstance(cached.get("body"), str) else cached.get("body", b""),
                cached.get("headers", {"content-type": "text/html"})
            )
            flow.response.headers["x-proxy-status"] = "fastapi-cached"
            print(f"  ✓ Served from cache")
            return

        # Apply modifications
        if apply_request_modifications(flow, modifications):
            print(f"  ❌ Request blocked")
            return

        flow.request.headers["x-proxy-status"] = "fastapi-connected"
        print(f"  ✓ Modified via FastAPI")
    else:
        flow.request.headers["x-proxy-status"] = "fastapi-unavailable"
        errors_count += 1
        print(f"  ⚠ Fallback mode")


def check_text_content(content_type: str) -> bool:
    """Check if content should be captured - basic types only"""
    text_types = ["text/html", "text/plain", "application/json"]
    return any(t in content_type.lower() for t in text_types)


def extract_body_content(flow: http.HTTPFlow) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    """Extract body content if it's text"""
    if not flow.response.content:
        return None, 0, None

    try:
        content = flow.response.content.decode('utf-8', errors='ignore')
        return content, len(content), None
    except Exception as e:
        return None, 0, str(e)


def prepare_response_data(flow: http.HTTPFlow) -> Dict:
    """
    Prepare response data for FastAPI
    Just capture everything - no parsing

    NOTE: request['headers'] includes Cookie header from original request
    """
    content_type = flow.response.headers.get("content-type", "").lower()

    response_data = {
        "request": {
            "method": flow.request.method,
            "host": flow.request.pretty_host,
            "path": flow.request.path,
            "original_path": flow.request.path,  # No path modification
            "url": flow.request.pretty_url,
            "headers": dict(flow.request.headers),  # Includes Cookie header
        },
        "debug_params": {},  # Empty - FastAPI will extract from cookies
        "response": {
            "status_code": flow.response.status_code,
            "headers": dict(flow.response.headers),
            "content_type": content_type,
        },
        "stats": {
            "response_count": response_count,
            "request_count": request_count,
            "errors_count": errors_count,
            "timestamp": datetime.utcnow().isoformat()
        },
        "version": VERSION__INTERCEPTOR
    }

    # Include body if text content
    if check_text_content(content_type):
        content, size, error = extract_body_content(flow)
        if content:
            response_data["response"]["body"] = content
            response_data["response"]["body_size"] = size
            print(f"  → Sending {size} chars")
        elif error:
            response_data["response"]["body_error"] = error

    return response_data


def apply_response_modifications(flow: http.HTTPFlow, modifications: Dict) -> None:
    """Apply modifications from FastAPI to response"""
    if not modifications:
        return

    # Check for complete response override
    if modifications.get("override_response"):
        if modifications.get("override_status"):
            flow.response.status_code = modifications["override_status"]

        if modifications.get("override_content_type"):
            flow.response.headers["content-type"] = modifications["override_content_type"]

        if modifications.get("modified_body"):
            flow.response.content = str(modifications["modified_body"]).encode('utf-8')
            flow.response.headers["content-length"] = str(len(flow.response.content))

    # Apply header modifications
    if "headers_to_add" in modifications:
        for key, value in modifications["headers_to_add"].items():
            flow.response.headers[key] = str(value)

    if "headers_to_remove" in modifications:
        for key in modifications["headers_to_remove"]:
            if key in flow.response.headers:
                del flow.response.headers[key]

    # Apply body modifications
    if "modified_body" in modifications and modifications["modified_body"]:
        try:
            content = modifications["modified_body"]
            if isinstance(content, bytes):
                flow.response.content = content
            else:
                flow.response.content = str(content).encode('utf-8')

            flow.response.headers["content-length"] = str(len(flow.response.content))
            print(f"  ✓ Body modified: {len(flow.response.content)} bytes")
        except Exception as e:
            print(f"  ⚠ Error modifying body: {e}")

    # Add stats if requested
    if modifications.get("include_stats"):
        flow.response.headers["x-proxy-stats"] = json.dumps(modifications.get("stats", {}))


async def response(flow: http.HTTPFlow) -> None:
    """Response handler - capture and forward to FastAPI"""
    global response_count
    response_count += 1

    print(f"[RESPONSE #{response_count}] {flow.response.status_code} from {flow.request.pretty_host}")

    # Add tracking header
    flow.response.headers["x-proxy-response-count"] = str(response_count)

    # Prepare and send to FastAPI
    response_data = prepare_response_data(flow)
    modifications = await call_fastapi_async(RESPONSE_ENDPOINT, response_data)

    if modifications:
        apply_response_modifications(flow, modifications)
        flow.response.headers["x-proxy-status"] = "fastapi-connected"
        print(f"  ✓ Modified via FastAPI")
    else:
        flow.response.headers["x-proxy-status"] = "fastapi-unavailable"
        print(f"  ⚠ Fallback mode")


def done():
    """Cleanup"""
    executor.shutdown(wait=False)


print("=" * 60)
print("FastAPI Interceptor Loaded!")
print(f"Version: {VERSION__INTERCEPTOR}")
print(f"FastAPI: {FASTAPI_BASE_URL}")
print("Control via cookies: mitm-show, mitm-inject, mitm-debug, etc.")
print("=" * 60)