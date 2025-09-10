"""
FastAPI Interceptor for Mitmproxy
Proper async implementation that works with mitmproxy's event loop
"""
from mitmproxy import http
import json
import asyncio
from datetime import datetime
import os
from typing import Dict, Tuple, Optional

# For HTTP calls, we'll use mitmproxy's built-in async support with urllib
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor

# Configuration - will be set via environment or config
#FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://host.docker.internal:8000")
# on EC2 use this
FASTAPI_BASE_URL = "https://mitmproxy-api.dev.mgraph.ai"
# on local docker use this
#FASTAPI_BASE_URL  = "http://host.docker.internal:10016"     # todo: make this work with env vars

REQUEST_ENDPOINT     = "/proxy/process-request"
RESPONSE_ENDPOINT    = "/proxy/process-response"
TIMEOUT              = 0.5  # Reduced timeout for faster fallback
VERSION__INTERCEPTOR = "v0.1.3"                                 # version of the interceptor (manual set)

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
        req = urllib.request.Request(url, data=json_data, headers={'Content-Type': 'application/json'})

        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            if response.status == 200:
                response_data = response.read()
                return json.loads(response_data)
    except Exception as e:
        # Silent fail - we'll use fallback
        return None


async def call_fastapi_async(endpoint: str, data: dict) -> dict:
    """Async wrapper that runs sync call in thread pool"""
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(executor, call_fastapi_sync, endpoint, data)
        return result
    except Exception:
        return None


def extract_debug_params(path: str) -> Tuple[Dict[str, str], str, str]:
    """
    Extract debug parameters from path if present
    Handles both encoded (%7B, %7D) and unencoded ({, }) brackets

    Args:
        path: The original request path

    Returns:
        Tuple of (debug_params dict, clean_path, original_path)
    """
    debug_params = {}
    original_path = path
    clean_path = path

    # First, decode URL-encoded brackets if present
    decoded_path = path.replace('%7B', '{').replace('%7D', '}')

    # Check if path starts with debug pattern /{key=value}/
    if decoded_path.startswith('/{') and '}/' in decoded_path:
        try:
            # Find the closing bracket in the decoded path
            end_bracket = decoded_path.index('}/')

            # Extract the debug string (without brackets)
            debug_string = decoded_path[2:end_bracket]  # Skip '/{'

            # Parse debug parameters
            for param in debug_string.split(','):
                if '=' in param:
                    key, value = param.split('=', 1)
                    debug_params[key.strip()] = value.strip()

            # For the clean path, we need to remove the debug portion from the ORIGINAL path
            # Calculate where the debug params end in the original (possibly encoded) path
            if '%7B' in path:
                # Path has encoded brackets
                end_bracket_original = path.index('%7D/') + 3  # +3 for '%7D'
            else:
                # Path has unencoded brackets
                end_bracket_original = path.index('}/') + 1  # +1 for '}'

            clean_path = path[end_bracket_original:]  # Keep the '/' after the bracket

        except (ValueError, IndexError) as e:
            print(f"  ⚠ Error parsing debug params: {e}")

    return debug_params, clean_path, original_path


def prepare_request_data(flow: http.HTTPFlow, debug_params: Dict[str, str], original_path: str) -> Dict:
    """
    Prepare request data for FastAPI

    Args:
        flow: The mitmproxy flow object
        debug_params: Extracted debug parameters
        original_path: Original path before cleaning

    Returns:
        Dictionary with request data for FastAPI
    """
    return {
        "method": flow.request.method,
        "host": flow.request.pretty_host,
        "path": flow.request.path,  # This is the clean path
        "original_path": original_path,
        "debug_params": debug_params,
        "headers": dict(flow.request.headers),
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

    Args:
        flow: The mitmproxy flow object
        modifications: Modifications dict from FastAPI

    Returns:
        True if request should be blocked, False otherwise
    """
    if not modifications:
        return False

    # Apply header modifications
    if "headers_to_add" in modifications:
        for key, value in modifications["headers_to_add"].items():
            flow.request.headers[key] = str(value)

    if "headers_to_remove" in modifications:
        for key in modifications["headers_to_remove"]:
            if key in flow.request.headers:
                del flow.request.headers[key]

    # Check if request should be blocked
    if modifications.get("block_request"):
        flow.response = http.Response.make(
            modifications.get("block_status", 403),
            modifications.get("block_message", "Blocked by proxy").encode(),
            {"Content-Type": "text/plain", "X-Blocked-By": "MGraph-Proxy"}
        )
        return True

    return False


async def request(flow: http.HTTPFlow) -> None:
    """
    Async request handler - mitmproxy will await this
    """
    global request_count, errors_count
    request_count += 1

    # Extract debug parameters and clean the path
    debug_params, clean_path, original_path = extract_debug_params(flow.request.path)

    # Update the flow with clean path (so upstream server doesn't see debug params)
    if debug_params:
        flow.request.path = clean_path
        # Also update the URL
        flow.request.url = flow.request.url.replace(original_path, clean_path)

        print(f"[REQUEST #{request_count}] {flow.request.method} {flow.request.pretty_host}")
        print(f"  🔧 Debug params: {debug_params}")
        print(f"  📝 Original: {original_path}")
        print(f"  ✨ Clean: {clean_path}")
    else:
        print(f"[REQUEST #{request_count}] {flow.request.method} {flow.request.pretty_host}{flow.request.path}")

    # Store debug params and original path in flow metadata for response phase
    flow.metadata['debug_params'] = debug_params
    flow.metadata['original_path'] = original_path

    # Always add basic tracking headers
    flow.request.headers["x-proxy-request-count"] = str(request_count)

    # Prepare and send data to FastAPI
    request_data = prepare_request_data(flow, debug_params, original_path)
    modifications = await call_fastapi_async(REQUEST_ENDPOINT, request_data)

    if modifications:
        # Apply modifications and check if blocked
        if apply_request_modifications(flow, modifications):
            print(f"  ❌ Request blocked")
            return

        flow.request.headers["x-proxy-status"] = "fastapi-connected"
        print(f"  ✓ Modified via FastAPI")
    else:
        # Fallback - FastAPI unavailable
        flow.request.headers["x-proxy-status"] = "fastapi-unavailable"
        flow.request.headers["x-proxy-fallback"] = "true"
        errors_count += 1
        print(f"  ⚠ Fallback mode")


def check_text_content(content_type: str, debug_params: Dict[str, str]) -> bool:
    """
    Check if content should be processed as text based on content type and debug params

    Args:
        content_type: The content-type header value
        debug_params: Debug parameters that might override default behavior

    Returns:
        True if content should be processed as text
    """
    # Always capture HTML and plain text
    text_types = [
        "text/html",
        "text/plain",
    ]

    # Check debug params for additional types to capture
    if debug_params.get('capture_all') == 'true':
        return True
    if debug_params.get('capture_json') == 'true':
        text_types.append("application/json")
    if debug_params.get('capture_css') == 'true':
        text_types.append("text/css")
    if debug_params.get('capture_js') == 'true':
        text_types.extend(["text/javascript", "application/javascript"])
    if debug_params.get('capture_xml') == 'true':
        text_types.append("application/xml")

    return any(t in content_type for t in text_types)


async def response(flow: http.HTTPFlow) -> None:
    """
    Async response handler - mitmproxy will await this
    """
    global response_count, errors_count
    response_count += 1

    # Retrieve debug params and original path from request phase
    debug_params = flow.metadata.get('debug_params', {})
    original_path = flow.metadata.get('original_path', flow.request.path)

    print(f"[RESPONSE #{response_count}] {flow.response.status_code} from {flow.request.pretty_host}")
    if debug_params:
        print(f"  🔧 Debug params active: {debug_params}")

    # Always add basic tracking headers
    flow.response.headers["x-proxy-response-count"] = str(response_count)

    # NO MORE DEBUG INJECTIONS HERE - just prepare data for FastAPI

    # Prepare and send data to FastAPI (including body for text content)
    response_data = prepare_response_data(flow, debug_params, original_path)
    modifications = await call_fastapi_async(RESPONSE_ENDPOINT, response_data)

    if modifications:
        apply_response_modifications(flow, modifications, debug_params)
        flow.response.headers["x-proxy-status"] = "fastapi-connected"
        flow.response.headers["x-fastapi-url"] = FASTAPI_BASE_URL
        print(f"  ✓ Modified via FastAPI")
    else:
        # Fallback - FastAPI unavailable
        flow.response.headers["x-proxy-status"] = "fastapi-unavailable"
        flow.response.headers["x-proxy-fallback"] = "true"
        flow.response.headers["x-fastapi-url"] = FASTAPI_BASE_URL
        errors_count += 1
        print(f"  ⚠ Fallback mode")


def extract_body_content(flow: http.HTTPFlow, content_type: str) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    """
    Extract body content from response if it's text

    Args:
        flow: The mitmproxy flow object
        content_type: The content-type of the response

    Returns:
        Tuple of (content, size, error)
    """
    if not flow.response.content:
        return None, 0, None

    try:
        content = flow.response.content.decode('utf-8', errors='ignore')
        return content, len(content), None
    except Exception as e:
        return None, 0, str(e)


def prepare_response_data(flow: http.HTTPFlow, debug_params: Dict[str, str], original_path: str) -> Dict:
    """
    Prepare response data for FastAPI

    Args:
        flow: The mitmproxy flow object
        debug_params: Debug parameters from request phase
        original_path: Original path from request phase

    Returns:
        Dictionary with response data for FastAPI
    """
    content_type = flow.response.headers.get("content-type", "").lower()

    response_data = {
        "request": {
            "method": flow.request.method,
            "host": flow.request.pretty_host,
            "path": flow.request.path,
            "original_path": original_path,
            "url": flow.request.pretty_url,
        },
        "debug_params": debug_params,
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

    # Include body content if appropriate
    is_text_content = check_text_content(content_type, debug_params)
    if is_text_content:
        content, size, error = extract_body_content(flow, content_type)
        if content:
            response_data["response"]["body"] = content
            response_data["response"]["body_size"] = size
            print(f"  → Sending {size} chars of {content_type} content")
        elif error:
            response_data["response"]["body_error"] = error
            print(f"  ⚠ Could not decode body: {error}")

    return response_data


def apply_response_modifications(flow: http.HTTPFlow, modifications: Dict, debug_params: Dict[str, str]) -> None:
    """
    Apply modifications from FastAPI to the response
    """
    if not modifications:
        return

    # Check if we need to completely override the response
    if modifications.get("override_response"):
        # Override status code if specified
        if modifications.get("override_status"):
            flow.response.status_code = modifications["override_status"]

        # Override content type if specified
        if modifications.get("override_content_type"):
            flow.response.headers["Content-Type"] = modifications["override_content_type"]

        # Set the body to the debug output
        if modifications.get("modified_body"):
            flow.response.content = str(modifications["modified_body"]).encode('utf-8')
            flow.response.headers["Content-Length"] = str(len(flow.response.content))

    # Apply header modifications
    if "headers_to_add" in modifications:
        for key, value in modifications["headers_to_add"].items():
            flow.response.headers[key] = str(value)

    if "headers_to_remove" in modifications:
        for key in modifications["headers_to_remove"]:
            if key in flow.response.headers:
                del flow.response.headers[key]

    # Apply body modifications if provided
    if "modified_body" in modifications:
        modified_content = modifications["modified_body"]
        # Only apply if we actually have content to apply
        if modified_content is not None and modified_content != "":
            try:
                # Handle both string and bytes
                if isinstance(modified_content, bytes):
                    flow.response.content = modified_content
                else:
                    flow.response.content = str(modified_content).encode('utf-8')

                flow.response.headers["content-length"] = str(len(flow.response.content))
                flow.response.headers["x-content-modified"] = "true"
                print(f"  ✓ Body modified: {len(flow.response.content)} bytes")
            except Exception as e:
                print(f"  ⚠ Error modifying body: {e}")
                global errors_count
                errors_count += 1

    # Add statistics headers if requested
    if modifications.get("include_stats"):
        stats = modifications.get("stats", {})
        flow.response.headers["x-proxy-stats"] = json.dumps(stats)


def done():
    """Cleanup when mitmproxy shuts down"""
    executor.shutdown(wait=False)
    print("FastAPI Interceptor shutting down")


print("=" * 60)
print("FastAPI Interceptor Loaded! (Async Version)")
print(f"Version: {VERSION__INTERCEPTOR}")
print(f"Delegating to: {FASTAPI_BASE_URL}")
print(f"Timeout: {TIMEOUT}s, Workers: 10")
print("Debug params support: ENABLED")
print("  Example: /{debug=true,capture_all=true}/path/to/resource")
print("=" * 60)