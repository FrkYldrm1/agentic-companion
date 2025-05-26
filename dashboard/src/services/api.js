const API_BASE = "http://localhost:8000";

/**
 * Fetches all flagged responses pending review.
 */
export async function getFlaggedResponses() {
    const res = await fetch(`${API_BASE}/governance/flagged`);
    if (!res.ok) {
        throw new Error(`Failed to fetch flags: ${res.status}`);
    }
    return await res.json();
}

/**
 * Sends a resolution decision for a specific flag.
 * @param {number} id - ID of the flagged response.
 * @param {"approved" | "edited" | "rejected"} decision
 * @param {string | null} replacementText - Only required for edited decisions.
 */
export async function resolveFlag(id, decision, replacementText = null) {
    const payload = {
        decision,
        ...(decision === "edited" && { replacement_text: replacementText }),
    };

    const res = await fetch(`${API_BASE}/governance/flagged/${id}/resolve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Failed to resolve flag: ${res.status} - ${errorText}`);
    }
}

/**
 * Creates a new user.
 * @param {Object} userData
 */
export async function createUser(userData) {
    const payload = {
        ...userData,
        age: parseInt(userData.age, 10) || 0, // fallback if empty
    };

    const res = await fetch(`${API_BASE}/users`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    if (!res.ok) {
        const error = await res.text();
        console.error("Backend error:", error);
        throw new Error(`Failed to create user: ${res.status} — ${error}`);
    }

    if (!res.ok) {
    const errorText = await res.text();
    if (res.status === 500 && errorText.includes("UNIQUE constraint failed")) {
        throw new Error(" Username already exists. Choose another one.");
    }
    throw new Error(`Failed to create user: ${res.status} — ${errorText}`);
}

    return await res.json();
}


/**
 * Fetches all users.
 */
export async function getUsers() {
    const res = await fetch(`${API_BASE}/users`);
    if (!res.ok) throw new Error(`Failed to fetch users: ${res.status}`);
    return await res.json();
}

export async function fetchUserCount() {
    const res = await fetch("http://localhost:8000/users");
    const data = await res.json();
    return data.length; // assuming response is an array of users
}

export async function fetchPendingFlagCount() {
    const res = await fetch("http://localhost:8000/governance/flagged");
    const data = await res.json();
    return data.filter((flag) => flag.status === "pending").length;
}


