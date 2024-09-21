from flask.testing import FlaskClient
from sqlalchemy import null
from core.models.assignments import AssignmentStateEnum, GradeEnum
import json


def test_get_assignments(client: FlaskClient, h_principal: dict[str, str]):
    response = client.get(
        '/principal/assignments',
        headers=h_principal
    )

    assert response.status_code == 200

    data = response.json.get['data',[]]
    for assignment in data:
        assert assignment['state'] in [AssignmentStateEnum.SUBMITTED.value, AssignmentStateEnum.GRADED.value]

def setup_draft_assignment(client,h_principal):
    
    assignment_data={
        'grade':None,
        'student_id': 1,
        'teacher_id': None,
        'state': 'DRAFT'
    }
    response= client.post('/principal/assignments', headers=h_principal, 
                          json=assignment_data  # Ensure it's created as a draft
    )
    
    assert response.status_code == 201, (
        f"Failed to create draft assignment. Status code: {response.status_code}"
    )
    return response.json['data']['id']  # Return the ID of the created assignment
def test_grade_assignment_draft_assignment(client: FlaskClient, h_principal: dict[str, str],setup_draft_assignment):
    """ 
    failure case: If an assignment is in Draft state, it cannot be graded by principal
    """
    assignment_id =setup_draft_assignment(client,h_principal)
    response = client.post(
        '/principal/assignments/grade',
        headers=h_principal,
        json={
            'id': assignment_id,
            'grade': GradeEnum.A.value
        },
        
    )

    assert response.status_code == 400,f"Expected status code 400 (Bad Request), got {response.status_code}"
    assert 'cannot be graded' in response.json['error'], (
        "Expected error message indicating draft assignment cannot be graded."
    )

def test_grade_assignment(client: FlaskClient, h_principal: dict[str, str]):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 1,
            'grade': GradeEnum.C.value
        },
        headers=h_principal
    )

    assert response.status_code == 200

    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.C


def test_regrade_assignment(client: FlaskClient, h_principal: dict[str, str]):
    
    response = client.get('/principal/assignments/4', headers=h_principal)
    assert response.status_code == 200
    assert response.json['data']['state'] == AssignmentStateEnum.DRAFT.value
    assert response.json['data']['grade'] is None
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )   

    assert response.status_code == 200

    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.B
    
    response = client.get('/principal/assignments/4', headers=h_principal)
    assert response.status_code == 200
    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.B.value
