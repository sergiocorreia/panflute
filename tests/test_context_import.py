import os
from panflute.utils import ContextImport


def test_all():
    test_context_import()


def test_context_import():
    test_file = os.path.join(os.getcwd(), 'tests/dependency/dependency.py')
    print("Importing from the file: \n\t", end="")
    print(test_file)
    with ContextImport(test_file) as module:
        test_function_res = module.test_function()
        test_class = module.test_class()
        test_class_method_test = test_class.test_me()
    assert test_function_res == True, "Unexpected result from test function execution"
    assert test_class_method_test == "I'm a test", "Unexpected result from test function execution"


if __name__ == "__main__":
    test_all()
