
import { useEffect, useState } from "react";
import api from "../api/axios";

function OrdersDashboard() {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const fetchOrders = async () => {
        try {
            setLoading(true);
            const response = await api.get("/orders/");
            setOrders(response.data.orders || []);
            setError("");
        } catch (err) {
            console.error(err);
            setError("Could not load orders.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchOrders();
    }, []);

    const updateOrder = async (orderId, action) => {
        try {
            if (action === "status") {
                const nextStatuses = {
                    confirmed: "processing",
                    processing: "shipped",
                    shipped: "delivered",
                };

                const order = orders.find(
                    (item) => item.order_id === orderId
                );

                await api.put(`/orders/${orderId}/status`, {
                    status: nextStatuses[order.status],
                });
            } else {
                await api.put(`/orders/${orderId}/${action}`);
            }

            await fetchOrders();
            alert("Order updated successfully!");
        } catch (err) {
            console.error(err);
            alert(
                err.response?.data?.message || "Could not update order."
            );
        }
    };

    const getNextAction = (status) => {
        const actions = {
            confirmed: { endpoint: "status", label: "Process Order" },
            processing: { endpoint: "status", label: "Ship Order" },
            shipped: { endpoint: "status", label: "Mark Delivered" },
        };

        return actions[status];
    };

    return (
        <section className="orders-dashboard">
            <div className="orders-heading">
                <div>
                    <p className="hero-label">ADMINISTRATION</p>
                    <h2>Orders Management</h2>
                </div>

                <button onClick={fetchOrders} className="reset-button">
                    Refresh Orders
                </button>
            </div>

            {loading && <p>Loading orders...</p>}
            {error && <p>{error}</p>}

            {!loading && !error && orders.length === 0 && (
                <p>No orders found.</p>
            )}

            {!loading && !error && orders.map((order) => {
                const nextAction = getNextAction(order.status);

                return (
                    <div className="order-card" key={order.order_id}>
                        <div className="order-customer">
                            <h3>Order #{order.order_id}</h3>

                            <p>
                                <strong>Customer:</strong>{" "}
                                {order.customer_name || "Unknown Customer"}
                            </p>

                            <p>
                                <strong>Username:</strong>{" "}
                                {order.username || "Not linked"}
                            </p>

                            <p>
                                <strong>Email:</strong>{" "}
                                {order.email || "Not available"}
                            </p>

                            <p>
                                <strong>Phone:</strong>{" "}
                                {order.phone || "Not provided"}
                            </p>

                            <p>
                                <strong>City:</strong>{" "}
                                {order.city || "Not provided"}
                            </p>
                        </div>

                        <div className="order-products">
                            <h4>Ordered Products</h4>

                            {order.items && order.items.length > 0 ? (
                                order.items.map((item) => (
                                    <div
                                        className="order-product-item"
                                        key={item.order_item_id}
                                    >
                                        <div>
                                            <strong>{item.product_name}</strong>
                                            <p>
                                                Quantity: {item.quantity} × €
                                                {Number(item.unit_price).toFixed(2)}
                                            </p>
                                        </div>

                                        <strong>
                                            €{Number(item.subtotal).toFixed(2)}
                                        </strong>
                                    </div>
                                ))
                            ) : (
                                <p>No product details available.</p>
                            )}
                        </div>

                        <div className="order-details">
                            <p>Date: {order.order_date}</p>

                            <p>
                                Total: €{Number(order.total_amount).toFixed(2)}
                            </p>

                            <p>
                                Status: <strong>{order.status}</strong>
                            </p>

                            <div className="order-actions">
                                {order.status === "pending" && (
                                    <button
                                        className="confirm-button"
                                        onClick={() =>
                                            updateOrder(order.order_id, "confirm")
                                        }
                                    >
                                        Confirm
                                    </button>
                                )}

                                {nextAction && (
                                    <button
                                        className="confirm-button"
                                        onClick={() =>
                                            updateOrder(
                                                order.order_id,
                                                nextAction.endpoint
                                            )
                                        }
                                    >
                                        {nextAction.label}
                                    </button>
                                )}

                                {["pending", "confirmed"].includes(order.status) && (
                                    <button
                                        className="cancel-button"
                                        onClick={() =>
                                            updateOrder(order.order_id, "cancel")
                                        }
                                    >
                                        Cancel
                                    </button>
                                )}
                            </div>
                        </div>
                    </div>
                );
            })}
        </section>
    );
}

export default OrdersDashboard;
