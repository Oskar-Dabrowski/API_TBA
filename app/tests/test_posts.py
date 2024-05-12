import pytest
from flask import json


def test_create_post_successful(client):
    """1. Test creating a new post successfully."""
    response = client.post('/posts', json={'title': 'Test Post', 'content': 'Test Content'})
    assert response.status_code == 201
    assert 'Post created' in response.get_json()['message']

def test_create_post_missing_title(client):
    """2. Test response with missing title."""
    response = client.post('/posts', json={'content': 'Test Content'})
    assert response.status_code == 400
    assert 'title is required' in response.get_json()['message']

def test_create_post_missing_content(client):
    """3. Test response with missing content."""
    response = client.post('/posts', json={'title': 'Test Post'})
    assert response.status_code == 400
    assert 'content is required' in response.get_json()['message']

def test_create_post_empty_payload(client):
    """4. Test response for empty payload."""
    response = client.post('/posts', json={})
    assert response.status_code == 400
    assert 'title is required' in response.get_json()['message']

def test_create_post_invalid_title_type(client):
    """5. Test response to a non-string title."""
    response = client.post('/posts', json={'title': 123, 'content': 'Test Content'})
    assert response.status_code == 400
    assert 'title must be a string' in response.get_json()['message']

def test_create_post_invalid_content_type(client):
    """6. Test response to a non-string content."""
    response = client.post('/posts', json={'title': 'Test Post', 'content': 123})
    assert response.status_code == 400
    assert 'content must be a string' in response.get_json()['message']

def test_create_post_with_script_injection(client):
    """7. Test resistance to script injection."""
    response = client.post('/posts', json={'title': 'Test', 'content': "<script>alert('XSS')</script>"})
    assert response.status_code == 201
    assert '<script>' not in response.get_json()['content']

def test_get_all_posts_when_empty(client):
    """8. Test response when no posts exist."""
    response = client.get('/posts')
    assert response.status_code == 200
    assert response.get_json() == []

def test_get_all_posts_with_multiple_posts(client):
    """9. Test response when multiple posts exist."""
    client.post('/posts', json={'title': 'Post One', 'content': 'Content One'})
    client.post('/posts', json={'title': 'Post Two', 'content': 'Content Two'})
    response = client.get('/posts')
    assert response.status_code == 200
    assert len(response.get_json()) == 2

def test_get_single_post_successful(client):
    """10. Test retrieving a single post successfully."""
    post_response = client.post('/posts', json={'title': 'New Post', 'content': 'New Content'})
    post_id = post_response.get_json()['id']
    response = client.get(f'/posts/{post_id}')
    assert response.status_code == 200
    assert response.get_json()['title'] == 'New Post'

def test_get_single_post_nonexistent(client):
    """11. Test response for a non-existent post."""
    response = client.get('/posts/999')
    assert response.status_code == 404

def test_get_post_check_for_xss_protection(client):
    """12. Test for XSS protection in post content."""
    response = client.get('/posts/1')  # Assume this post contains potential XSS content
    assert '<script>' not in response.get_json()['content']

def test_update_post_successful(client):
    """13. Test successful post update."""
    post_response = client.post('/posts', json={'title': 'Old Title', 'content': 'Old content'})
    post_id = post_response.get_json()['id']
    response = client.put(f'/posts/{post_id}', json={'title': 'Updated Title', 'content': 'Updated Content'})
    assert response.status_code == 200
    assert 'Post updated' in response.get_json()['message']

def test_update_nonexistent_post(client):
    """14. Test updating a non-existent post."""
    response = client.put('/posts/999', json={'title': 'New Title', 'content': 'New Content'})
    assert response.status_code == 404

def test_update_post_with_invalid_data(client):
    """15. Test updating a post with invalid data."""
    post_response = client.post('/posts', json={'title': 'Initial Title', 'content': 'Initial Content'})
    post_id = post_response.get_json()['id']
    response = client.put(f'/posts/{post_id}', json={'title': '', 'content': ''})
    assert response.status_code == 400

def test_update_post_to_empty_title(client):
    """16. Test updating a post to have an empty title."""
    post_response = client.post('/posts', json={'title': 'Valid Title', 'content': 'Valid Content'})
    post_id = post_response.get_json()['id']
    response = client.put(f'/posts/{post_id}', json={'title': '', 'content': 'Still Valid Content'})
    assert response.status_code == 400

def test_update_post_to_empty_content(client):
    """17. Test updating a post to have empty content."""
    post_response = client.post('/posts', json={'title': 'Valid Title', 'content': 'Valid Content'})
    post_id = post_response.get_json()['id']
    response = client.put(f'/posts/{post_id}', json={'title': 'Still Valid Title', 'content': ''})
    assert response.status_code == 400

def test_delete_post_successful(client):
    """18. Test successful post deletion."""
    post_response = client.post('/posts', json={'title': 'To be deleted', 'content': 'To be deleted content'})
    post_id = post_response.get_json()['id']
    response = client.delete(f'/posts/{post_id}')
    assert response.status_code == 200
    assert 'Post deleted' in response.get_json()['message']

def test_delete_nonexistent_post(client):
    """19. Test deleting a non-existent post."""
    response = client.delete('/posts/999')
    assert response.status_code == 404

def test_delete_post_twice(client):
    """20. Test deleting the same post twice."""
    post_response = client.post('/posts', json={'title': 'To be deleted twice', 'content': 'To be deleted content twice'})
    post_id = post_response.get_json()['id']
    client.delete(f'/posts/{post_id}')  # First deletion
    response = client.delete(f'/posts/{post_id}')  # Second attempt
    assert response.status_code == 404

def test_end_to_end_post_creation_and_deletion(client):
    """21. Test from creation to deletion of a post."""
    create_response = client.post('/posts', json={'title': 'Temp Post', 'content': 'Temp Content'})
    assert create_response.status_code == 201
    post_id = create_response.get_json()['id']
    delete_response = client.delete(f'/posts/{post_id}')
    assert delete_response.status_code == 200

def test_api_response_time_for_single_post_retrieval(client):
    """22. Test API response time for retrieving a single post."""
    import time
    start_time = time.time()
    response = client.get('/posts/1')
    end_time = time.time()
    assert response.status_code == 200
    assert (end_time - start_time) < 0.5  # Response time should be less than 0.5 seconds

def test_stress_test_for_creating_posts(client):
    """23. Stress test for creating posts."""
    for _ in range(100):  # Create 100 posts
        response = client.post('/posts', json={'title': 'Stress Test Post', 'content': 'Stress Test Content'})
        assert response.status_code == 201

def test_post_creation_with_xss_payload(client):
    """24. Test creating a post with an XSS payload."""
    xss_payload = "<script>alert('XSS');</script>"
    response = client.post('/posts', json={'title': 'XSS Test', 'content': xss_payload})
    assert response.status_code == 201
    assert '<script>' not in response.get_json()['post']['content']
    assert 'alert' not in response.get_json()['post']['content']

def test_api_resistance_to_sql_injection_on_post_update(client):
    """25. Test API's resistance to SQL Injection on post update."""
    sql_injection_payload = "1; DROP TABLE posts;"
    response = client.put('/posts/1', json={'title': sql_injection_payload, 'content': 'Test Content'})
    assert response.status_code == 200
    assert 'DROP TABLE' not in response.get_json()['post']['title']

def test_create_post_with_numerical_title(client):
    """26. Test creating a post with a title that consists only of numbers."""
    response = client.post('/posts', json={'title': '123456', 'content': 'Valid Content'})
    assert response.status_code == 201
    assert response.get_json()['post']['title'] == '123456'

def test_create_post_with_extremely_long_title_and_content(client):
    """27. Test creating a post with an extremely long title and content."""
    long_title = 'T' * 1000
    long_content = 'C' * 10000
    response = client.post('/posts', json={'title': long_title, 'content': long_content})
    assert response.status_code == 201
    assert len(response.get_json()['post']['title']) == 1000
    assert len(response.get_json()['post']['content']) == 10000

def test_create_post_without_authentication(client):
    """28. Test that creating a post is blocked for unauthenticated users."""
    # This assumes your API requires authentication which isn't implemented in the example
    response = client.post('/posts', json={'title': 'Test Post', 'content': 'Test Content'})
    assert response.status_code == 401  # Assumes a 401 Unauthorized status for unauthenticated access

def test_update_post_by_different_user(client):
    """29. Test updating a post by a user who is not the author."""
    response = client.put('/posts/1', json={'title': 'Unauthorized Update', 'content': 'Attempt by different user'})
    assert response.status_code == 403  # Assumes a 403 Forbidden status is returned

def test_delete_post_by_different_user(client):
    """30. Test deleting a post by a user who is not the author."""
    response = client.delete('/posts/1')
    assert response.status_code == 403  # Assumes a 403 Forbidden status is returned

def test_retrieve_all_posts_after_multiple_creations(client):
    """31. Test retrieving all posts after multiple creations."""
    for i in range(5):
        client.post('/posts', json={'title': f'Batch post {i}', 'content': 'Batch content'})
    response = client.get('/posts')
    assert response.status_code == 200
    assert len(response.get_json()['posts']) == 5

def test_update_post_multiple_times_consecutively(client):
    """32. Test multiple consecutive updates to a post."""
    for i in range(5):
        response = client.put('/posts/1', json={'title': f'Updated title {i}', 'content': f'Updated content {i}'})
        assert response.status_code == 200
    response = client.get('/posts/1')
    assert response.get_json()['post']['title'] == 'Updated title 4'

def test_delete_multiple_posts_consecutively(client):
    """33. Test quickly deleting multiple posts one after the other."""
    for i in range(1, 4):
        response = client.delete(f'/posts/{i}')
        assert response.status_code == 200

