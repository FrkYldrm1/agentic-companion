import React from "react";

const UserList = ({ users }) => (
    <div className="table-container">
        <h3>📋 Registered Users</h3>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>First</th>
                    <th>Last</th>
                    <th>Age</th>
                    <th>Language</th>
                </tr>
            </thead>
            <tbody>
                {users.map((user) => (
                    <tr key={user.id}>
                        <td>{user.id}</td>
                        <td>{user.username}</td>
                        <td>{user.first_name}</td>
                        <td>{user.last_name}</td>
                        <td>{user.age}</td>
                        <td>{user.language}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    </div>
);

export default UserList;
