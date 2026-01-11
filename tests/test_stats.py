import pytest
from unittest.mock import patch
from flask_jwt_extended import create_access_token


@pytest.mark.stats
class TestOverview:
    def _get_mock_token(self):
        """Cria um token mock válido para testes"""
        # Cria um token somente para vlaidar o endpoint
        return create_access_token(identity='test_user')
    

    # ========== TESTES DO ENDOINT /titles ==========
    @pytest.mark.integration
    @pytest.mark.stats_overview
    #Definindo o mock_get_overview
    @patch('api.routes.stats.get_stats_overview')
    def test_quando_buscar_overview_com_sucesso_deve_retornar_200_com_lista(self, mock_get_overview, client):
        #given
        overview_esperado = [
            { "avg_price": 35.07,
             "rating_distribution": [ 
                {"rating": "One", "total": 226},
                {"rating": "Three", "total": 203},
                {"rating": "Two","total": 196}
                ]
            }
        ]
        mock_get_overview.return_value = overview_esperado

        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        #when
        response = client.get('/api/v1/stats/overview', headers=headers)
        resultado = response.get_json()
        
        #then
        assert response.status_code == 200
        assert isinstance(resultado, list)
        assert resultado == overview_esperado
        mock_get_overview.assert_called_once()

    @pytest.mark.integration
    @pytest.mark.stats_overview
    #Definindo o mock_get_overview
    @patch('api.routes.stats.get_stats_overview')
    def test_quando_buscar_overview_e_lista_vir_vazio(self, mock_get_overview, client):
        #given

        mock_get_overview.return_value = []

        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        #when
        response = client.get('/api/v1/stats/overview', headers=headers)
        resultado = response.get_json()
        
        #then
        assert response.status_code == 404
        assert resultado['msg'] == 'Nenhuma estatística disponível'
        mock_get_overview.assert_called_once()

    @pytest.mark.integration
    @pytest.mark.stats_genres
    #Definindo o mock_get_overview
    @patch('api.routes.stats.get_stats_by_genre')
    def test_quando_buscar_genres_com_sucesso_deve_retornar_200_com_lista(self, mock_get_stats_by_genres, client):
        #given
        genres_esperado = [
            {"avg_price": 34, "genre": "Default", "total": 152},
            {"avg_price": 34, "genre": "Nonfiction", "total": 110}
        ]
        mock_get_stats_by_genres.return_value = genres_esperado

        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        #when
        response = client.get('/api/v1/stats/genres', headers=headers)
        resultado = response.get_json()
        
        #then
        assert response.status_code == 200
        assert isinstance(resultado, list)
        assert resultado == genres_esperado
        mock_get_stats_by_genres.assert_called_once()

    @pytest.mark.integration
    @pytest.mark.genres
    #Definindo o mock_get_overviewy
    @patch('api.routes.stats.get_stats_by_genre')
    def test_quando_buscar_genres_e_lista_vir_vazia(self, mock_get_stats_by_genres, client):
        #given
        mock_get_stats_by_genres.return_value = []

        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        #when
        response = client.get('/api/v1/stats/genres', headers=headers)
        resultado = response.get_json()
        
        #then
        assert response.status_code == 404
        assert resultado['msg'] == 'Nenhuma estatística por gênero disponível'

        mock_get_stats_by_genres.assert_called_once()