from scripts.custom_models import StudentModel
import pytest
from pydantic import ValidationError

def test_valid_student():
    s = StudentModel(name="Alice", email="alice@example.com", course="Math", gpa=3.9)
    assert s.name == "Alice"

def test_invalid_gpa():
    with pytest.raises(ValidationError):
        StudentModel(name="Bob", email="bob@example.com", course="CS", gpa=5.0)
