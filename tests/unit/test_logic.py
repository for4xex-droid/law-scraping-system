from src.core.logic import BusinessLogic
from src.core.result import Err, Ok


def test_process_success() -> None:
    result = BusinessLogic.process("test")
    assert isinstance(result, Ok)
    assert result.value.message == "Processed: test"


def test_process_failure() -> None:
    result = BusinessLogic.process("")
    assert isinstance(result, Err)
    assert result.error == "Input cannot be empty"
