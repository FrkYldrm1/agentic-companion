import React from "react";

const UserForm = ({ formData, onChange, onSubmit }) => (
    <form onSubmit={onSubmit} className="form-container">
        {Object.keys(formData).map((field) => (
            <div key={field} className="form-group">
                <label>{field.replace("_", " ")}</label>
                <input
                    type={field === "password" ? "password" : "text"}
                    name={field}
                    value={formData[field]}
                    onChange={onChange}
                    required
                />
            </div>
        ))}
        <button type="submit" className="submit-btn">Create User</button>
    </form>
);

export default UserForm;
