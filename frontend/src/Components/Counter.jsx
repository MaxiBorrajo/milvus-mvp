import React, { useState } from "react";

const Counter = ({ initialValue = 0, maxValue = 100, minValue = 0 }) => {
  const [count, setCount] = useState(initialValue);
  const [showMessage, setShowMessage] = useState(false);

  const increment = () => {
    if (count < maxValue) {
      setCount((prev) => prev + 1);
      setShowMessage(false);
    } else {
      setShowMessage(true);
    }
  };

  const decrement = () => {
    if (count > minValue) {
      setCount((prev) => prev - 1);
      setShowMessage(false);
    } else {
      setShowMessage(true);
    }
  };

  const reset = () => {
    setCount(initialValue);
    setShowMessage(false);
  };

  const isAtMax = count >= maxValue;
  const isAtMin = count <= minValue;

  return (
    <div className="counter-container">
      <h3>Counter Component</h3>
      <div className="counter-display">
        <span className="counter-value">{count}</span>
      </div>

      <div className="counter-controls">
        <button
          className={`counter-btn ${isAtMin ? "disabled" : ""}`}
          onClick={decrement}
          disabled={isAtMin}
        >
          -
        </button>

        <button className="counter-btn reset-btn" onClick={reset}>
          Reset
        </button>

        <button
          className={`counter-btn ${isAtMax ? "disabled" : ""}`}
          onClick={increment}
          disabled={isAtMax}
        >
          +
        </button>
      </div>

      {showMessage && (
        <div className="counter-message">
          {isAtMax ? "Maximum value reached!" : "Minimum value reached!"}
        </div>
      )}

      <div className="counter-info">
        <p>
          Range: {minValue} - {maxValue}
        </p>
        <p>Current: {count}</p>
      </div>
    </div>
  );
};

export default Counter;
