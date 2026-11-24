
import { useEffect, useState } from "react";
import api from "../api/axios";

function UsersDashboard() {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");

    const [form, setForm] = useState({
        username: "",
        email: "",
        password: "",
        role_id: "3"
    });

    const [editingUser, setEditingUser] = useState(null);

    const currentUser = JSON.parse(localStorage.getItem("user") || "null");

    const fetchUsers = async () => {
        try {
            setLoading(true);
            setError("");
            const response = await api.get("/users/");
            setUsers(response.data.users || []);
        } catch (err) {
            setError(err.response?.data?.message || "Could not load users.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handleCreate = async (e) => {
        e.preventDefault();
        setError("");
        setMessage("");

        try {
            await api.post("/users/", {
                ...form,
                role_id: Number(form.role_id)
            });

            setForm({
                username: "",
                email: "",
                password: "",
                role_id: "3"
            });

            setMessage("User created successfully.");
            fetchUsers();
        } catch (err) {
            setError(err.response?.data?.message || "Could not create user.");
        }
    };

    const startEditing = (user) => {
        setEditingUser({
            user_id: user.user_id,
            username: user.username,
            email: user.email,
            role_id: String(user.role_id)
        });
        setError("");
        setMessage("");
    };

    const handleUpdate = async (e) => {
        e.preventDefault();
        setError("");
        setMessage("");

        try {
            await api.put(`/users/${editingUser.user_id}`, {
                username: editingUser.username,
                email: editingUser.email,
                role_id: Number(editingUser.role_id)
            });

            setEditingUser(null);
            setMessage("User updated successfully.");
            fetchUsers();
        } catch (err) {
            setError(err.response?.data?.message || "Could not update user.");
        }
    };

    const handleDelete = async (user) => {
        if (user.user_id === currentUser?.user_id) {
            setError("You cannot delete your own account while logged in.");
            return;
        }

        if (!window.confirm(`Are you sure you want to delete ${user.username}?`)) {
            return;
        }

        setError("");
        setMessage("");

        try {
            await api.delete(`/users/${user.user_id}`);
            setMessage("User deleted successfully.");
            fetchUsers();
        } catch (err) {
            setError(err.response?.data?.message || "Could not delete user.");
        }
    };

    return (
        <section className="users-dashboard">
            <div className="orders-heading">
                <div>
                    <p className="hero-label">ADMINISTRATION</p>
                    <h2>User Management</h2>
                    <p>Create, edit and manage store accounts.</p>
                </div>
                <button className="reset-button" onClick={fetchUsers}>
                    Refresh Users
                </button>
            </div>

            {error && <p className="error-message">{error}</p>}
            {message && <p className="success-message">{message}</p>}

            <div className="user-form-card">
                <h3>Create New User</h3>

                <form onSubmit={handleCreate} className="user-form">
                    <input
                        name="username"
                        placeholder="Username"
                        value={form.username}
                        onChange={handleChange}
                        required
                    />

                    <input
                        name="email"
                        type="email"
                        placeholder="Email"
                        value={form.email}
                        onChange={handleChange}
                        required
                    />

                    <input
                        name="password"
                        type="password"
                        placeholder="Password (minimum 8 characters)"
                        value={form.password}
                        onChange={handleChange}
                        minLength={8}
                        required
                    />

                    <select
                        name="role_id"
                        value={form.role_id}
                        onChange={handleChange}
                    >
                        <option value="1">Admin</option>
                        <option value="2">Advanced User</option>
                        <option value="3">Simple User</option>
                    </select>

                    <button type="submit">Create User</button>
                </form>
            </div>

            <div className="users-list-card">
                <h3>Registered Users ({users.length})</h3>

                {loading ? (
                    <p>Loading users...</p>
                ) : users.length === 0 ? (
                    <p>No users found.</p>
                ) : (
                    <div className="users-table-wrapper">
                        <table className="users-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Username</th>
                                    <th>Email</th>
                                    <th>Role</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>

                            <tbody>
                                {users.map((user) => (
                                    <tr key={user.user_id}>
                                        <td>{user.user_id}</td>
                                        <td>{user.username}</td>
                                        <td>{user.email}</td>
                                        <td>{user.role_name}</td>
                                        <td>
                                            <button
                                                type="button"
                                                onClick={() => startEditing(user)}
                                            >
                                                Edit
                                            </button>

                                            <button
                                                type="button"
                                                onClick={() => handleDelete(user)}
                                                disabled={user.user_id === currentUser?.user_id}
                                            >
                                                Delete
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {editingUser && (
                <div className="user-form-card">
                    <h3>Edit User #{editingUser.user_id}</h3>

                    <form onSubmit={handleUpdate} className="user-form">
                        <input
                            value={editingUser.username}
                            onChange={(e) =>
                                setEditingUser({
                                    ...editingUser,
                                    username: e.target.value
                                })
                            }
                            placeholder="Username"
                            required
                        />

                        <input
                            type="email"
                            value={editingUser.email}
                            onChange={(e) =>
                                setEditingUser({
                                    ...editingUser,
                                    email: e.target.value
                                })
                            }
                            placeholder="Email"
                            required
                        />

                        <select
                            value={editingUser.role_id}
                            onChange={(e) =>
                                setEditingUser({
                                    ...editingUser,
                                    role_id: e.target.value
                                })
                            }
                        >
                            <option value="1">Admin</option>
                            <option value="2">Advanced User</option>
                            <option value="3">Simple User</option>
                        </select>

                        <button type="submit">Save Changes</button>
                        <button type="button" onClick={() => setEditingUser(null)}>
                            Cancel
                        </button>
                    </form>
                </div>
            )}
        </section>
    );
}

export default UsersDashboard;
