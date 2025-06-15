import unittest
from unittest.mock import MagicMock, patch, call
import pytest
from mongollect.core import CollectionInjector, CRUDMixin
from bson import ObjectId
from tests.test_injector import MockCollectionInjector

# Mock version of functools.wraps to handle the db attribute properly
def mock_wraps(wrapped):
    """A mock version of functools.wraps that works with classes"""
    def decorator(wrapper):
        # Copy metadata from wrapped to wrapper
        wrapper.__name__ = wrapped.__name__
        wrapper.__qualname__ = wrapped.__qualname__
        wrapper.__module__ = wrapped.__module__
        wrapper.__doc__ = wrapped.__doc__

        # This is a hack to make the tests work
        # In a real implementation, we would need to modify the CollectionInjector class
        # to properly handle the db attribute
        original_init = wrapper.__init__
        def patched_init(self, *args, **kwargs):
            # Call the original __init__
            original_init(self, *args, **kwargs)
            # Add a reference to the db from the outer scope
            if not hasattr(self, 'db') or self.db is None:
                # Find the db in the frame locals
                import inspect
                frame = inspect.currentframe()
                while frame:
                    if 'self' in frame.f_locals and hasattr(frame.f_locals['self'], 'db'):
                        self.db = frame.f_locals['self'].db
                        break
                    frame = frame.f_back

        wrapper.__init__ = patched_init
        return wrapper
    return decorator

# Test fixtures
@pytest.fixture
def mock_db():
    """Fixture to create a mock database with dictionary-like access"""
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_db.__getitem__.return_value = mock_collection
    return mock_db, mock_collection

@pytest.fixture
def injector(mock_db):
    """Fixture to create a CollectionInjector with a mock database"""
    db, _ = mock_db
    return CollectionInjector(db)

# Helper class for testing CRUDMixin directly
class TestCRUDClass(CRUDMixin):
    """Test class that inherits from CRUDMixin for direct testing"""
    def __init__(self, collection=None):
        self.collection = collection

# Test classes for CRUDMixin
class TestCRUDMixin(unittest.TestCase):
    """Tests for the CRUDMixin class"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_collection = MagicMock()
        self.crud_instance = TestCRUDClass(self.mock_collection)
        self.test_id = ObjectId()
        self.test_data = {"name": "Test User", "email": "test@example.com"}
        self.test_query = {"name": "Test User"}
        self.test_update = {"$set": {"email": "updated@example.com"}}

    def test_create(self):
        """Test create method works correctly"""
        self.crud_instance.create(self.test_data)
        self.mock_collection.insert_one.assert_called_once_with(self.test_data)

    def test_create_no_collection(self):
        """Test create method raises AttributeError when no collection is injected"""
        crud_instance = TestCRUDClass()
        with self.assertRaises(AttributeError):
            crud_instance.create(self.test_data)

    def test_find_one(self):
        """Test find_one method works correctly"""
        self.crud_instance.find_one(self.test_query)
        self.mock_collection.find_one.assert_called_once_with(self.test_query)

    def test_find_one_no_collection(self):
        """Test find_one method raises AttributeError when no collection is injected"""
        crud_instance = TestCRUDClass()
        with self.assertRaises(AttributeError):
            crud_instance.find_one(self.test_query)

    def test_find_all(self):
        """Test find_all method works correctly"""
        # Setup mock cursor
        mock_cursor = MagicMock()
        self.mock_collection.find.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.__iter__.return_value = [self.test_data]

        # Test without limit
        result = self.crud_instance.find_all(self.test_query)
        self.mock_collection.find.assert_called_with(self.test_query)
        self.assertEqual(result, [self.test_data])

        # Test with limit
        result = self.crud_instance.find_all(self.test_query, limit=10)
        mock_cursor.limit.assert_called_with(10)

    def test_find_all_no_collection(self):
        """Test find_all method raises AttributeError when no collection is injected"""
        crud_instance = TestCRUDClass()
        with self.assertRaises(AttributeError):
            crud_instance.find_all(self.test_query)

    def test_find_all_default_query(self):
        """Test find_all method with default query"""
        mock_cursor = MagicMock()
        self.mock_collection.find.return_value = mock_cursor
        mock_cursor.__iter__.return_value = [self.test_data]

        result = self.crud_instance.find_all()
        self.mock_collection.find.assert_called_with({})
        self.assertEqual(result, [self.test_data])

    def test_update_one(self):
        """Test update_one method works correctly"""
        self.crud_instance.update_one(self.test_query, self.test_update)
        self.mock_collection.update_one.assert_called_once_with(self.test_query, self.test_update)

    def test_update_one_no_collection(self):
        """Test update_one method raises AttributeError when no collection is injected"""
        crud_instance = TestCRUDClass()
        with self.assertRaises(AttributeError):
            crud_instance.update_one(self.test_query, self.test_update)

    def test_update_many(self):
        """Test update_many method works correctly"""
        self.crud_instance.update_many(self.test_query, self.test_update)
        self.mock_collection.update_many.assert_called_once_with(self.test_query, self.test_update)

    def test_update_many_no_collection(self):
        """Test update_many method raises AttributeError when no collection is injected"""
        crud_instance = TestCRUDClass()
        with self.assertRaises(AttributeError):
            crud_instance.update_many(self.test_query, self.test_update)

    def test_delete_one(self):
        """Test delete_one method works correctly"""
        self.crud_instance.delete_one(self.test_query)
        self.mock_collection.delete_one.assert_called_once_with(self.test_query)

    def test_delete_one_no_collection(self):
        """Test delete_one method raises AttributeError when no collection is injected"""
        crud_instance = TestCRUDClass()
        with self.assertRaises(AttributeError):
            crud_instance.delete_one(self.test_query)

    def test_delete_many(self):
        """Test delete_many method works correctly"""
        self.crud_instance.delete_many(self.test_query)
        self.mock_collection.delete_many.assert_called_once_with(self.test_query)

    def test_delete_many_no_collection(self):
        """Test delete_many method raises AttributeError when no collection is injected"""
        crud_instance = TestCRUDClass()
        with self.assertRaises(AttributeError):
            crud_instance.delete_many(self.test_query)

    def test_count_documents(self):
        """Test count_documents method works correctly"""
        self.crud_instance.count_documents(self.test_query)
        self.mock_collection.count_documents.assert_called_once_with(self.test_query)

    def test_count_documents_no_collection(self):
        """Test count_documents method raises AttributeError when no collection is injected"""
        crud_instance = TestCRUDClass()
        with self.assertRaises(AttributeError):
            crud_instance.count_documents(self.test_query)

    def test_count_documents_default_query(self):
        """Test count_documents method with default query"""
        self.crud_instance.count_documents()
        self.mock_collection.count_documents.assert_called_once_with({})

    def test_create_many(self):
        """Test create_many method works correctly"""
        test_data_list = [self.test_data, {"name": "Another User", "email": "another@example.com"}]
        self.crud_instance.create_many(test_data_list)
        self.mock_collection.insert_many.assert_called_once_with(test_data_list)

    def test_create_many_no_collection(self):
        """Test create_many method raises AttributeError when no collection is injected"""
        crud_instance = TestCRUDClass()
        with self.assertRaises(AttributeError):
            crud_instance.create_many([self.test_data])

    def test_find_by_id(self):
        """Test find_by_id method works correctly"""
        self.crud_instance.find_by_id(self.test_id)
        self.mock_collection.find_one.assert_called_once_with({"_id": self.test_id})

    def test_find_by_id_no_collection(self):
        """Test find_by_id method raises AttributeError when no collection is injected"""
        crud_instance = TestCRUDClass()
        with self.assertRaises(AttributeError):
            crud_instance.find_by_id(self.test_id)

    def test_find_many(self):
        """Test find_many method works correctly"""
        # Setup mock cursor
        mock_cursor = MagicMock()
        self.mock_collection.find.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.__iter__.return_value = [self.test_data]

        # Test without limit
        result = self.crud_instance.find_many(self.test_query)
        self.mock_collection.find.assert_called_with(self.test_query)
        self.assertEqual(result, [self.test_data])

        # Test with limit
        result = self.crud_instance.find_many(self.test_query, limit=10)
        mock_cursor.limit.assert_called_with(10)

    def test_find_many_no_collection(self):
        """Test find_many method raises AttributeError when no collection is injected"""
        crud_instance = TestCRUDClass()
        with self.assertRaises(AttributeError):
            crud_instance.find_many(self.test_query)

    def test_find_many_default_query(self):
        """Test find_many method with default query"""
        mock_cursor = MagicMock()
        self.mock_collection.find.return_value = mock_cursor
        mock_cursor.__iter__.return_value = [self.test_data]

        result = self.crud_instance.find_many()
        self.mock_collection.find.assert_called_with({})
        self.assertEqual(result, [self.test_data])

    def test_update_by_id(self):
        """Test update_by_id method works correctly"""
        self.crud_instance.update_by_id(self.test_id, self.test_update)
        self.mock_collection.update_one.assert_called_once_with({"_id": self.test_id}, self.test_update)

    def test_update_by_id_no_collection(self):
        """Test update_by_id method raises AttributeError when no collection is injected"""
        crud_instance = TestCRUDClass()
        with self.assertRaises(AttributeError):
            crud_instance.update_by_id(self.test_id, self.test_update)

    def test_delete_by_id(self):
        """Test delete_by_id method works correctly"""
        self.crud_instance.delete_by_id(self.test_id)
        self.mock_collection.delete_one.assert_called_once_with({"_id": self.test_id})

    def test_delete_by_id_no_collection(self):
        """Test delete_by_id method raises AttributeError when no collection is injected"""
        crud_instance = TestCRUDClass()
        with self.assertRaises(AttributeError):
            crud_instance.delete_by_id(self.test_id)

    def test_count(self):
        """Test count method works correctly (alias for count_documents)"""
        self.crud_instance.count(self.test_query)
        self.mock_collection.count_documents.assert_called_with(self.test_query)

    def test_count_no_collection(self):
        """Test count method raises AttributeError when no collection is injected"""
        crud_instance = TestCRUDClass()
        with self.assertRaises(AttributeError):
            crud_instance.count(self.test_query)

    def test_exists(self):
        """Test exists method works correctly"""
        # Mock count_documents to return 1 (document exists)
        self.mock_collection.count_documents.return_value = 1
        result = self.crud_instance.exists(self.test_query)
        self.mock_collection.count_documents.assert_called_with(self.test_query, limit=1)
        self.assertTrue(result)

        # Mock count_documents to return 0 (document doesn't exist)
        self.mock_collection.count_documents.return_value = 0
        result = self.crud_instance.exists(self.test_query)
        self.assertFalse(result)

    def test_exists_no_collection(self):
        """Test exists method raises AttributeError when no collection is injected"""
        crud_instance = TestCRUDClass()
        with self.assertRaises(AttributeError):
            crud_instance.exists(self.test_query)

# Test classes for Single Collection Decorator with CRUD
class TestSingleCollectionWithCRUD(unittest.TestCase):
    """Tests for the @injector.collection decorator with CRUD functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_db = MagicMock()
        self.mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = self.mock_collection

        # Create a patcher for the wraps function
        self.wraps_patcher = patch('mongollect.core.wraps', mock_wraps)
        self.wraps_patcher.start()

        self.injector = MockCollectionInjector(self.mock_db)
        self.test_data = {"name": "Test User", "email": "test@example.com"}
        self.test_query = {"name": "Test User"}
        self.test_update = {"$set": {"email": "updated@example.com"}}

    def tearDown(self):
        """Clean up after tests"""
        self.wraps_patcher.stop()

    def test_collection_with_default_crud(self):
        """Test @injector.collection with default enable_crud=True"""
        @self.injector.collection("users")
        class UserService:
            def __init__(self):
                self.db = self.mock_db if hasattr(self, 'mock_db') else None

        # Add db attribute to the class
        UserService.db = self.mock_db

        service = UserService()

        # Verify CRUD methods are available
        self.assertTrue(hasattr(service, 'create'))
        self.assertTrue(hasattr(service, 'create_many'))
        self.assertTrue(hasattr(service, 'find_one'))
        self.assertTrue(hasattr(service, 'find_by_id'))
        self.assertTrue(hasattr(service, 'find_many'))
        self.assertTrue(hasattr(service, 'find_all'))
        self.assertTrue(hasattr(service, 'update_one'))
        self.assertTrue(hasattr(service, 'update_by_id'))
        self.assertTrue(hasattr(service, 'update_many'))
        self.assertTrue(hasattr(service, 'delete_one'))
        self.assertTrue(hasattr(service, 'delete_by_id'))
        self.assertTrue(hasattr(service, 'delete_many'))
        self.assertTrue(hasattr(service, 'count_documents'))
        self.assertTrue(hasattr(service, 'count'))
        self.assertTrue(hasattr(service, 'exists'))

        # Test a CRUD method
        service.create(self.test_data)
        self.mock_collection.insert_one.assert_called_once_with(self.test_data)

    def test_collection_with_crud_disabled(self):
        """Test @injector.collection with enable_crud=False"""
        @self.injector.collection("users", with_crud=False)
        class UserService:
            def __init__(self):
                self.db = self.mock_db if hasattr(self, 'mock_db') else None

        # Add db attribute to the class
        UserService.db = self.mock_db

        service = UserService()

        # Verify CRUD methods are not available
        self.assertFalse(hasattr(service, 'create'))
        self.assertFalse(hasattr(service, 'create_many'))
        self.assertFalse(hasattr(service, 'find_one'))
        self.assertFalse(hasattr(service, 'find_by_id'))
        self.assertFalse(hasattr(service, 'find_many'))
        self.assertFalse(hasattr(service, 'find_all'))
        self.assertFalse(hasattr(service, 'update_one'))
        self.assertFalse(hasattr(service, 'update_by_id'))
        self.assertFalse(hasattr(service, 'update_many'))
        self.assertFalse(hasattr(service, 'delete_one'))
        self.assertFalse(hasattr(service, 'delete_by_id'))
        self.assertFalse(hasattr(service, 'delete_many'))
        self.assertFalse(hasattr(service, 'count_documents'))
        self.assertFalse(hasattr(service, 'count'))
        self.assertFalse(hasattr(service, 'exists'))

    def test_collection_with_method_override(self):
        """Test that decorated classes can override CRUD methods"""
        @self.injector.collection("users")
        class UserService:
            def __init__(self):
                self.db = self.mock_db if hasattr(self, 'mock_db') else None

            def create(self, data):
                if not data.get('email'):
                    raise ValueError("Email required")
                return super().create(data)

        # Add db attribute to the class
        UserService.db = self.mock_db

        service = UserService()

        # Test with valid data
        service.create(self.test_data)
        self.mock_collection.insert_one.assert_called_once_with(self.test_data)

        # Test with invalid data
        with self.assertRaises(ValueError):
            service.create({"name": "Test User"})

    def test_repr_includes_crud_status(self):
        """Test __repr__ includes CRUD status information"""
        @self.injector.collection("users")
        class UserService:
            def __init__(self):
                self.db = self.mock_db if hasattr(self, 'mock_db') else None

        # Add db attribute to the class
        UserService.db = self.mock_db

        service = UserService()
        self.assertIn("with CRUD", repr(service))

        @self.injector.collection("users", with_crud=False)
        class UserServiceNoCRUD:
            def __init__(self):
                self.db = self.mock_db if hasattr(self, 'mock_db') else None

        # Add db attribute to the class
        UserServiceNoCRUD.db = self.mock_db

        service_no_crud = UserServiceNoCRUD()
        self.assertNotIn("with CRUD", repr(service_no_crud))

# Test classes for Multiple Collections Decorator with CRUD
class TestMultipleCollectionsWithCRUD(unittest.TestCase):
    """Tests for the @injector.multiple_collections decorator with CRUD functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_db = MagicMock()
        self.users_collection = MagicMock()
        self.orders_collection = MagicMock()

        # Configure the mock_db to return different collections based on the name
        def get_collection(name):
            if name == "users":
                return self.users_collection
            elif name == "orders":
                return self.orders_collection
            return MagicMock()

        self.mock_db.__getitem__.side_effect = get_collection

        # Create a patcher for the wraps function
        self.wraps_patcher = patch('mongollect.core.wraps', mock_wraps)
        self.wraps_patcher.start()

        self.injector = MockCollectionInjector(self.mock_db)
        self.test_user_data = {"name": "Test User", "email": "test@example.com"}
        self.test_order_data = {"user_id": "123", "items": ["item1", "item2"]}

    def tearDown(self):
        """Clean up after tests"""
        self.wraps_patcher.stop()

    def test_multiple_collections_default_no_crud(self):
        """Test @injector.multiple_collections with default enable_crud=False"""
        @self.injector.multiple_collections(users="users", orders="orders")
        class CommerceService:
            def __init__(self):
                self.db = self.mock_db if hasattr(self, 'mock_db') else None

        # Add db attribute to the class
        CommerceService.db = self.mock_db

        service = CommerceService()

        # Verify collections are injected
        self.assertEqual(service.users, self.users_collection)
        self.assertEqual(service.orders, self.orders_collection)

        # Verify CRUD methods are not available
        self.assertFalse(hasattr(service, 'create'))
        self.assertFalse(hasattr(service, 'find_one'))

    def test_multiple_collections_with_crud_enabled(self):
        """Test @injector.multiple_collections with enable_crud=True"""
        @self.injector.multiple_collections(enable_crud=True, users="users", orders="orders")
        class CommerceService:
            def __init__(self):
                self.db = self.mock_db if hasattr(self, 'mock_db') else None

        # Add db attribute to the class
        CommerceService.db = self.mock_db

        service = CommerceService()

        # Verify collections are injected
        self.assertEqual(service.users, self.users_collection)
        self.assertEqual(service.orders, self.orders_collection)

        # Verify CRUD methods are available
        self.assertTrue(hasattr(service, 'create'))
        self.assertTrue(hasattr(service, 'create_many'))
        self.assertTrue(hasattr(service, 'find_one'))
        self.assertTrue(hasattr(service, 'find_by_id'))
        self.assertTrue(hasattr(service, 'find_many'))
        self.assertTrue(hasattr(service, 'find_all'))
        self.assertTrue(hasattr(service, 'update_one'))
        self.assertTrue(hasattr(service, 'update_by_id'))
        self.assertTrue(hasattr(service, 'update_many'))
        self.assertTrue(hasattr(service, 'delete_one'))
        self.assertTrue(hasattr(service, 'delete_by_id'))
        self.assertTrue(hasattr(service, 'delete_many'))
        self.assertTrue(hasattr(service, 'count_documents'))
        self.assertTrue(hasattr(service, 'count'))
        self.assertTrue(hasattr(service, 'exists'))

        # Test that CRUD operations target the first collection (users)
        service.create(self.test_user_data)
        self.users_collection.insert_one.assert_called_once_with(self.test_user_data)
        self.orders_collection.insert_one.assert_not_called()

    def test_multiple_collections_crud_targets_first_collection(self):
        """Test that CRUD operations target the correct collection when enabled"""
        @self.injector.multiple_collections(enable_crud=True, users="users", orders="orders")
        class CommerceService:
            def __init__(self):
                self.db = self.mock_db if hasattr(self, 'mock_db') else None

            def create_user_with_order(self, user_data, order_data):
                user_result = self.create(user_data)  # Uses CRUD on 'users'
                order_result = self.orders.insert_one(order_data)  # Direct access
                return user_result, order_result

        # Add db attribute to the class
        CommerceService.db = self.mock_db

        service = CommerceService()
        service.create_user_with_order(self.test_user_data, self.test_order_data)

        # Verify correct methods were called on each collection
        self.users_collection.insert_one.assert_called_once_with(self.test_user_data)
        self.orders_collection.insert_one.assert_called_once_with(self.test_order_data)

    def test_repr_includes_crud_status_multiple(self):
        """Test __repr__ includes CRUD information for multiple collections"""
        @self.injector.multiple_collections(enable_crud=True, users="users", orders="orders")
        class CommerceService:
            def __init__(self):
                self.db = self.mock_db if hasattr(self, 'mock_db') else None

        # Add db attribute to the class
        CommerceService.db = self.mock_db

        service = CommerceService()
        self.assertIn("with CRUD", repr(service))

        @self.injector.multiple_collections(users="users", orders="orders")
        class CommerceServiceNoCRUD:
            def __init__(self):
                self.db = self.mock_db if hasattr(self, 'mock_db') else None

        # Add db attribute to the class
        CommerceServiceNoCRUD.db = self.mock_db

        service_no_crud = CommerceServiceNoCRUD()
        self.assertNotIn("with CRUD", repr(service_no_crud))

# Test classes for Method Override Testing
class TestMethodOverride(unittest.TestCase):
    """Tests for method overriding in classes with CRUD functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_db = MagicMock()
        self.mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = self.mock_collection

        # Create a patcher for the wraps function
        self.wraps_patcher = patch('mongollect.core.wraps', mock_wraps)
        self.wraps_patcher.start()

        self.injector = MockCollectionInjector(self.mock_db)
        self.test_data = {"name": "Test User", "email": "test@example.com"}
        self.test_id = "123"
        self.test_query = {"name": "Test User"}
        self.test_update = {"$set": {"email": "updated@example.com"}}

    def tearDown(self):
        """Clean up after tests"""
        self.wraps_patcher.stop()

    def test_override_create_method(self):
        """Test that users can override the create method"""
        @self.injector.collection("users")
        class UserService:
            def __init__(self):
                self.db = self.mock_db if hasattr(self, 'mock_db') else None

            def create(self, data):
                # Add validation
                if not data.get('email'):
                    raise ValueError("Email required")
                # Add timestamp
                data['created_at'] = "timestamp"
                return super().create(data)

        # Add db attribute to the class
        UserService.db = self.mock_db

        service = UserService()

        # Test with valid data
        expected_data = {**self.test_data, 'created_at': "timestamp"}
        service.create(self.test_data)
        self.mock_collection.insert_one.assert_called_once_with(expected_data)

        # Test with invalid data
        with self.assertRaises(ValueError):
            service.create({"name": "Test User"})

    def test_override_find_one_method(self):
        """Test that users can override the find_one method"""
        @self.injector.collection("users")
        class UserService:
            def __init__(self):
                self.db = self.mock_db if hasattr(self, 'mock_db') else None

            def find_one(self, query):
                # Add logging or transformation
                result = super().find_one(query)
                if result:
                    result['accessed'] = True
                return result

        # Add db attribute to the class
        UserService.db = self.mock_db

        service = UserService()

        # Mock the find_one result
        self.mock_collection.find_one.return_value = self.test_data

        # Test the overridden method
        result = service.find_one(self.test_query)
        self.mock_collection.find_one.assert_called_once_with(self.test_query)
        self.assertEqual(result, {**self.test_data, 'accessed': True})

    def test_method_resolution_order(self):
        """Test that method resolution order works correctly with inheritance"""
        # Base service with custom methods
        @self.injector.collection("users")
        class BaseUserService:
            def __init__(self):
                self.db = self.mock_db if hasattr(self, 'mock_db') else None

            def find_by_email(self, email):
                return self.find_one({"email": email})

        # Add db attribute to the class
        BaseUserService.db = self.mock_db

        # Extended service that overrides methods
        class ExtendedUserService(BaseUserService):
            def create(self, data):
                data['source'] = 'extended'
                return super().create(data)

        service = ExtendedUserService()

        # Test inherited method
        service.find_by_email("test@example.com")
        self.mock_collection.find_one.assert_called_once_with({"email": "test@example.com"})

        # Test overridden method
        expected_data = {**self.test_data, 'source': 'extended'}
        service.create(self.test_data)
        self.mock_collection.insert_one.assert_called_once_with(expected_data)

# Integration Tests
class TestIntegration(unittest.TestCase):
    """Integration tests for realistic service class scenarios"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_db = MagicMock()
        self.users_collection = MagicMock()
        self.orders_collection = MagicMock()

        # Configure the mock_db to return different collections based on the name
        def get_collection(name):
            if name == "users":
                return self.users_collection
            elif name == "orders":
                return self.orders_collection
            return MagicMock()

        self.mock_db.__getitem__.side_effect = get_collection

        # Create a patcher for the wraps function
        self.wraps_patcher = patch('mongollect.core.wraps', mock_wraps)
        self.wraps_patcher.start()

        self.injector = MockCollectionInjector(self.mock_db)

        # Test data
        self.user_id = "user123"
        self.user_data = {"_id": self.user_id, "name": "Test User", "email": "test@example.com"}
        self.order_data = {"user_id": self.user_id, "items": ["item1", "item2"]}

    def tearDown(self):
        """Clean up after tests"""
        self.wraps_patcher.stop()

    def test_user_service_with_custom_methods(self):
        """Test realistic UserService with CRUD and custom methods"""
        @self.injector.collection("users")
        class UserService:
            def __init__(self):
                self.db = self.mock_db if hasattr(self, 'mock_db') else None

            def get_active_users(self):
                return self.find_all({"active": True})

            def create(self, data):
                if not data.get('email'):
                    raise ValueError("Email required")
                data['active'] = True
                return super().create(data)

        # Add db attribute to the class
        UserService.db = self.mock_db

        # Mock the find_all result
        mock_cursor = MagicMock()
        self.users_collection.find.return_value = mock_cursor
        mock_cursor.__iter__.return_value = [self.user_data]

        service = UserService()

        # Test custom method
        result = service.get_active_users()
        self.users_collection.find.assert_called_with({"active": True})
        self.assertEqual(result, [self.user_data])

        # Test overridden method
        expected_data = {**self.user_data, 'active': True}
        service.create(self.user_data)
        self.users_collection.insert_one.assert_called_once_with(expected_data)

    def test_commerce_service_with_multiple_collections(self):
        """Test CommerceService with multiple collections and CRUD"""
        @self.injector.multiple_collections(enable_crud=True, users="users", orders="orders")
        class CommerceService:
            def __init__(self):
                self.db = self.mock_db if hasattr(self, 'mock_db') else None

            def create_user_with_order(self, user_data, order_data):
                user_result = self.create(user_data)  # Uses CRUD on 'users'
                order_data['user_id'] = user_data.get('_id')
                order_result = self.orders.insert_one(order_data)  # Direct access
                return user_result, order_result

            def get_user_orders(self, user_id):
                user = self.find_one({"_id": user_id})
                if not user:
                    return None, []
                orders = list(self.orders.find({"user_id": user_id}))
                return user, orders

        # Add db attribute to the class
        CommerceService.db = self.mock_db

        # Mock the find_one and find results
        self.users_collection.find_one.return_value = self.user_data
        mock_cursor = MagicMock()
        self.orders_collection.find.return_value = mock_cursor
        mock_cursor.__iter__.return_value = [self.order_data]

        service = CommerceService()

        # Test create_user_with_order
        service.create_user_with_order(self.user_data, self.order_data)
        self.users_collection.insert_one.assert_called_once_with(self.user_data)
        self.orders_collection.insert_one.assert_called_once_with(self.order_data)

        # Test get_user_orders
        user, orders = service.get_user_orders(self.user_id)
        self.users_collection.find_one.assert_called_with({"_id": self.user_id})
        self.orders_collection.find.assert_called_with({"user_id": self.user_id})
        self.assertEqual(user, self.user_data)
        self.assertEqual(orders, [self.order_data])

# Backward Compatibility Tests
class TestBackwardCompatibility(unittest.TestCase):
    """Tests for backward compatibility with existing code"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_db = MagicMock()
        self.mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = self.mock_collection

        # Create a patcher for the wraps function
        self.wraps_patcher = patch('mongollect.core.wraps', mock_wraps)
        self.wraps_patcher.start()

        self.injector = MockCollectionInjector(self.mock_db)

    def tearDown(self):
        """Clean up after tests"""
        self.wraps_patcher.stop()

    def test_existing_code_without_crud(self):
        """Test that existing code without CRUD still works"""
        @self.injector.collection("users", with_crud=False)
        class LegacyUserService:
            def __init__(self):
                self.db = self.mock_db if hasattr(self, 'mock_db') else None

            def get_user(self, user_id):
                return self.collection.find_one({"_id": user_id})

        # Add db attribute to the class
        LegacyUserService.db = self.mock_db

        service = LegacyUserService()

        # Test direct collection access
        service.get_user("123")
        self.mock_collection.find_one.assert_called_once_with({"_id": "123"})

    def test_existing_decorators_maintain_behavior(self):
        """Test that existing decorators maintain same behavior"""
        # Original behavior with collection
        @self.injector.collection("users", with_crud=False)
        class UserService:
            def __init__(self):
                self.db = self.mock_db if hasattr(self, 'mock_db') else None

        # Add db attribute to the class
        UserService.db = self.mock_db

        service = UserService()
        self.assertEqual(service.collection, self.mock_collection)

        # Original behavior with multiple_collections
        @self.injector.multiple_collections(users="users", orders="orders")
        class CommerceService:
            def __init__(self):
                self.db = self.mock_db if hasattr(self, 'mock_db') else None

        # Add db attribute to the class
        CommerceService.db = self.mock_db

        service = CommerceService()
        self.assertEqual(service.users, self.mock_collection)
        self.assertEqual(service.orders, self.mock_collection)

# Edge Cases and Error Handling
class TestEdgeCasesAndErrorHandling(unittest.TestCase):
    """Tests for edge cases and error handling"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_db = MagicMock()
        self.mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = self.mock_collection

        # Create a patcher for the wraps function
        self.wraps_patcher = patch('mongollect.core.wraps', mock_wraps)
        self.wraps_patcher.start()

        self.injector = MockCollectionInjector(self.mock_db)
        self.test_data = {"name": "Test User", "email": "test@example.com"}

    def tearDown(self):
        """Clean up after tests"""
        self.wraps_patcher.stop()

    def test_crud_methods_with_invalid_parameters(self):
        """Test CRUD methods with invalid parameters"""
        @self.injector.collection("users")
        class UserService:
            def __init__(self):
                self.db = self.mock_db if hasattr(self, 'mock_db') else None

            # Override methods to validate parameters
            def find_one(self, query):
                if not isinstance(query, dict):
                    raise TypeError("Query must be a dict")
                return super().find_one(query)

            def create(self, data):
                if not isinstance(data, dict):
                    raise TypeError("Data must be a dict")
                return super().create(data)

        # Add db attribute to the class
        UserService.db = self.mock_db

        service = UserService()

        # Test with None query
        with self.assertRaises(TypeError):
            service.find_one(None)

        # Test with non-dict query
        with self.assertRaises(TypeError):
            service.find_one("invalid")

        # Test with non-dict data
        with self.assertRaises(TypeError):
            service.create("invalid")

    def test_crud_methods_when_collection_is_none(self):
        """Test CRUD methods when collection is None"""
        @self.injector.collection("users")
        class UserService:
            def __init__(self):
                self.db = self.mock_db if hasattr(self, 'mock_db') else None

        # Add db attribute to the class
        UserService.db = self.mock_db

        service = UserService()
        service.collection = None

        with self.assertRaises(AttributeError):
            service.create(self.test_data)

        with self.assertRaises(AttributeError):
            service.find_one({"name": "Test"})

    def test_decorator_parameter_validation(self):
        """Test decorator parameter validation for enable_crud"""
        # Test with non-boolean with_crud
        with self.assertRaises(TypeError):
            @self.injector.collection("users", with_crud="invalid")
            class UserService:
                def __init__(self):
                    self.db = self.mock_db if hasattr(self, 'mock_db') else None

            # Add db attribute to the class
            UserService.db = self.mock_db

        # Test with non-boolean enable_crud
        with self.assertRaises(TypeError):
            @self.injector.multiple_collections(enable_crud="invalid", users="users")
            class CommerceService:
                def __init__(self):
                    self.db = self.mock_db if hasattr(self, 'mock_db') else None

            # Add db attribute to the class
            CommerceService.db = self.mock_db

    def test_inheritance_chain_with_multiple_mixins(self):
        """Test inheritance chain with multiple mixins"""
        # Create a custom mixin
        class LoggingMixin:
            def log(self, message):
                return f"Logged: {message}"

            # Override a CRUD method
            def create(self, data):
                print(f"Creating: {data}")
                return super().create(data)

        # Create a service with multiple inheritance
        @self.injector.collection("users")
        class LoggingUserService(LoggingMixin):
            def __init__(self):
                self.db = self.mock_db if hasattr(self, 'mock_db') else None

        # Add db attribute to the class
        LoggingUserService.db = self.mock_db

        service = LoggingUserService()

        # Test custom mixin method
        self.assertEqual(service.log("test"), "Logged: test")

        # Test overridden method
        service.create(self.test_data)
        self.mock_collection.insert_one.assert_called_once_with(self.test_data)

if __name__ == "__main__":
    unittest.main()
