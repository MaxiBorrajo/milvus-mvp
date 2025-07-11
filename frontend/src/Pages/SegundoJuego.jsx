import { useState } from "react";
import Header from "../Components/Header";
import useAlterSearch from "../hooks/useAlterSearch";
import { Link } from "react-router-dom";

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
      console.log(response, "Response");
      setResult(response);
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

      <div className="game-content libertinus-font">
        <h1>⚔️ Segundo Ritual</h1>
        <p>La guerra entre ángeles y demonios se avecina...</p>

        <div className="game-instructions great-primer-sc">
          <h3>Indicaciones:</h3>
          <ul>
            <li>Elegí una foto tuya</li>
            <li>Lanzala al abismo para revelar tu verdadera esencia</li>
            <li>Descubrí a qué bando pertenecés… y encontrá a tus similares para la batalla</li>
          </ul>
        </div>

        <div className="file-upload-container home-container great-primer-sc">
          <h2>Sube una foto...</h2>
          <div className="input-group">
            <label htmlFor="file-upload">Selecciona un archivo</label>
            <input
              type="file"
              id="file-upload"
              className="file-input great-primer-sc"
              disabled={loading}
              onChange={(e) => handleFileChange(e)}
            />
          </div>
        </div>

        {isUploaded && (
          <button
            className="game-start-btn great-primer-sc"
            onClick={searchAlter}
            onKeyDown={(e) => e.key === "Enter" && searchAlter}
            disabled={loading}
          >
            Consultar al abismo...
          </button>
        )}
        <>
          <div className="result-section">
            <h3>Tu legión:</h3>
          </div>
          {result && (
            <div className="results-images-container">
              {result.map((r) => (
                <div className="result-image-card" key={r.index}>
                  <img
                    src={r.url}
                    alt="Result"
                    style={{
                      maxWidth: "100%",
                      borderRadius: "10px",
                      border: "1px solid rgba(255, 255, 255, 0.2)",
                    }}
                  />
                </div>
              ))}
            </div>
          )}
        </>

        <Link to="/" className="back-btn">
          ← Volver al calabozo
        </Link>
      </div>
    </div>
  );
};

export default SegundoJuego;
