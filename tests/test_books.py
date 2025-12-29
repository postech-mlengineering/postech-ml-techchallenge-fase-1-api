import pytest
from unittest.mock import patch
from flask_jwt_extended import create_access_token


@pytest.mark.books
class TestBooks:
    def _get_mock_token(self):
        """Cria um token mock válido para testes"""
        # Cria um token somente para vlaidar o endpoint
        return create_access_token(identity='test_user')
    

    # ========== TESTES DO ENDOINT /titles ==========
    @pytest.mark.integration
    @pytest.mark.titles
    #Definindo o mock_get_titles
    @patch('api.routes.books.get_all_book_titles')
    def test_quando_buscar_titulos_com_sucesso_deve_retornar_200_com_lista(self, mock_get_titles, client):
        #given
        titulos_esperados = [
            {'title': 'A Light in the Attic'},
            {'title': 'Tipping the Velvet'},
            {'title': 'Soumission'}
        ]
        mock_get_titles.return_value = titulos_esperados
        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        #when
        response = client.get('/api/v1/books/titles', headers=headers)
        resultado = response.get_json()
        
        #then
        assert response.status_code == 200
        assert isinstance(resultado, list)
        assert resultado == titulos_esperados
        mock_get_titles.assert_called_once()
    
    @pytest.mark.integration
    @pytest.mark.titles
    @patch('api.routes.books.get_all_book_titles')
    def test_quando_buscar_titulos_e_estiver_vazia(self, mock_get_titles, client):

        #given
        mock_get_titles.return_value = []
        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}

        #when
        response = client.get('/api/v1/books/titles', headers=headers)
        resultado = response.get_json()

        #then
        assert response.status_code == 200
        assert resultado['msg'] == 'Não há livros cadastrados'
        mock_get_titles.assert_called_once()

    # ========== TESTES DO ENDPOINT /<string:id>' ==========
    @pytest.mark.integration
    @pytest.mark.book_id
    @patch('api.routes.books.get_book_by_id')
    def test_quando_buscar_livro_por_id_com_sucesso_deve_retornar_200_com_detalhes(self, mock_get_book_by_id, client):
        #given
        livro_esperado = {
            'id': 1,
            'upc': 'a228380e22709289',
            'title': 'The White Queen',
            'genre': 'Historical',
            'price': 5.99,
            'availability': 5,
            'rating': 'Five stars',
            'description': 'A description...',
            'product_type': 'books',
            'price_excl_tax': 5.99,
            'price_incl_tax': 5.99,
            'tax': 0.00,
            'number_of_reviews': 1,
            'url': 'http://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html',
            'image_url': 'http://books.toscrape.com/media/cache/fe/8a/fe8af6ceec7718986380c0fde9b3b34f.jpg'
        }
        mock_get_book_by_id.return_value = livro_esperado
        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        #when
        response = client.get('/api/v1/books/1', headers=headers)
        resultado = response.get_json()
        
        #then
        assert response.status_code == 200
        assert isinstance(resultado, dict)
        assert resultado == livro_esperado
        mock_get_book_by_id.assert_called_once_with('1')

    @pytest.mark.integration
    @pytest.mark.book_id
    @patch('api.routes.books.get_book_by_id')
    def test_quando_buscar_livro_por_id_nao_encontrado_deve_retornar_404(self, mock_get_book_by_id, client):
        #given
        mock_get_book_by_id.return_value = None
        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        #when
        response = client.get('/api/v1/books/999', headers=headers)
        resultado = response.get_json()
        
        #then
        assert response.status_code == 404
        assert resultado['msg'] == 'Livro com id 999 não encontrado'
        mock_get_book_by_id.assert_called_once_with('999')

    # ========== TESTES DO ENDPOINT /search ==========
    @pytest.mark.integration
    @pytest.mark.search
    @patch('api.routes.books.get_books_by_title_or_category')
    def test_quando_buscar_por_titulo_com_sucesso_deve_retornar_200_com_lista(self, mock_get_books, client):
        #given
        livros_esperados = [
            {
                'id': 43,
                'upc': 'f684a82adc49f011',
                'title': 'A Murder in Time',
                'genre': 'Mystery',
                'price': 53.98,
                'image_url': 'http://books.toscrape.com/media/cache/f6/8e/f68e6ae2f9da04fccbde8442b0a1b52a.jpg'
            },
            {
                'id': 15,
                'upc': 'f733e8c19d40ec2e',
                'title': 'A Murder in Time',
                'genre': 'Mystery',
                'price': 16.64,
                'image_url': 'http://books.toscrape.com/media/cache/cc/bd/ccbd7a62caefd5a3a2e04dd7c2ff48fe.jpg'
            }
        ]
        mock_get_books.return_value = livros_esperados
        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        #when
        response = client.get('/api/v1/books/search?title=Murder', headers=headers)
        resultado = response.get_json()
        
        #then
        assert response.status_code == 200
        assert isinstance(resultado, list)
        assert resultado == livros_esperados
        mock_get_books.assert_called_once_with(title='Murder', genre=None)

    @pytest.mark.integration
    @pytest.mark.search
    @patch('api.routes.books.get_books_by_title_or_category')
    def test_quando_buscar_por_genero_com_sucesso_deve_retornar_200_com_lista(self, mock_get_books, client):
        #given
        livros_esperados = [
            {
                'id': 10,
                'upc': 'abc123',
                'title': 'Mystery Book',
                'genre': 'Mystery',
                'price': 20.50,
                'image_url': 'http://example.com/image.jpg'
            }
        ]
        mock_get_books.return_value = livros_esperados
        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        #when
        response = client.get('/api/v1/books/search?genre=Mystery', headers=headers)
        resultado = response.get_json()
        
        #then
        assert response.status_code == 200
        assert isinstance(resultado, list)
        assert resultado == livros_esperados
        mock_get_books.assert_called_once_with(title=None, genre='Mystery')

    @pytest.mark.integration
    @pytest.mark.search
    @patch('api.routes.books.get_books_by_title_or_category')
    def test_quando_buscar_por_titulo_e_genero_com_sucesso_deve_retornar_200(self, mock_get_books, client):
        #given
        livros_esperados = [
            {
                'id': 1, 
                'upc': '123', 
                'title': 'Test Book', 
                'genre': 'Fiction', 
                'price': 15.99, 
                'image_url': 'http://example.com/img.jpg'
            }
        
        ]
        mock_get_books.return_value = livros_esperados
        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        #when
        response = client.get('/api/v1/books/search?title=Test&genre=Fiction', headers=headers)
        resultado = response.get_json()
        
        #then
        assert response.status_code == 200
        assert resultado == livros_esperados
        mock_get_books.assert_called_once_with(title='Test', genre='Fiction')

    @pytest.mark.integration
    @pytest.mark.search
    def test_quando_buscar_sem_parametros_deve_retornar_400(self, client):
        #given
        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        #when
        response = client.get('/api/v1/books/search', headers=headers)
        resultado = response.get_json()
        
        #then
        assert response.status_code == 400
        assert resultado['msg'] == 'Forneça o parâmetro title e/ou genre para a consulta.'

    @pytest.mark.integration
    @pytest.mark.search
    @patch('api.routes.books.get_books_by_title_or_category')
    def test_quando_buscar_e_nao_encontrar_livros_deve_retornar_404(self, mock_get_books, client):
        #given
        mock_get_books.return_value = None
        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        #when
        response = client.get('/api/v1/books/search?title=Inexistente', headers=headers)
        resultado = response.get_json()
        
        #then
        assert response.status_code == 404
        assert resultado['msg'] == 'Nenhum livro encontrado com os parâmetros fornecidos'
        mock_get_books.assert_called_once_with(title='Inexistente', genre=None)

    # ========== TESTES DO ENDPOINT /price-range ==========
    @pytest.mark.integration
    @pytest.mark.price_range
    @patch('api.routes.books.get_books_by_price_range')
    def test_quando_buscar_por_faixa_preco_com_sucesso_deve_retornar_200(self, mock_get_books, client):
        #given
        livros_esperados = [
            {
                'id': 42,
                'genre': 'Young Adult',
                'price': 10.0,
                'title': 'An Abundance of Katherines',
                'upc': 'f36d24c309e87e5b',
                'image_url': 'http://books.toscrape.com/media/cache/d5/45/d54527d34174d5dd7eaeaaffdfcb3c5c.jpg'
            },
            {
                'id': 805,
                'genre': 'Science',
                'price': 10.01,
                'title': 'The Origin of Species',
                'upc': '0345872b14f9e774',
                'image_url': 'http://books.toscrape.com/media/cache/9b/c8/9bc86bc10a6beea536422bbe82e076fb.jpg'
            }
        ]
        mock_get_books.return_value = livros_esperados
        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        #when
        response = client.get('/api/v1/books/price-range?min=10&max=15', headers=headers)
        resultado = response.get_json()
        
        #then
        assert response.status_code == 200
        assert isinstance(resultado, list)
        assert resultado == livros_esperados
        mock_get_books.assert_called_once_with(min_price=10.0, max_price=15.0)
    
    @pytest.mark.integration
    @pytest.mark.price_range
    def test_quando_buscar_por_faixa_preco_sem_parametro_min_deve_retornar_400(self, client):
        #given
        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        #when
        response = client.get('/api/v1/books/price-range?max=15', headers=headers)
        resultado = response.get_json()
        
        #then
        assert response.status_code == 400
        assert resultado['msg'] == 'Os parâmetros min e max são obrigatórios.'

    @pytest.mark.integration
    @pytest.mark.price_range
    def test_quando_buscar_por_faixa_preco_sem_parametro_max_deve_retornar_400(self, client):
        #given
        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        #when
        response = client.get('/api/v1/books/price-range?min=10', headers=headers)
        resultado = response.get_json()
        
        #then
        assert response.status_code == 400
        assert resultado['msg'] == 'Os parâmetros min e max são obrigatórios.'

    @pytest.mark.integration
    @pytest.mark.price_range
    def test_quando_buscar_por_faixa_preco_sem_parametros_deve_retornar_400(self, client):
        #given
        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        #when
        response = client.get('/api/v1/books/price-range', headers=headers)
        resultado = response.get_json()
        
        #then
        assert response.status_code == 400
        assert resultado['msg'] == 'Os parâmetros min e max são obrigatórios.'

    @pytest.mark.integration
    @pytest.mark.price_range
    @patch('api.routes.books.get_books_by_price_range')
    def test_quando_buscar_por_faixa_preco_e_nao_encontrar_deve_retornar_404(self, mock_get_books, client):
        #given
        mock_get_books.return_value = None
        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        #when
        response = client.get('/api/v1/books/price-range?min=1000&max=2000', headers=headers)
        resultado = response.get_json()
        
        #then
        assert response.status_code == 404
        assert resultado['msg'] == 'Nenhum livro encontrado na faixa de preço informada.'
        mock_get_books.assert_called_once_with(min_price=1000.0, max_price=2000.0)


    # ========== TESTES DO ENDPOINT /top-rated ==========
    @pytest.mark.integration
    @pytest.mark.top_rated
    @patch('api.routes.books.get_top_rated_books')
    def test_quando_buscar_top_rated_com_sucesso_deve_retornar_200_com_lista(self, mock_get_top_rated, client):
        #given
        livros_esperados = [
            {
                'id': 11,
                'genre': 'Travel',
                'price': 26.08,
                'rating': 'Five',
                'title': '1,000 Places to See Before You Die',
                'upc': '228ba5e7577e1d49',
                'image_url': 'http://books.toscrape.com/media/cache/9e/10/9e106f81f65b293e488718a4f54a6a3f.jpg'
            },
            {
                'id': 993,
                'genre': 'Health',
                'price': 49.71,
                'rating': 'Five',
                'title': '110-Day Green Smoothie Cleanse: Lose Up to 15 Pounds in 10 Days!',
                'upc': '96aa539bfd4c07e2',
                'image_url': 'http://books.toscrape.com/media/cache/79/84/7984ef7c568a60372f430c1ddae64034.jpg'
            }
        ]
        mock_get_top_rated.return_value = livros_esperados
        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        #when
        response = client.get('/api/v1/books/top-rated', headers=headers)
        resultado = response.get_json()
        
        #then
        assert response.status_code == 200
        assert isinstance(resultado, list)
        assert resultado == livros_esperados
        mock_get_top_rated.assert_called_once_with(limit=10)

    @pytest.mark.integration
    @pytest.mark.top_rated
    @patch('api.routes.books.get_top_rated_books')
    def test_quando_buscar_top_rated_e_nao_encontrar_deve_retornar_404(self, mock_get_top_rated, client):
        #given
        mock_get_top_rated.return_value = None
        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        #when
        response = client.get('/api/v1/books/top-rated', headers=headers)
        resultado = response.get_json()
        
        #then
        assert response.status_code == 404
        assert resultado['msg'] == 'Nenhum livro encontrado'
        mock_get_top_rated.assert_called_once_with(limit=10)
