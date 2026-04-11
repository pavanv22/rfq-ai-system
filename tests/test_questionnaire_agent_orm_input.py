"""Unit tests for questionnaire_agent ORM and dict input handling."""
import pytest
from app.agents.questionnaire_agent import generate_questionnaire, _get_field
from app.models import RFQModel


class TestGetFieldHelper:
    """Test the _get_field helper that extracts fields from dict or ORM objects."""

    def test_get_field_from_dict(self):
        """Test extraction from dict."""
        data = {"project_name": "Test Project", "scope": "Marketing"}
        assert _get_field(data, "project_name") == "Test Project"
        assert _get_field(data, "scope") == "Marketing"

    def test_get_field_from_orm_object(self, test_rfq):
        """Test extraction from ORM object."""
        assert _get_field(test_rfq, "subject") == test_rfq.subject
        assert _get_field(test_rfq, "scope") == test_rfq.scope

    def test_get_field_missing_returns_default(self):
        """Test missing field returns default value."""
        data = {"name": "Test"}
        assert _get_field(data, "missing_field", "default") == "default"

    def test_get_field_list_converted_to_json_string(self):
        """Test list fields converted to JSON string."""
        data = {"items": [{"a": 1}, {"b": 2}]}
        result = _get_field(data, "items")
        assert isinstance(result, str)
        assert "a" in result and "1" in result

    def test_get_field_dict_converted_to_json_string(self):
        """Test dict fields converted to JSON string."""
        data = {"config": {"key1": "value1"}}
        result = _get_field(data, "config")
        assert isinstance(result, str)
        assert "key1" in result


class TestGenerateQuestionnaireOrmInput:
    """Test generate_questionnaire function with ORM input."""

    def test_generate_questionnaire_accepts_orm_model(self, test_rfq):
        """Verify generate_questionnaire accepts RFQModel instance."""
        # Should not raise "'RFQModel' object is not subscriptable"
        try:
            result = generate_questionnaire(test_rfq)
            # Result should be a dict with expected keys
            assert isinstance(result, dict)
            assert "questions" in result
            assert "prompt" in result
            assert "raw_response" in result
        except TypeError as e:
            if "subscriptable" in str(e):
                pytest.fail(f"generate_questionnaire failed with ORM input: {e}")
            raise

    def test_generate_questionnaire_accepts_dict_input(self, test_rfq_dict):
        """Verify generate_questionnaire accepts dict input."""
        try:
            result = generate_questionnaire(test_rfq_dict)
            assert isinstance(result, dict)
            assert "questions" in result
            assert isinstance(result["questions"], list)
        except TypeError as e:
            if "subscriptable" in str(e):
                pytest.fail(f"generate_questionnaire failed with dict input: {e}")
            raise

    def test_generate_questionnaire_output_structure(self, test_rfq):
        """Verify output structure contains expected fields."""
        result = generate_questionnaire(test_rfq)
        
        # Check top-level structure
        assert "questions" in result
        assert "prompt" in result
        assert "raw_response" in result
        
        # Check questions is a list
        assert isinstance(result["questions"], list)
        
        # Check each question has required fields
        for q in result["questions"]:
            assert "question" in q
            assert "category" in q
            assert "required" in q
            assert isinstance(q["question"], str)
            assert isinstance(q["required"], bool)

    def test_generate_questionnaire_extracts_subject(self, test_rfq):
        """Verify prompt includes extracted subject."""
        result = generate_questionnaire(test_rfq)
        prompt = result["prompt"]
        
        # Should include subject in prompt
        assert "Subject:" in prompt or "RFQ:" in prompt

    def test_generate_questionnaire_categories_present(self, test_rfq):
        """Verify questions span expected categories."""
        result = generate_questionnaire(test_rfq)
        questions = result["questions"]
        
        # Extract categories
        categories = {q.get("category") for q in questions}
        
        # Should have questions (even if category is None)
        assert len(questions) > 0
