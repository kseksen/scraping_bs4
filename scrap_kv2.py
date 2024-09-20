import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import warnings
from urllib3.exceptions import NotOpenSSLWarning

warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

home_url = "http://books.toscrape.com/"

response = requests.get(home_url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

    categories = soup.find('div', class_='side_categories').find_all('a')

    category_links = [urljoin(home_url, category['href']) for category in categories]
    print("Category Links:", category_links)

    book_data = []

    for category_link in category_links:
        print(f"Scraping category: {category_link}")
        response = requests.get(category_link)
        if response.status_code == 200:
            category_soup = BeautifulSoup(response.content, 'html.parser')
            books = category_soup.find_all('article', class_='product_pod')

            print(f"Found {len(books)} books in this category.")

            for book in books:
                try:
                    title = book.h3.a['title']
                    print(f"Title: {title}")

                    price_text = book.find('p', class_='price_color').get_text()
                    price = float(price_text[1:])  
                    print(f"Price: {price}")

                    stock_text = book.find('p', class_='instock availability').get_text().strip()
                    stock = int(stock_text.split('(')[-1].split()[0]) if '(' in stock_text else 0
                    print(f"Stock: {stock}")

                    relative_url = book.h3.a['href']
                    description_url = urljoin(category_link, relative_url)
                    print(f"Scraping book: {description_url}")

                    description_response = requests.get(description_url)
                    if description_response.status_code == 200:
                        print("Book detail page fetched successfully.")
                        description_soup = BeautifulSoup(description_response.content, 'html.parser')

                        description_meta = description_soup.find('meta', attrs={'name': 'description'})
                        if description_meta:
                            description = description_meta['content'].strip()
                        else:
                            description_paragraph = description_soup.find('article', class_='product_page').find_all('p')
                            description = description_paragraph[0].get_text().strip() if description_paragraph else "No description available."

                        print(f"Description: {description}")

                        book_data.append({
                            'title': title,
                            'price': price,
                            'stock': stock,
                            'description': description
                        })
                        print(f"Book appended: {title}")

                    else:
                        print(f"Failed to fetch book details for {description_url}")

                except Exception as e:
                    print(f"Error extracting book details: {e}")

with open('books_data.json', 'w') as file:
    json.dump(book_data, file, indent=4)

print(f"Successfully extracted data for {len(book_data)} books.")