from functools import wraps
from typing import Any, Callable, Type, TypeVar, Optional

T = TypeVar('T')

class CollectionInjector:
    """
    A decorator-based dependency injector for database collections.
    
    This class provides a mechanism to inject database collection references
    into classes through a decorator pattern. It wraps target classes to
    automatically provide access to specified database collections.
    
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

    def collection(self, name: str) -> Callable[[Type[T]], Type[T]]:
        """
        Decorator factory that injects a database collection into a class.
        
        This method returns a decorator that wraps the target class, adding
        a 'collection' attribute that references the specified database collection.
        The wrapped class maintains all original functionality while gaining
        access to the injected collection.
        
        Args:
            name: The name of the database collection to inject.
        
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
            ...         return self.collection.find_one({'_id': user_id})
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

            @wraps(cls)
            class Wrapped(cls):
                """
                Wrapped version of the original class with collection injection.
                
                This class inherits all functionality from the original class
                and adds automatic collection injection during initialization.
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
                    super().__init__(*args, **kwargs)
                    self.collection = self.db[name]

                def __repr__(self) -> str:
                    """Return a string representation of the wrapped instance."""
                    return f"{cls.__name__}(collection='{name}')"

            # Preserve original class metadata
            Wrapped.__name__ = cls.__name__
            Wrapped.__qualname__ = cls.__qualname__
            Wrapped.__module__ = cls.__module__
            Wrapped.__doc__ = cls.__doc__ or f"{cls.__name__} with injected collection '{name}'"

            return Wrapped
        return wrapper

    def multiple_collections(self, **collections: str) -> Callable[[Type[T]], Type[T]]:
        """
        Decorator factory that injects multiple database collections into a class.
        
        Args:
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

            @wraps(cls)
            class Wrapped(cls):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    for attr_name, collection_name in collections.items():
                        setattr(self, attr_name, self.db[collection_name])

                def __repr__(self) -> str:
                    collections_str = ', '.join(f"{k}='{v}'" for k, v in collections.items())
                    return f"{cls.__name__}(collections={{{collections_str}}})"

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