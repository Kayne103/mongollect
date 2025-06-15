from functools import wraps
from typing import Any, Callable, Type, TypeVar, Optional, Dict

T = TypeVar('T')

class CRUDMixin:
    """
    Mixin class that provides default CRUD operations for injected collections.

    These methods can be overridden by the user's class to provide custom implementations.
    """

    def create(self, data: Dict[str, Any]) -> Any:
        """
        Create a new document in the collection.

        Args:
            data: Document data to insert

        Returns:
            Insert result from MongoDB
        """
        if not hasattr(self, 'collection'):
            raise AttributeError("No collection found. Ensure class is decorated with @injector.collection()")
        return self.collection.insert_one(data)

    def create_many(self, data: list) -> Any:
        """
        Create multiple documents in the collection.

        Args:
            data: List of document data to insert

        Returns:
            Insert result from MongoDB
        """
        if not hasattr(self, 'collection'):
            raise AttributeError("No collection found. Ensure class is decorated with @injector.collection()")
        return self.collection.insert_many(data)

    def find_by_id(self, doc_id: Any) -> Optional[Dict[str, Any]]:
        """
        Find a document by its ID.

        Args:
            doc_id: Document ID to find

        Returns:
            Found document or None
        """
        if not hasattr(self, 'collection'):
            raise AttributeError("No collection found. Ensure class is decorated with @injector.collection()")
        return self.collection.find_one({"_id": doc_id})

    def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a single document matching the query.

        Args:
            query: MongoDB query filter

        Returns:
            Found document or None
        """
        if not hasattr(self, 'collection'):
            raise AttributeError("No collection found. Ensure class is decorated with @injector.collection()")
        return self.collection.find_one(query)

    def find_many(self, query: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> list:
        """
        Find multiple documents matching the query.

        Args:
            query: MongoDB query filter (default: {})
            limit: Maximum number of documents to return

        Returns:
            List of matching documents
        """
        if not hasattr(self, 'collection'):
            raise AttributeError("No collection found. Ensure class is decorated with @injector.collection()")

        query = query or {}
        cursor = self.collection.find(query)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)

    def find_all(self, query: Optional[Dict[str, Any]] = None, limit: Optional[int] = None) -> list:
        """
        Find all documents matching the query.

        Args:
            query: MongoDB query filter (default: {})
            limit: Maximum number of documents to return

        Returns:
            List of matching documents
        """
        if not hasattr(self, 'collection'):
            raise AttributeError("No collection found. Ensure class is decorated with @injector.collection()")

        query = query or {}
        cursor = self.collection.find(query)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)

    def update_by_id(self, doc_id: Any, update_data: Dict[str, Any]) -> Any:
        """
        Update a document by its ID.

        Args:
            doc_id: Document ID to update
            update_data: Update operations to apply

        Returns:
            Update result from MongoDB
        """
        if not hasattr(self, 'collection'):
            raise AttributeError("No collection found. Ensure class is decorated with @injector.collection()")
        return self.collection.update_one({"_id": doc_id}, update_data)

    def update_one(self, query: Dict[str, Any], update: Dict[str, Any]) -> Any:
        """
        Update a single document matching the query.

        Args:
            query: MongoDB query filter
            update: Update operations to apply

        Returns:
            Update result from MongoDB
        """
        if not hasattr(self, 'collection'):
            raise AttributeError("No collection found. Ensure class is decorated with @injector.collection()")
        return self.collection.update_one(query, update)

    def update_many(self, query: Dict[str, Any], update: Dict[str, Any]) -> Any:
        """
        Update multiple documents matching the query.

        Args:
            query: MongoDB query filter
            update: Update operations to apply

        Returns:
            Update result from MongoDB
        """
        if not hasattr(self, 'collection'):
            raise AttributeError("No collection found. Ensure class is decorated with @injector.collection()")
        return self.collection.update_many(query, update)

    def delete_by_id(self, doc_id: Any) -> Any:
        """
        Delete a document by its ID.

        Args:
            doc_id: Document ID to delete

        Returns:
            Delete result from MongoDB
        """
        if not hasattr(self, 'collection'):
            raise AttributeError("No collection found. Ensure class is decorated with @injector.collection()")
        return self.collection.delete_one({"_id": doc_id})

    def delete_one(self, query: Dict[str, Any]) -> Any:
        """
        Delete a single document matching the query.

        Args:
            query: MongoDB query filter

        Returns:
            Delete result from MongoDB
        """
        if not hasattr(self, 'collection'):
            raise AttributeError("No collection found. Ensure class is decorated with @injector.collection()")
        return self.collection.delete_one(query)

    def delete_many(self, query: Dict[str, Any]) -> Any:
        """
        Delete multiple documents matching the query.

        Args:
            query: MongoDB query filter

        Returns:
            Delete result from MongoDB
        """
        if not hasattr(self, 'collection'):
            raise AttributeError("No collection found. Ensure class is decorated with @injector.collection()")
        return self.collection.delete_many(query)

    def count_documents(self, query: Optional[Dict[str, Any]] = None) -> int:
        """
        Count documents matching the query.

        Args:
            query: MongoDB query filter (default: {})

        Returns:
            Number of matching documents
        """
        if not hasattr(self, 'collection'):
            raise AttributeError("No collection found. Ensure class is decorated with @injector.collection()")

        query = query or {}
        return self.collection.count_documents(query)

    def count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """
        Alias for count_documents.

        Args:
            query: MongoDB query filter (default: {})

        Returns:
            Number of matching documents
        """
        return self.count_documents(query)

    def exists(self, query: Dict[str, Any]) -> bool:
        """
        Check if a document matching the query exists.

        Args:
            query: MongoDB query filter

        Returns:
            True if a matching document exists, False otherwise
        """
        if not hasattr(self, 'collection'):
            raise AttributeError("No collection found. Ensure class is decorated with @injector.collection()")
        return self.collection.count_documents(query, limit=1) > 0


class CollectionInjector:
    """
    A decorator-based dependency injector for database collections.

    This class provides a mechanism to inject database collection references
    into classes through a decorator pattern. It wraps target classes to
    automatically provide access to specified database collections along
    with default CRUD operations that can be overridden.

    Attributes:
        db: The database instance used to access collections.
    """

    def __init__(self, db: Any):
        """
        Initialize the CollectionInjector with a database instance.

        Args:
            db: Database instance that supports collection access via indexing.
                Expected to support db[collection_name] syntax.

        Raises:
            ValueError: If db is None.
        """
        if db is None:
            raise ValueError("Database instance cannot be None")
        self.db = db

    def collection(self, name: str, with_crud: bool = True) -> Callable[[Type[T]], Type[T]]:
        """
        Decorator factory that injects a database collection into a class.

        This method returns a decorator that wraps the target class, adding
        a 'collection' attribute that references the specified database collection.
        The wrapped class maintains all original functionality while gaining
        access to the injected collection and optional default CRUD operations.

        Args:
            name: The name of the database collection to inject.
            with_crud: Whether to include default CRUD operations (default: True).

        Returns:
            A decorator function that wraps the target class.

        Raises:
            ValueError: If collection name is empty or None.
            KeyError: If the specified collection doesn't exist in the database.

        Example:
            >>> injector = CollectionInjector(database)
            >>> @injector.collection('users')
            ... class UserService:
            ...     def get_user(self, user_id):
            ...         return self.find_one({'_id': user_id})  # Uses default CRUD
            ...
            ...     def create(self, data):  # Override default create method
            ...         # Custom validation logic
            ...         return super().create(data)
        """
        if not name or not isinstance(name, str):
            raise ValueError("Collection name must be a non-empty string")

        def wrapper(cls: Type[T]) -> Type[T]:
            """
            Decorator function that wraps the target class.

            Args:
                cls: The class to be wrapped and enhanced with collection injection.

            Returns:
                A new class that inherits from the original class with
                collection injection functionality.
            """
            if not isinstance(cls, type):
                raise TypeError("Decorator can only be applied to classes")

            # Validate collection exists at decoration time
            try:
                _ = self.db[name]  # Test collection access
            except (KeyError, AttributeError) as e:
                raise KeyError(f"Collection '{name}' not accessible in database") from e

            # Create base classes tuple
            base_classes = [cls]
            if with_crud:
                base_classes.append(CRUDMixin)

            @wraps(cls)
            class Wrapped(*base_classes):
                """
                Wrapped version of the original class with collection injection.

                This class inherits all functionality from the original class
                and adds automatic collection injection during initialization.
                Optionally includes default CRUD operations that can be overridden.
                """

                def __init__(self, *args, **kwargs):
                    """
                    Initialize the wrapped instance with collection injection.

                    Calls the parent class constructor and then injects the
                    specified database collection as an instance attribute.

                    Args:
                        *args: Variable length argument list passed to parent constructor.
                        **kwargs: Arbitrary keyword arguments passed to parent constructor.
                    """
                    # Initialize all parent classes
                    for base in base_classes:
                        if hasattr(base, '__init__'):
                            try:
                                base.__init__(self, *args, **kwargs)
                            except TypeError:
                                # Handle classes that don't accept arguments
                                if base is not object:
                                    base.__init__(self)

                    # Inject the collection
                    self.collection = self.db[name]

                def __repr__(self) -> str:
                    """Return a string representation of the wrapped instance."""
                    crud_info = " with CRUD" if with_crud else ""
                    return f"{cls.__name__}(collection='{name}'{crud_info})"

            # Preserve original class metadata
            Wrapped.__name__ = cls.__name__
            Wrapped.__qualname__ = cls.__qualname__
            Wrapped.__module__ = cls.__module__
            Wrapped.__doc__ = cls.__doc__ or f"{cls.__name__} with injected collection '{name}'"

            return Wrapped
        return wrapper

    def multiple_collections(self, with_crud: bool = False, **collections: str) -> Callable[[Type[T]], Type[T]]:
        """
        Decorator factory that injects multiple database collections into a class.

        Note: CRUD operations are disabled by default for multiple collections
        to avoid ambiguity about which collection the operations should target.

        Args:
            with_crud: Whether to include CRUD operations (default: False for multiple collections)
            **collections: Keyword arguments where keys are attribute names
                          and values are collection names.

        Returns:
            A decorator function that wraps the target class.

        Example:
            >>> @injector.multiple_collections(users='users', orders='orders')
            ... class CompositeService:
            ...     def get_user_orders(self, user_id):
            ...         user = self.users.find_one({'_id': user_id})
            ...         return list(self.orders.find({'user_id': user_id}))
        """
        if not collections:
            raise ValueError("At least one collection must be specified")

        def wrapper(cls: Type[T]) -> Type[T]:
            if not isinstance(cls, type):
                raise TypeError("Decorator can only be applied to classes")

            # Validate all collections exist
            for attr_name, collection_name in collections.items():
                try:
                    _ = self.db[collection_name]
                except (KeyError, AttributeError) as e:
                    raise KeyError(f"Collection '{collection_name}' not accessible in database") from e

            # Create base classes tuple
            base_classes = [cls]
            if with_crud:
                base_classes.append(CRUDMixin)

            @wraps(cls)
            class Wrapped(*base_classes):
                def __init__(self, *args, **kwargs):
                    # Initialize all parent classes
                    for base in base_classes:
                        if hasattr(base, '__init__'):
                            try:
                                base.__init__(self, *args, **kwargs)
                            except TypeError:
                                # Handle classes that don't accept arguments
                                if base is not object:
                                    base.__init__(self)

                    # Inject all collections
                    for attr_name, collection_name in collections.items():
                        setattr(self, attr_name, self.db[collection_name])

                    # For CRUD operations with multiple collections, set the first one as default
                    if with_crud and collections:
                        first_collection = next(iter(collections.values()))
                        self.collection = self.db[first_collection]

                def __repr__(self) -> str:
                    collections_str = ', '.join(f"{k}='{v}'" for k, v in collections.items())
                    crud_info = " with CRUD" if with_crud else ""
                    return f"{cls.__name__}(collections={{{collections_str}}}{crud_info})"

            # Preserve original class metadata
            Wrapped.__name__ = cls.__name__
            Wrapped.__qualname__ = cls.__qualname__
            Wrapped.__module__ = cls.__module__
            Wrapped.__doc__ = cls.__doc__ or f"{cls.__name__} with injected collections: {list(collections.keys())}"

            return Wrapped
        return wrapper

    def __repr__(self) -> str:
        """Return a string representation of the CollectionInjector."""
        return f"CollectionInjector(db={type(self.db).__name__})"
