import React, { useState, useEffect } from "react";
import { createUser, getUsers } from "../services/api";
import "../styles/style.css";

const UsersPage = () => {
    const [formData, setFormData] = useState({
        username: "", password: "", first_name: "", last_name: "",
        age: "", hobbies: "", language: ""
    });
    const [message, setMessage] = useState("");
    const [users, setUsers] = useState([]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const result = await createUser(formData);
            setMessage(`✅ User created. ID: ${result.id}`);
            setUsers((prev) => [...prev, result]);
            setFormData({
                username: "", password: "", first_name: "", last_name: "",
                age: "", hobbies: "", language: ""
            });
        } catch (error) {
            setMessage(error.message || "Failed to create user.");
        }
    };

    useEffect(() => {
        getUsers()
            .then(setUsers)
            .catch((err) => setMessage(" Could not load users"));
    }, []);

    return (
        <div className="page-container">
            <div className="section-header">
                <h2>👥 Manage Users</h2>
                <p>Create and manage elderly user profiles linked to AI agents.</p>
            </div>

            <div className="card-form">
                <h3>Create New User</h3>
                <form onSubmit={handleSubmit} className="form-grid">
                    {[
                        ["username", "Username"],
                        ["password", "Password"],
                        ["first_name", "First Name"],
                        ["last_name", "Last Name"],
                        ["age", "Age"],
                        ["hobbies", "Hobbies"],
                        ["language", "Language"],
                    ].map(([key, label]) => (
                        <div key={key} className="form-group">
                            <label htmlFor={key}>{label}</label>
                            <input
                                type={key === "password" ? "password" : key === "age" ? "number" : "text"}
                                name={key}
                                value={formData[key]}
                                onChange={handleChange}
                                required
                            />
                        </div>
                    ))}
                    <button type="submit" className="button-green">➕ Create User</button>
                </form>
                {message && <p className="form-message">{message}</p>}
            </div>

            <div className="card-list">
                <h3>Existing Users</h3>
                {users.length === 0 ? (
                    <p>No users found.</p>
                ) : (
                    <table className="user-table">
                        <thead>
                            <tr>
                                <th>Username</th>
                                <th>First Name</th>
                                <th>Last Name</th>
                                <th>Age</th>
                                <th>Hobbies</th>
                                <th>Language</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map((user) => (
                                <tr key={user.id}>
                                    <td>{user.username}</td>
                                    <td>{user.first_name}</td>
                                    <td>{user.last_name}</td>
                                    <td>{user.age}</td>
                                    <td>{user.hobbies}</td>
                                    <td>{user.language}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
};

export default UsersPage;
