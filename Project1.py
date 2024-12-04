import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_flipkart(search_query, num_products):
    """Scrape product data from Flipkart"""
    base_url = "https://www.flipkart.com/search?q="
    url = base_url + search_query.replace(" ", "+")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    # Save raw HTML response for debugging
    with open("flipkart_response.html", "w", encoding="utf-8") as file:
        file.write(response.text)

    soup = BeautifulSoup(response.content, "html.parser")

    products = []
    product_containers = soup.find_all("div", class_="_1AtVbE")
    if not product_containers:
        print("Flipkart HTML structure might have changed, or scraping was blocked.")
        return products

    for item in product_containers:
        name = item.find("div", class_="_4rR01T")
        price = item.find("div", class_="_30jeq3")
        discount = item.find("div", class_="_3Ay6Sb")
        seller = item.find("div", class_="_2fuX-1")
        link_tag = item.find("a", class_="_1fQZEK")

        if name and price and link_tag:
            products.append({
                "Name": name.text,
                "Price": price.text,
                "Discount": discount.text if discount else "N/A",
                "Seller": seller.text if seller else "N/A",
                "Link": f"https://www.flipkart.com{link_tag['href']}"
            })
        if len(products) >= num_products:
            break

    if not products:
        print("No products scraped from Flipkart.")
    return products

def scrape_amazon(search_query, num_products):
    """Scrape product data from Amazon"""
    base_url = "https://www.amazon.in/s?k="
    url = base_url + search_query.replace(" ", "+")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    response = requests.get(url, headers=headers)

    # Save raw HTML response for debugging
    with open("amazon_response.html", "w", encoding="utf-8") as file:
        file.write(response.text)

    soup = BeautifulSoup(response.content, "html.parser")

    product_container = soup.find("div", class_="s-main-slot")
    if not product_container:
        print("Amazon page structure has changed or the request was blocked.")
        return []

    products = []
    for item in product_container.find_all("div", class_="s-result-item"):
        name = item.find("span", class_="a-size-medium")
        price = item.find("span", class_="a-price-whole")
        seller = item.find("span", class_="a-size-small")
        link_tag = item.find("a", class_="a-link-normal")

        if name and price and link_tag:
            products.append({
                "Name": name.text.strip(),
                "Price": f"₹{price.text.strip()}",
                "Discount": "N/A",
                "Seller": seller.text.strip() if seller else "N/A",
                "Link": f"https://www.amazon.in{link_tag['href']}"
            })
        if len(products) >= num_products:
            break
    return products

def append_to_excel(data, filename, sheet_name):
    """Append data to a new sheet in an Excel file."""
    try:
        with pd.ExcelWriter(filename, engine="openpyxl", mode="a", if_sheet_exists="new") as writer:
            df = pd.DataFrame(data)
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    except FileNotFoundError:
        # Create a new file if it doesn't exist
        with pd.ExcelWriter(filename, engine="openpyxl") as writer:
            df = pd.DataFrame(data)
            df.to_excel(writer, sheet_name=sheet_name, index=False)

def main():
    search_query = input("Enter product name to search: ")
    num_products = int(input("Enter the number of products to fetch: "))
    
    # Scrape data from Flipkart
    print("Scraping Flipkart...")
    flipkart_products = scrape_flipkart(search_query, num_products)

    # Scrape data from Amazon
    print("Scraping Amazon...")
    amazon_products = scrape_amazon(search_query, num_products)

    # Save Flipkart and Amazon data to separate sheets
    filename = "products.xlsx"
    if flipkart_products:
        append_to_excel(flipkart_products, filename, f"Flipkart-{search_query}")
    else:
        print("No data available for Flipkart.")

    if amazon_products:
        append_to_excel(amazon_products, filename, f"Amazon-{search_query}")
    else:
        print("No data available for Amazon.")

    print(f"Scraped data for '{search_query}' has been added to '{filename}'.")

if __name__ == "__main__":
    main()
