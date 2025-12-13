import pytest
import json


@pytest.mark.auth
class TestAuth:
    @pytest.mark.register
    def test_quando_registrar_usuario_valido_deve_retornar_201(self, client):
        #given
        payload = {'username': 'teste', 'password': 'teste'}
        esperado = 'Usuário criado com sucesso'
        #when
        response = client.post(
            '/api/v1/auth/register', 
            data=json.dumps(payload),
            content_type='application/json'
        )
        resultado = response.get_json()
        #then
        assert response.status_code == 201
        assert resultado['msg'] == esperado

    @pytest.mark.login
    def test_quando_login_com_sucesso_deve_gerar_access_e_refresh_token(self, client):
        #given
        user_data = {'username': 'teste', 'password': 'teste'}
        client.post('/api/v1/auth/register', data=json.dumps(user_data), content_type='application/json')
        #when 
        response = client.post('/api/v1/auth/login', data=json.dumps(user_data), content_type='application/json')
        resultado = response.get_json()
        #then
        assert response.status_code == 200
        assert 'access_token' in resultado
        assert 'refresh_token' in resultado

    @pytest.mark.token
    def test_quando_refresh_token_invalido_deve_retornar_401(self, client):
        #given
        headers = {'Authorization': 'Bearer token_inventado_errado'}
        #when
        response = client.post('/api/v1/auth/refresh', headers=headers)
        #then
        assert response.status_code == 401