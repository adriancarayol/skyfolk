import React from 'react';
export const FilterButton = ({ buttonName, buttonText, onClick }) => (
    <button className="waffes-effect waves-light btn white black-text" type="submit" name={buttonName} onClick={onClick}>{buttonText}</button>
);
