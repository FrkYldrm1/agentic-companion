import React from "react";
import FlagCard from "./FlagCard";

const FlagList = ({ flags, editedResponses, onChange, onAction }) => (
    <div className="card-list">
        {flags.map((flag) => (
            <FlagCard
                key={flag.id}
                flag={flag}
                value={editedResponses[flag.id] || flag.response_text}
                onChange={onChange}
                onAction={onAction}
            />
        ))}
    </div>
);

export default FlagList;
