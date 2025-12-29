import pytest
from unittest.mock import patch
from flask_jwt_extended import create_access_token

@pytest.mark.genres
class TestGenres:

    def _get_mock_token(self):
        return create_access_token(identity='test_user')


    # ========== TESTES DO ENDPOINT / Titles ========

    @pytest.mark.genres
    @patch('api.routes.genres.get_all_genres')
    def test_quando_buscar_genres_com_sucesso_deve_retornar_200_com_lista(self, mock_get_genres, client):
        
        #given
        
        genres_esperados = [
            {"genre": "Academic"},
            {"genre": "Add a comment"}
        ]

        mock_get_genres.return_value = genres_esperados
        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}

        #when
        response = client.get('/api/v1/genres', headers=headers)
        resultado = response.get_json()

        #then
        assert response.status_code == 200
        assert isinstance(resultado, list)
        assert resultado == genres_esperados # Validando result com o Mock
        assert all(isinstance(item['genre'], str) for item in resultado)
        mock_get_genres.assert_called_once()

    @pytest.mark.genres
    @patch('api.routes.genres.get_all_genres')
    def test_quando_buscar_genres_e_estiver_vazia(self, mock_get_genres, client):

        #given
        mock_get_genres.return_value = []
        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}

        #when
        response = client.get('/api/v1/genres', headers=headers)
        resultado = response.get_json()

        #then
        assert response.status_code == 200
        assert resultado['msg'] == 'Sem categorias cadastradas'
        mock_get_genres.assert_called_once()
