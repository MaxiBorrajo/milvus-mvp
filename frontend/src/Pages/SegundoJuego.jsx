import { useState } from "react";
import Header from "../Components/Header";
import useAlterSearch from "../hooks/useAlterSearch";

const SegundoJuego = () => {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [isUploaded, setIsUploaded] = useState(false);

  const { loading, error, searchEgo } = useAlterSearch();

  const searchAlter = async () => {
    if (!file) {
      alert("No cargaste una imagen, vas a enojar al antiguo!");
    }
    try {
      setResult(null);
      const response = await searchEgo(file);
      setResult(response.data);
    } catch (err) {
      console.error("Error en searchAlter:", err, error);
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setFile(file);
    if (file) {
      setIsUploaded(true);
    } else {
      setIsUploaded(false);
    }
  };

  return (
    <div className="game-container">
      <Header title="Segundo Ritual" />

      <div className="game-content">
        <h1>🕮 Segundo Ritual</h1>
        <p>¡Encontrá tu alter ego espiritual!</p>

        <div className="game-instructions">
          <h3>Indicaciones:</h3>
          <ul>
            <li>Elegi una foto tuya</li>
            <li>Tirala al abismo para iniciar el ritual</li>
            <li>¡Pierde la cordura al ver la respuesta!</li>
          </ul>
        </div>

        <div className="file-upload-container home-container">
          <h2>Sube tu foto...</h2>
          <div className="input-group">
            <label htmlFor="file-upload">Selecciona un archivo</label>
            <input
              type="file"
              id="file-upload"
              className="file-input"
              disabled={loading}
              onChange={(e) => handleFileChange(e)}
            />
          </div>
        </div>

        {isUploaded && (
          <button
            className="game-start-btn"
            onClick={searchAlter}
            onKeyDown={(e) => e.key === "Enter" && searchAlter}
            disabled={loading}
          >
            Consultar al abismo...
          </button>
        )}

        {result && (
          <div className="result-section">
            <h3>Tu par:</h3>
            <div className="games-grid">
              <div className="result-card" key={result.index}>
                <img
                  src={result.url}
                  style={{
                    maxWidth: "100%",
                    borderRadius: "10px",
                    border: "1px solid rgba(255, 255, 255, 0.2)",
                  }}
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SegundoJuego;
