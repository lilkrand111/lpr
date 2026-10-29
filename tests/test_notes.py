import pytest


@pytest.mark.parametrize(
    ("body", "expected_content"),
    [
        ({"title": "Первая", "content": "Текст"}, "Текст"),
        ({"title": "Без текста"}, None),
    ],
    ids=["with_content", "without_content"],
)
def test_create_note(client, auth_a, body, expected_content):
    response = client.post("/notes", json=body, headers=auth_a)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == body["title"]
    assert data["content"] == expected_content
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_get_note_id(client, auth_a, note_a):
    response = client.get(f'/notes/{note_a["id"]}', headers=auth_a)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == note_a["title"]
    assert data["content"] == note_a["content"]
    assert data["id"] == note_a["id"]


def test_edit_note(client, auth_a, note_a):
    response = client.put(
        f"/notes/{note_a['id']}",
        json={"title": "Новый", "content": "Новый текст"},
        headers=auth_a,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Новый"
    assert data["content"] == "Новый текст"
    response = client.get(f"/notes/{note_a['id']}", headers=auth_a)
    data = response.json()
    assert response.status_code == 200
    assert data["title"] == "Новый"
    assert data["content"] == "Новый текст"


def test_delete_note(client, auth_a, note_a):
    response = client.delete(f"/notes/{note_a['id']}", headers=auth_a)
    assert response.status_code == 204
    assert response.text == ""
    response = client.get(f"/notes/{note_a['id']}", headers=auth_a)
    assert response.status_code == 404
    response = client.delete(f"/notes/{note_a['id']}", headers=auth_a)
    assert response.status_code == 404


@pytest.mark.parametrize(("note_id", "error_id"), [(9999, 404), (0, 422), ("abc", 422)])
def test_incorrect_id(client, auth_a, note_id, error_id):
    response = client.get(f"/notes/{note_id}", headers=auth_a)
    assert response.status_code == error_id


def test_own_notes(client, auth_a, auth_b, create_note):
    create_note(headers=auth_a, title="A1")
    create_note(headers=auth_a, title="A2")
    create_note(headers=auth_b, title="B1")
    response = client.get("/notes", headers=auth_a)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {n["title"] for n in data} == {"A1", "A2"}
    response = client.get("/notes", headers=auth_b)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert {n["title"] for n in data} == {"B1"}


def test_foreign_note(client, auth_a, auth_b, create_note):
    note = create_note(headers=auth_a, title='A1', content='A1 content')
    response = client.get(f'/notes/{note['id']}', headers=auth_b)
    assert response.status_code == 404
    assert 'A1' not in response.text
    response = client.get(f'/notes/{note['id']}', headers=auth_a)
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == 'A1'
    assert data['content'] == 'A1 content'


def test_foreign_put_note(client, auth_a, auth_b, create_note):
    title = 'A1'
    body = {
        'title': 'A2',
        'content': 'A2 content'
    }
    note = create_note(headers=auth_a, title=title)
    response = client.put(f'/notes/{note['id']}', json=body, headers=auth_b)
    assert response.status_code == 404
    assert 'A1' not in response.text
    response = client.get(f'/notes/{note['id']}', headers=auth_a)
    assert response.status_code == 200
    assert response.json()['title'] == title


def test_foreign_delete_note(client, auth_a, auth_b, create_note):
    title = 'A1'
    content = 'A1 content'
    note = create_note(headers=auth_a, title=title, content=content)
    response = client.delete(f'/notes/{note['id']}', headers=auth_b)
    assert response.status_code == 404
    response = client.get(f'/notes/{note['id']}', headers=auth_a)
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == title
    assert data['content'] == content