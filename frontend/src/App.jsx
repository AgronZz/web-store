
import { useEffect, useState } from "react";
import api from "./api/axios";
import Navbar from "./components/Navbar";
import ProductList from "./components/ProductList";
import Cart from "./components/Cart";
import OrdersDashboard from "./components/OrdersDashboard";
import ReportsDashboard from "./components/ReportsDashboard";
import Login from "./components/Login";
import CustomerOrders from "./components/CustomerOrders";
import UsersDashboard from "./components/UsersDashboard";

function App() {
    const [products, setProducts] = useState([]);
    const [cart, setCart] = useState([]);
    const [showCart, setShowCart] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem("user");

    try {
        return savedUser ? JSON.parse(savedUser) : null;
    } catch {
        localStorage.removeItem("user");
        localStorage.removeItem("access_token");
        return null;
    }
    });

    const handleLogout = () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");

        setUser(null);
        setCart([]);
        setShowCart(false);

        alert("You have logged out successfully."); 
    };  

    const [filters, setFilters] = useState({
        name: "",
        category_id: "",
        brand_id: "",
        gender_id: "",
        min_price: "",
        max_price: "",
        size_id: "",
        color_name: "",
    });

    const fetchProducts = async (searchFilters = {}) => {
        try {
            setLoading(true);
            setError("");

            const params = Object.fromEntries(
                Object.entries(searchFilters).filter(
                    ([, value]) => value !== ""
                )
            );

            const response = await api.get("/products/search", { params });
            setProducts(response.data.products);
        } catch (err) {
            console.error(err);
            setError("Could not load products.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchProducts();
    }, []);

    const handleFilterChange = (event) => {
        const { name, value } = event.target;

        setFilters((previous) => ({
            ...previous,
            [name]: value,
        }));
    };

    const handleSearch = (event) => {
        event.preventDefault();

        if (
            filters.min_price !== "" &&
            filters.max_price !== "" &&
            Number(filters.min_price) > Number(filters.max_price)
        ) {
            alert("Minimum price cannot be greater than maximum price.");
            return;
        }

        fetchProducts(filters);
    };

    const handleReset = () => {
        const emptyFilters = {
            name: "",
            category_id: "",
            brand_id: "",
            gender_id: "",
            min_price: "",
            max_price: "",
            size_id: "",
            color_name: "",
        };

        setFilters(emptyFilters);
        fetchProducts();
    };

    const addToCart = (product) => {
        setCart((previous) => {
            const existing = previous.find(
                (item) => item.product_id === product.product_id
            );

            if (existing) {
                if (existing.cart_quantity >= product.available_quantity) {
                    alert("Not enough stock available.");
                    return previous;
                }

                return previous.map((item) =>
                    item.product_id === product.product_id
                        ? { ...item, cart_quantity: item.cart_quantity + 1 }
                        : item
                );
            }

            return [
                ...previous,
                { ...product, cart_quantity: 1 },
            ];
        });
    };

    const handleCheckout = async () => {
        if (!user) {
        alert("Please log in before placing an order.");
        return;
        }
        if (cart.length === 0) {
            alert("Your cart is empty.");
            return;
        }

        try {
            const response = await api.post("/orders/", {
                client_id: 1,
                items: cart.map((item) => ({
                    product_id: item.product_id,
                    quantity: item.cart_quantity,
                })),
            });

            console.log("ORDER API RESPONSE:", response.data);

             alert(
                  `Order created successfully!\nOrder ID: ${response.data.order_id}\nTotal: €${response.data.total_amount}\nStatus: ${response.data.status}`
              );

              setCart([]);
              setShowCart(false);
              fetchProducts(filters);
        } catch (err) {
            console.error(err);
            alert(
                err.response?.data?.message || "Could not create order."
            );
        }
    };

    const cartCount = cart.reduce(
        (sum, item) => sum + item.cart_quantity,
        0
    );

    return (
        <>
            <Navbar
                cartCount={cartCount}
                onCartClick={() => setShowCart(!showCart)}
            />
            
            {user ? (
                <div className="auth-status">
                    <span>
                        Welcome, <strong>{user.username}</strong>
                        {" "}({user.role_name})
                    </span>

                    <button onClick={handleLogout}>
                        Logout
                    </button>
                </div>
            ) : (
                <Login onLogin={setUser} />
            )}


            <main className="container">
              {user && ["Admin", "Advanced User"].includes(user.role_name) && (
                    <>
                        <ReportsDashboard />
                        <OrdersDashboard />
                    </>
                )}
                {user && user.role_name === "Admin" && (
                  <UsersDashboard />
                )}
                {user && user.role_name === "Simple User" && (
                    <CustomerOrders />
                )}
                <section className="hero">
                    <p className="hero-label">NEW COLLECTION</p>
                    <h1>Find Your Style.</h1>
                    <p>
                        Discover clothing that matches your personality.
                    </p>
                    <a href="#products" className="shop-button">
                        Explore Collection
                    </a>
                </section>

                {showCart && (
                    <Cart
                        cart={cart}
                        setCart={setCart}
                        onCheckout={handleCheckout}
                    />
                )}

                <section id="products" className="products-section">
                    <div className="section-heading">
                        <div>
                            <p className="hero-label">OUR COLLECTION</p>
                            <h2>Featured Products</h2>
                        </div>

                        <span>{products.length} products</span>
                    </div>

                    <form className="filter-panel" onSubmit={handleSearch}>
                        <h3>Find Your Product</h3>

                        <div className="filter-grid">
                            <input
                                name="name"
                                placeholder="Search product name..."
                                value={filters.name}
                                onChange={handleFilterChange}
                            />

                            <select name="category_id" value={filters.category_id} onChange={handleFilterChange}>
                                <option value="">All Categories</option>
                                <option value="1">Shirts</option>
                                <option value="2">Pants</option>
                                <option value="3">Jackets</option>
                                <option value="4">Shoes</option>
                            </select>

                            <select name="brand_id" value={filters.brand_id} onChange={handleFilterChange}>
                                <option value="">All Brands</option>
                                <option value="1">Nike</option>
                                <option value="2">Adidas</option>
                                <option value="3">Zara</option>
                                <option value="4">Tommy Hilfiger</option>
                            </select>

                            <select name="gender_id" value={filters.gender_id} onChange={handleFilterChange}>
                                <option value="">All Genders</option>
                                <option value="1">Men</option>
                                <option value="2">Women</option>
                                <option value="3">Children</option>
                            </select>

                            <input
                                type="number"
                                name="min_price"
                                placeholder="Minimum price (€)"
                                min="0"
                                value={filters.min_price}
                                onChange={handleFilterChange}
                            />

                            <input
                                type="number"
                                name="max_price"
                                placeholder="Maximum price (€)"
                                min="0"
                                value={filters.max_price}
                                onChange={handleFilterChange}
                            />

                            <select name="size_id" value={filters.size_id} onChange={handleFilterChange}>
                                <option value="">All Sizes</option>
                                <option value="1">XS</option>
                                <option value="2">S</option>
                                <option value="3">M</option>
                                <option value="4">L</option>
                                <option value="5">XL</option>
                                <option value="6">XXL</option>
                            </select>

                            <select name="color_name" value={filters.color_name} onChange={handleFilterChange}>
                                <option value="">All Colors</option>
                                <option value="Black">Black</option>
                                <option value="White">White</option>
                                <option value="Red">Red</option>
                                <option value="Blue">Blue</option>
                                <option value="Green">Green</option>
                            </select>
                        </div>

                        <div className="filter-actions">
                            <button type="submit" className="add-button">
                                Search Products
                            </button>

                            <button type="button" className="reset-button" onClick={handleReset}>
                                Reset Filters
                            </button>
                        </div>
                    </form>

                    {loading && <p>Loading products...</p>}
                    {error && <p>{error}</p>}

                    {!loading && !error && products.length === 0 && (
                        <p>No products found.</p>
                    )}

                    {!loading && !error && products.length > 0 && (
                        <ProductList
                            products={products}
                            onAddToCart={addToCart}
                        />
                    )}
                </section>
            </main>
        </>
    );
}

export default App;
