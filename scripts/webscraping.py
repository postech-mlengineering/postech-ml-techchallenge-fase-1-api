import requests
from bs4 import BeautifulSoup
import pandas as pd
import re 
import logging
from typing import List, Dict, Any, Optional


BASE_URL = "http://books.toscrape.com/"
HOME_URL = BASE_URL + "index.html"
DATA = []


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def clean_currency(currency_str: str) -> float:
    """
    Limpa a string de preço, removendo caracteres de moeda (£, etc.) 
    e convertendo para float.
    """
    cleaned_str = currency_str.replace('Â', '').replace('£', '')
    try:
        return float(cleaned_str)
    except ValueError:
        logging.warning(f"Não foi possível converter o preço: {currency_str} para float. Retornando 0.0")
        return 0.0


def extract_number_from_availability(availability_text: str) -> int:
    """Extrai o número de estoque disponível (e.g., 22 de 'In stock (22 available)')."""
    match = re.search(r'\d+', availability_text)
    return int(match.group()) if match else 0


def get_category_links() -> List[Dict[str, str]]:
    """Coleta o nome e a URL inicial de todas as categorias na página inicial."""
    logging.info("Iniciando a coleta de links de categorias...")

    try:
        home_response = requests.get(HOME_URL, timeout=10)
        home_response.raise_for_status() 
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao acessar a URL inicial: {e}")
        return []
    
    home_soup = BeautifulSoup(home_response.text, 'html.parser')
    
    #encontra a lista de categorias
    category_list_html = home_soup.find('ul', class_='nav nav-list').find('ul').find_all('li')
    
    categories = []
    for item in category_list_html:
        tag_a = item.find('a')
        category_name = tag_a.text.strip()
        relative_link = tag_a['href']
        
        #constrói a url absoluta
        category_url = BASE_URL + relative_link 
        
        categories.append({
            'name': category_name,
            'initial_url': category_url
        })
        
    logging.info(f"Total de {len(categories)} categorias encontradas.")
    return categories


def extract_book_details(url: str, genre: str) -> Optional[Dict[str, Any]]:
    """Acessa a página de detalhes de um livro e extrai todas as informações."""
    try:
        detail_response = requests.get(url, timeout=10)
        detail_response.raise_for_status()
        detail_soup = BeautifulSoup(detail_response.text, 'html.parser')

        #extraindo dados simples
        title = detail_soup.find('h1').text
        
        #preço principal
        price = detail_soup.find('p', class_='price_color').text
        price = clean_currency(price)

        #descrição
        description_tag = detail_soup.find('div', id='product_description')
        description = description_tag.find_next_sibling('p').text if description_tag else 'No Description'

        #avaliação em estrelas
        rating_tag = detail_soup.find('p', class_='star-rating')
        rating = rating_tag['class'][1] if rating_tag else 'No Rating'

        #tabela de informações
        product_table = detail_soup.find('table', class_='table-striped').find_all('td')
        
        #extração de dados da tabela
        upc = product_table[0].text
        product_type = product_table[1].text
        
        price_excl_tax = clean_currency(product_table[2].text)
        price_incl_tax = clean_currency(product_table[3].text)
        tax = clean_currency(product_table[4].text)

        availability_text = product_table[5].text
        availability = extract_number_from_availability(availability_text)
        
        number_of_reviews = int(product_table[6].text) if product_table[6].text.isdigit() else 0

        return {
            'title': title,
            'genre': genre,
            'price': price,
            'upc': upc,
            'product_type': product_type,
            'price_excl_tax': price_excl_tax,
            'price_incl_tax': price_incl_tax,
            'tax': tax,
            'number_of_reviews': number_of_reviews,
            'availability': availability,
            'rating': rating,
            'description': description,
            'url': url
        }
    except Exception as e:
        logging.error(f"Erro ao extrair detalhes de {url}: {e}")
        return None


def scrape_category(category: Dict[str, str]) -> None:
    """Itera sobre todas as páginas de uma categoria, extrai os links e os detalhes dos livros."""
    genre_name = category['name']
    current_url = category['initial_url']
    page_number = 1

    logging.info(f"Scraping gênero: {genre_name}")

    while True:
        logging.info(f"  > Processando {genre_name} - pag. {page_number}")

        try:
            page_response = requests.get(current_url, timeout=15)
            page_response.raise_for_status()
            page_soup = BeautifulSoup(page_response.text, 'html.parser')
            
            #encontrar todos os livros na página atual
            books_on_page = page_soup.find_all('article', class_='product_pod')
            
            #iterar sobre os links de livros
            for book in books_on_page:
                relative_link = book.find('h3').find('a')['href']
                #ajusta o link relativo para ser absoluto, removendo o padrão "../../"
                url = BASE_URL + 'catalogue/' + relative_link.replace('../', '')
                #extrair e adicionar os detalhes
                book_data = extract_book_details(url, genre_name)
                if book_data:
                    DATA.append(book_data)
            
            #verificar Paginação ("next" button)
            next_button = page_soup.find('li', class_='next')
            
            if next_button:
                #se houver botão 'next', atualiza a URL para a próxima página
                link_next = next_button.find('a')['href']
                
                #cria a URL completa para a próxima página
                url_parts = current_url.split('/')
                current_url = '/'.join(url_parts[:-1]) + '/' + link_next
                page_number += 1
            else:
                #não há mais páginas, sai do loop
                break

        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao processar a página {current_url}: {e}")
            break
        except Exception as e:
            logging.error(f"Erro inesperado ao raspar categoria {genre_name}: {e}")
            break


if __name__ == "__main__":
    #coleta todos os links de gênero
    categories_list = get_category_links()
    
    #processa cada gênero
    for category in categories_list:
        scrape_category(category)
        
    logging.info(f"\nTotal de {len(DATA)} livros coletados.")

    #criação do DataFrame
    if DATA:
        #cria o DataFrame
        df_books = pd.DataFrame(DATA)
        
        # Colunas ordenadas para o output final
        ordered_columns = [
            'title', 
            'genre', 
            'price', 
            'availability', 
            'rating', 
            'upc', 
            'description',
            'product_type', 
            'price_excl_tax', 
            'price_incl_tax', 
            'tax', 
            'number_of_reviews',
            'url'
        ]
        
        df_books = df_books[ordered_columns]

        logging.info("\nDataFrame criado com sucesso!")
        print(df_books.head())
        
        #exporta dados em arquivo em csv
        file_path = '../data/books.csv'
        df_books.to_csv(file_path, index=False, encoding='utf-8')
        logging.info(f"\nDados salvos em '{file_path}'")
    else:
        logging.warning("Nenhum dado de livro foi coletado.")