import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import "./App.css";
import Home from "./Pages/Home";
import PrimerJuego from "./Pages/PrimerJuego";
import SegundoJuego from "./Pages/SegundoJuego";
import TercerJuego from "./Pages/TercerJuego";
// Header component is used in individual pages

function App() {
  return (
    <Router>
      <div className="App">
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/primer-juego" element={<PrimerJuego />} />
            <Route path="/segundo-juego" element={<SegundoJuego />} />
            <Route path="/tercer-juego" element={<TercerJuego />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
