# `mongollect`

**`mongollect`** is a tiny, zero-dependency Python utility that lets you inject MongoDB collections into your classes using decorators.

---

## 🚀 Features

✅ Simple `@injector.collection("name")` decorator for single collections  
✅ `@injector.multiple_collections()` decorator for multiple collections  
✅ Keeps your services clean — no repeated DB connection logic  
✅ Lets **you control the MongoDB connection** (great for FastAPI, Flask, etc.)  
✅ Easy to test and mock  
✅ Early validation of collection existence  
✅ Full type hint support

---

## 💻 Installation

```bash
pip install mongollect
```

---

## ⚡ Quick Start

### Single Collection Injection

```python
from pymongo import MongoClient
from mongollect import CollectionInjector

# Set up your MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]

# Create the injector
injector = CollectionInjector(db)

# Apply to your service
@injector.collection("accounts")
class AccountService:
    def create(self, data):
        return self.collection.insert_one(data)

    def find_all(self):
        return list(self.collection.find())

# Example usage
service = AccountService()
service.create({"username": "john_doe", "email": "john@example.com"})
print(service.find_all())
```

### Multiple Collections Injection

```python
# Inject multiple collections into a single class
@injector.multiple_collections(
    users="users",
    orders="orders", 
    products="products"
)
class CommerceService:
    def get_user_orders(self, user_id):
        # Access collections via their attribute names
        user = self.users.find_one({"_id": user_id})
        orders = list(self.orders.find({"user_id": user_id}))
        return {"user": user, "orders": orders}
    
    def get_order_details(self, order_id):
        order = self.orders.find_one({"_id": order_id})
        if order:
            # Enrich with product details
            product_ids = [item["product_id"] for item in order.get("items", [])]
            products = list(self.products.find({"_id": {"$in": product_ids}}))
            order["product_details"] = products
        return order

# Example usage
commerce = CommerceService()
user_orders = commerce.get_user_orders("user123")
order_details = commerce.get_order_details("order456")
```

---

## 🛠 API Reference

### `CollectionInjector(db)`

Create an injector with your MongoDB database instance.

**Parameters:**
* **`db`** → A `pymongo.database.Database` instance

**Raises:**
* `ValueError` → If db is None

---

### `@injector.collection(name)`

A class decorator that injects a single MongoDB collection into `self.collection`.

**Parameters:**
* **`name`** → The MongoDB collection name (string)

**Raises:**
* `ValueError` → If collection name is empty or not a string
* `KeyError` → If the specified collection doesn't exist in the database
* `TypeError` → If decorator is not applied to a class

**Example:**
```python
@injector.collection("users")
class UserService:
    def find_user(self, user_id):
        return self.collection.find_one({"_id": user_id})
```

---

### `@injector.multiple_collections(**collections)`

A class decorator that injects multiple MongoDB collections as named attributes.

**Parameters:**
* **`**collections`** → Keyword arguments where keys are attribute names and values are collection names

**Raises:**
* `ValueError` → If no collections are specified
* `KeyError` → If any specified collection doesn't exist in the database
* `TypeError` → If decorator is not applied to a class

**Example:**
```python
@injector.multiple_collections(
    users="user_collection",
    posts="post_collection", 
    comments="comment_collection"
)
class BlogService:
    def get_user_posts_with_comments(self, user_id):
        user = self.users.find_one({"_id": user_id})
        posts = list(self.posts.find({"author_id": user_id}))
        
        for post in posts:
            post["comments"] = list(
                self.comments.find({"post_id": post["_id"]})
            )
        
        return {"user": user, "posts": posts}
```

---

## 🎯 Advanced Usage

### Custom Attribute Names

When using `multiple_collections`, you can map collections to custom attribute names:

```python
@injector.multiple_collections(
    user_db="users",           # self.user_db -> "users" collection
    order_db="orders",         # self.order_db -> "orders" collection  
    inventory="products"       # self.inventory -> "products" collection
)
class ECommerceService:
    def process_order(self, order_data):
        # Use custom attribute names
        user = self.user_db.find_one({"_id": order_data["user_id"]})
        product = self.inventory.find_one({"_id": order_data["product_id"]})
        
        if user and product:
            return self.order_db.insert_one(order_data)
```

### Error Handling

The decorators validate collections at decoration time, not runtime:

```python
# This will raise KeyError immediately when the decorator is applied
try:
    @injector.collection("nonexistent_collection")
    class BadService:
        pass
except KeyError as e:
    print(f"Collection validation failed: {e}")
```

---

## ✅ Why use `mongollect`?

* **Clean Architecture**: Keeps your service layer clean and DRY
* **Flexible**: Works with any MongoDB database you set up
* **Testable**: Easy to inject mock databases for testing
* **Type Safe**: Full type hint support for better IDE experience
* **Early Validation**: Catches collection errors at decoration time
* **Lightweight**: Zero dependencies beyond Python standard library
* **Multiple Collections**: Handle complex services that need multiple collections

---

## 📄 License

MIT — do whatever you want, just give credit!
```