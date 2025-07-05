# Milvus MVP - React JSX Frontend

This is a React application built with JSX that demonstrates modern React development practices.

## 🚀 Features

- **JSX Components**: All components use JSX syntax for declarative UI
- **Component Architecture**: Modular, reusable components
- **State Management**: React hooks for state management
- **Event Handling**: Interactive components with event handlers
- **Conditional Rendering**: Dynamic UI based on state
- **Props System**: Component communication through props
- **Responsive Design**: Mobile-first responsive layout
- **Modern Styling**: CSS with gradients, animations, and glassmorphism effects

## 📁 Project Structure

```
src/
├── Components/          # Reusable UI components
│   ├── Header.jsx      # Navigation header component
│   ├── Button.jsx      # Custom button component
│   └── Counter.jsx     # Interactive counter with state
├── Pages/              # Page components
│   └── Home.jsx        # Main home page
├── App.jsx             # Main application component
├── index.jsx           # Application entry point
├── App.css             # Application styles
└── index.css           # Global styles
```

## 🧩 Components

### Header Component

- Navigation bar with logo and menu
- Props: `title`, `showLogo`
- Conditional rendering for logo display

### Button Component

- Customizable button with variants
- Props: `children`, `onClick`, `variant`, `disabled`, `type`
- Event handling and disabled states

### Counter Component

- Interactive counter with state management
- Props: `initialValue`, `maxValue`, `minValue`
- Conditional rendering for limits
- Event handlers for increment/decrement/reset

## 🎨 Styling Features

- **Glassmorphism**: Translucent backgrounds with blur effects
- **Gradients**: Beautiful gradient backgrounds and buttons
- **Animations**: Smooth transitions and hover effects
- **Responsive**: Mobile-first design with breakpoints
- **Modern UI**: Clean, modern interface design

## 🚀 Getting Started

1. Install dependencies:

   ```bash
   npm install
   ```

2. Start the development server:

   ```bash
   npm start
   ```

3. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

## 🔧 Available Scripts

- `npm start` - Runs the app in development mode
- `npm run build` - Builds the app for production
- `npm test` - Launches the test runner
- `npm run eject` - Ejects from Create React App

## 📱 JSX Examples

### Basic JSX Component

```jsx
import React from "react";

const MyComponent = ({ title }) => {
  return (
    <div className="my-component">
      <h1>{title}</h1>
      <p>This is JSX!</p>
    </div>
  );
};

export default MyComponent;
```

### JSX with State

```jsx
import React, { useState } from "react";

const Counter = () => {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
};
```

### Conditional Rendering

```jsx
const ConditionalComponent = ({ isVisible }) => {
  return (
    <div>
      {isVisible && <p>This is visible!</p>}
      {isVisible ? <p>Shown</p> : <p>Hidden</p>}
    </div>
  );
};
```

## 🎯 JSX Benefits

- **Declarative**: Describe what you want, not how to do it
- **Component-based**: Reusable, modular code
- **Type-safe**: Better development experience with TypeScript
- **Performance**: Optimized rendering with React
- **Developer Experience**: Better tooling and debugging

## 📚 Learn More

- [React Documentation](https://reactjs.org/)
- [JSX Introduction](https://reactjs.org/docs/introducing-jsx.html)
- [React Hooks](https://reactjs.org/docs/hooks-intro.html)
- [Component Props](https://reactjs.org/docs/components-and-props.html)
