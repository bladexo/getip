import requests
from bs4 import BeautifulSoup
import concurrent.futures
import time
import sys

# Function to scrape free proxies
def get_free_proxies():
    url = "https://www.us-proxy.org/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the textarea containing the proxy list
    textarea = soup.find("textarea", {"class": "form-control"})
    if not textarea:
        raise ValueError("Proxy list textarea not found on the page")

    # Extract proxies from the textarea content
    raw_proxies = textarea.get_text(strip=True).split('\n')
    proxies = [proxy.strip() for proxy in raw_proxies if proxy.strip()]

    if not proxies:
        raise ValueError("No proxies found in the textarea")

    return proxies

# Function to check if a proxy is active and doesn't require authorization
def check_proxy(proxy):
    test_url = "http://httpbin.org/ip"
    proxies = {"http": proxy, "https": proxy}

    try:
        response = requests.get(test_url, proxies=proxies, timeout=5)
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json()
        return proxy if 'origin' in data else None
    except (requests.HTTPError, requests.RequestException):
        return None

# Function to get valid proxies using concurrent checks
def get_valid_proxies(num_proxies=10):
    all_proxies = get_free_proxies()
    valid_proxies = []

    print("Searching for valid proxies. Please wait...", end='', flush=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_proxy = {executor.submit(check_proxy, proxy): proxy for proxy in all_proxies}
        
        for future in concurrent.futures.as_completed(future_to_proxy):
            proxy = future_to_proxy[future]
            try:
                result = future.result()
                if result:
                    valid_proxies.append(result)
                    print(f"\nValid proxy found: {result}")
                    if len(valid_proxies) >= num_proxies:
                        break
            except Exception as e:
                print(f"\nError checking proxy {proxy}: {e}")

            # Update loading indicator
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.1)  # Short delay to make the indicator visible

    print()  # Move to the next line after loading
    return valid_proxies

# Example usage
if __name__ == '__main__':
    num_proxies = 10  # Number of proxies to retrieve
    valid_proxies = get_valid_proxies(num_proxies=num_proxies)

    if valid_proxies:
        print(f"\nFound {len(valid_proxies)} valid proxies:")
        for proxy in valid_proxies:
            print(proxy)
    else:
        print("No valid proxies found.")
