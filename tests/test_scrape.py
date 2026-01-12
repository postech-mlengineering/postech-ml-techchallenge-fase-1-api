import pytest
from unittest.mock import patch, MagicMock
from flask_jwt_extended import create_access_token


@pytest.mark.scrape
class TestScrape:
    def _get_mock_token(self):
        '''Cria um token mock válido para testes'''
        return create_access_token(identity='test_user')

    @pytest.mark.integration
    @pytest.mark.scrape
    @patch('api.scripts.scrape_utils.requests.get')
    @patch('api.scripts.scrape_utils.pd.DataFrame.to_csv')
    @patch('api.routes.scrape.db.session')
    def test_quando_executar_scrape_com_sucesso_deve_retornar_200_e_total_de_registros(self, mock_session, mock_csv, mock_get, client):
        #given
        html_home = '<ul class="nav nav-list"><li><ul><li><a href="cat.html">Classics</a></li></ul></li></ul>'
        html_list = '<article class="product_pod"><h3><a href="book.html">Livro Teste</a></h3></article>'
        html_detail = '''
            <h1>Livro Teste</h1>
            <div class='item active'><img src='capa.jpg'></div>
            <p class='price_color'>£15.50</p>
            <table class='table-striped'>
                <tr><td>UPC123</td></tr><tr><td>Books</td></tr>
                <tr><td>£15.50</td></tr><tr><td>£15.50</td></tr>
                <tr><td>£0.00</td></tr><tr><td>In stock (20 available)</td></tr>
                <tr><td>0</td></tr>
            </table>
        '''
        mock_get.side_effect = [
            MagicMock(status_code=200, text=html_home),
            MagicMock(status_code=200, text=html_list),
            MagicMock(status_code=200, text=html_detail)
        ]
        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}
        #when
        response = client.post('/api/v1/scrape/', headers=headers)
        resultado = response.get_json()
        #then
        assert response.status_code == 200
        assert resultado['msg'] == 'Web scraping realizado com sucesso'
        assert resultado['total_records'] == 1
        #verifica se as operações de banco foram chamadas
        assert mock_session.execute.called
        assert mock_session.bulk_insert_mappings.called
        assert mock_session.commit.called