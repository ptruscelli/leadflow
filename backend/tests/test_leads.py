from datetime import datetime, timezone

dummy_lead = {
    "name": "test name",
    "email": "test@example.com",
    "company": "test company",
    "phone": "1234567890",
    "source": "google",
    "message": "hello there"
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



