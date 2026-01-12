import pytest
from unittest.mock import patch, MagicMock
from flask_jwt_extended import create_access_token


@pytest.mark.ml
class TestML:
    def _get_mock_token(self):
        '''Cria um token mock válido para testes'''
        return create_access_token(identity='1')

    @pytest.mark.integration
    @pytest.mark.training_data
    @patch('api.routes.ml.db.session.execute')
    @patch('api.routes.ml.joblib.dump')
    @patch('api.routes.ml.os.makedirs')
    def test_quando_treinar_modelo_deve_retornar_200_e_nao_sobrescrever_arquivos(self, mock_os, mock_dump, mock_execute, client):
        #given
        mock_book = MagicMock(id=1, title='Livro Favoritado', description='A classic novel')
        mock_execute.return_value.scalars.return_value.all.return_value = [mock_book]
        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}
        #when
        response = client.get('/api/v1/ml/training-data', headers=headers)
        resultado = response.get_json()
        #then
        assert response.status_code == 200
        assert 'Pipeline de treinamento executado com sucesso' in resultado['msg']
        assert mock_dump.call_count == 3
        mock_execute.assert_called_once()

    @pytest.mark.integration
    @pytest.mark.predictions
    @patch('api.routes.ml.joblib.load')
    @patch('api.routes.ml.recommender')
    @patch('api.routes.ml.db.session')
    def test_quando_pedir_predicao_deve_retornar_200_e_salvar_preferencias(self, mock_db, mock_recommender, mock_load, client):
        #given
        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}
        payload = {'title': 'Livro Favoritado'}
        mock_recommender.return_value = ([{'id': 2, 'title': 'Recomendado', 'similarity_score': 0.95}], None)
        mock_load.return_value = MagicMock() 
        mock_book = MagicMock(id=1, title='Livro Favoritado')
        mock_db.execute.return_value.scalars.return_value.all.return_value = [mock_book]
        #when
        response = client.get('/api/v1/ml/predictions', json=payload, headers=headers)
        #then
        assert response.status_code == 200
        assert isinstance(response.get_json(), list)
        assert mock_db.add.called
        assert mock_db.commit.called

    @pytest.mark.integration
    @pytest.mark.user_preferences
    def test_quando_buscar_preferencias_usuario_existente_deve_retornar_200(self, client):
        #given
        token = self._get_mock_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        mock_pref = MagicMock(similarity_score=0.95)
        mock_book = MagicMock(
            id=10, 
            title='Livro Recomendado', 
            price=38.95, 
            rating='Three', 
            image_url='http://link.com/foto.jpg'
        )
        #when
        with patch('api.routes.ml.db.session.query') as mock_query:
            mock_query.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = [(mock_pref, mock_book)]
            response = client.get('/api/v1/ml/user-preferences/1', headers=headers)
        #then
        resultado = response.get_json()
        assert response.status_code == 200
        assert len(resultado) > 0
        assert resultado[0]['title'] == 'Livro Recomendado'
        assert resultado[0]['similarity_score'] == 0.95