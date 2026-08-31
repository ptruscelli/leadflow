from datetime import datetime, timezone

dummy_lead = {
    "name": "Test Name",
    "email": "test@example.com",
    "company": "Test Company",
    "phone": "1234567890",
    "source": "google",
    "message": "Hello there"
}


# soft-delete filtering (GET /leads should exclude deleted leads by default)
def test_soft_delete_filtering(client):
    # create two leads
    created = client.post("/leads", json={
        **dummy_lead
    })
    assert created.status_code == 201
    lead_id = created.json()["id"]

    created_2 = client.post("/leads", json={
        **dummy_lead
    })
    assert created_2.status_code == 201
    lead_2_id = created_2.json()["id"]

    # soft-delete first lead
    response = client.delete(f"/leads/{lead_id}")
    assert response.status_code == 200

    response = client.get("/leads")
    # test deleted lead is not returned
    assert response.status_code == 200
    assert len(response.json()["leads"]) == 1
    assert response.json()["leads"][0]["id"] == lead_2_id

    response = client.get("/leads?deleted=true")
    # test deleted lead is correctly filtered but still accessible
    assert response.status_code == 200
    assert len(response.json()["leads"]) == 1
    assert response.json()["leads"][0]["id"] == lead_id



# PATCH /leads/{id} should not allow editing a deleted lead
def test_edit_deleted_lead(client):
    created = client.post("/leads", json={
        **dummy_lead
    })
    assert created.status_code == 201
    lead_id = created.json()["id"]

    # soft-delete lead
    response = client.delete(f"/leads/{lead_id}")
    assert response.status_code == 200

    # try to edit deleted lead
    response = client.patch(f"/leads/{lead_id}", json={
        "note": "called on thursday"
    })
    # test edit is rejected
    assert response.status_code == 409
    assert response.json()["detail"] == "Cannot edit a deleted lead"



# user clearing a note ( = "") should set note to None
def test_clear_note(client):
    created = client.post("/leads", json={
        **dummy_lead
    })
    assert created.status_code == 201
    lead_id = created.json()["id"]

    response = client.patch(f"/leads/{lead_id}", json={
        "note": "called on thursday"
    })
    assert response.status_code == 200
    assert response.json()["note"] == "called on thursday"

    response = client.patch(f"/leads/{lead_id}", json={
        "note": ""
    })
    assert response.status_code == 200
    assert response.json()["note"] is None

    

# "server is source of truth":
# POST trying to set status/created at, should be rejected
# missing required field should be rejected
# message over 2000 chars should be rejected
def test_server_truth(client):

    response = client.post("/leads", json={
        **dummy_lead,
        "status": "contacted",
    })
    assert response.status_code == 422

    response = client.post("/leads", json={
        **dummy_lead,
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc).isoformat()
    })
    assert response.status_code == 422

    response = client.post("/leads", json={
    **dummy_lead,
    "company": None,
    })
    assert response.status_code == 422
    
    response = client.post("/leads", json={
        **dummy_lead,
        "message": "a" * 2001,
    })
    assert response.status_code == 422





# test search
# create 2 leads with different names
# get /leads?q=notinleads should return no leads
# get /leads?q=leadname should return 1 lead
def test_search(client):
    created = client.post("/leads", json={**dummy_lead})
    assert created.status_code == 201

    created_2 = client.post("/leads", json={
        **dummy_lead,
        "name": "Different Testname"
    })
    assert created_2.status_code == 201

    response = client.get("/leads?q=notinleads")
    assert response.status_code == 200
    assert response.json()["total_items"] == 0 # no leads found by search query
    assert response.json()["leads"] == [] # no leads returned

    response = client.get("/leads?q=different") # upper vs lowercase shouldn't matter
    assert response.status_code == 200
    assert response.json()["total_items"] == 1 # 1 lead found
    assert response.json()["leads"][0]["id"] == created_2.json()["id"] # search matches correct lead




# test status filtering
# create 2 leads, change status on one
# test /leads?status=contacted should return 1 lead
# test /leads should return both 
def test_filter_by_status(client):

    created = client.post("/leads", json={**dummy_lead})
    assert created.status_code == 201
    lead_id = created.json()["id"]
    response = client.patch(f"/leads/{lead_id}", json={
        "status": "contacted"
    })
    assert response.status_code == 200

    created_2 = client.post("/leads", json={**dummy_lead})
    assert created_2.status_code == 201
    
    response = client.get("/leads?status=contacted")
    assert response.status_code == 200
    assert response.json()["total_items"] == 1 
    assert response.json()["leads"][0]["id"] == lead_id

    response = client.get("/leads")
    assert response.status_code == 200
    assert response.json()["total_items"] == 2 # both leads returned



# test pagination 
# create 5 leads
# page3 = /leads?page=3&page_size=2 
# should get:
# page3["page"] == 3
# page3["page_size"] == 2
# page3["total_items"] == 5
# page3["total_pages"] == 3
# len(page3["leads"]) == 1 (leftover)
def test_pagination(client):
    
    for _ in range(5):
        created = client.post("/leads", json={**dummy_lead})
        assert created.status_code == 201

    page3 = client.get("/leads?page=3&page_size=2")
    assert page3.status_code == 200
    assert page3.json()["page"] == 3
    assert page3.json()["page_size"] == 2
    assert page3.json()["total_items"] == 5
    assert page3.json()["total_pages"] == 3
    assert len(page3.json()["leads"]) == 1 # 1 lead leftover on last page (2, 2, 1)