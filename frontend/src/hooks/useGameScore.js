import { useCallback } from "react";
import useApi from "./useApi";

const useGameScore = () => {
  const { loading, error, data, makeRequest, reset } = useApi();

  const saveScore = useCallback(
    async (gameName, score, playerName = "Anónimo") => {
      try {
        const result = await makeRequest("http://localhost:8000/save-score", {
          method: "POST",
          body: JSON.stringify({
            game: gameName,
            score,
            player: playerName,
            timestamp: new Date().toISOString(),
          }),
        });

        return result;
      } catch (err) {
        throw err;
      }
    },
    [makeRequest]
  );

  const getTopScores = useCallback(
    async (gameName, limit = 10) => {
      try {
        const result = await makeRequest(
          `http://localhost:8000/top-scores?game=${gameName}&limit=${limit}`
        );
        return result;
      } catch (err) {
        throw err;
      }
    },
    [makeRequest]
  );

  const getPlayerScores = useCallback(
    async (playerName) => {
      try {
        const result = await makeRequest(
          `http://localhost:8000/player-scores?player=${playerName}`
        );
        return result;
      } catch (err) {
        throw err;
      }
    },
    [makeRequest]
  );

  return {
    loading,
    error,
    data,
    saveScore,
    getTopScores,
    getPlayerScores,
    reset,
  };
};

export default useGameScore;
