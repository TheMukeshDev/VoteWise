"""Root conftest to mock firebase_admin before any imports."""

import sys
from unittest.mock import MagicMock


class MockFirebaseError(Exception):
    pass


class MockInvalidIdTokenError(MockFirebaseError):
    pass


class MockExpiredIdTokenError(MockFirebaseError):
    pass


class MockUserNotFoundError(MockFirebaseError):
    pass


class MockEmailAlreadyExistsError(MockFirebaseError):
    pass


class MockUidAlreadyExistsError(MockFirebaseError):
    pass


class MockFirebaseErrorClass(MockFirebaseError):
    pass


_mock_auth = MagicMock()
_mock_auth.FirebaseError = MockFirebaseErrorClass
_mock_auth.InvalidIdTokenError = MockInvalidIdTokenError
_mock_auth.ExpiredIdTokenError = MockExpiredIdTokenError
_mock_auth.UserNotFoundError = MockUserNotFoundError
_mock_auth.EmailAlreadyExistsError = MockEmailAlreadyExistsError
_mock_auth.UidAlreadyExistsError = MockUidAlreadyExistsError

_mock_credentials = MagicMock()
_mock_credentials.Certificate = MagicMock()

_mock_firestore = MagicMock()
_mock_storage = MagicMock()

mock_firebase_admin = MagicMock()
mock_firebase_admin._apps = {}
mock_firebase_admin.initialize_app = MagicMock()
mock_firebase_admin.auth = _mock_auth
mock_firebase_admin.credentials = _mock_credentials
mock_firebase_admin.firestore = _mock_firestore
mock_firebase_admin.storage = _mock_storage

sys.modules["firebase_admin"] = mock_firebase_admin
sys.modules["firebase_admin.auth"] = _mock_auth
sys.modules["firebase_admin.credentials"] = _mock_credentials
sys.modules["firebase_admin.firestore"] = _mock_firestore
sys.modules["firebase_admin.storage"] = _mock_storage
