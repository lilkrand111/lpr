import pytest

@pytest.mark.parametrize(
    ("body", "expected_content"),
    [
        ({'title': 'Первая', 'content': 'Текст'}, 'Текст'),
        ({'title': 'Без текста'}, None)
    ],
    ids=['with_content', 'without_content']
)
def test_create_note(client, auth_a, body, expected_content):
    response = client.post('/notes', json=body, headers=auth_a)
    assert response.status_code == 201
    data = response.json()
    assert data['title'] == body['title']
    assert data['content'] == expected_content
    assert 'id' in data
    assert 'created_at' in data
    assert 'updated_at' in data