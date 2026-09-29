import React, { useState } from 'react';

export default function ModelBenchmarks({ resultsData }) {
  const [activeNutrientTab, setActiveNutrientTab] = useState('K');

  const nutrientsData = resultsData.nutrients || {};
  const currentNutrientData = nutrientsData[activeNutrientTab] || {};
  const modelsMap = currentNutrientData.models || {};
  const selectedModel = currentNutrientData.selected_prototype_model || 'SVR';

  return (
    <section className="dark-panel">
      <div className="lighter-green-subheading">BENCHMARK PERFORMANCE & MODEL COMPARISON</div>
      <p style={{ color: '#c4d4c0', marginBottom: '1.5rem', fontSize: '0.95rem' }}>
        Quantitative regression evaluation across Random Forest, Support Vector Regressor (SVR), and K-Nearest Neighbors evaluated on holdout 80/20 chronological DAP split.
      </p>

      {/* Metric Tabs */}
      <div className="tabs-header" style={{ marginBottom: '1.25rem' }}>
        {['K', 'Mg', 'N'].map((nut) => (
          <button
            key={nut}
            className={`tab-button ${activeNutrientTab === nut ? 'active' : ''}`}
            onClick={() => setActiveNutrientTab(nut)}
            style={{ padding: '0.4rem 1.25rem', fontSize: '0.85rem' }}
          >
            {nut} MODELS
          </button>
        ))}
      </div>

      <div className="custom-table-container">
        <table className="custom-table">
          <thead>
            <tr>
              <th>ALGORITHM</th>
              <th>STATUS</th>
              <th>TRAIN R²</th>
              <th>TEST R²</th>
              <th>TEST RMSE</th>
              <th>TEST MAE</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(modelsMap).map(([modelName, metrics]) => {
              const isProduction = modelName === selectedModel;

              return (
                <tr key={modelName}>
                  <td style={{ fontWeight: '600' }}>{modelName}</td>
                  <td>
                    {isProduction && (
                      <span className="badge-production">PRODUCTION CHOICE</span>
                    )}
                  </td>
                  <td>{(metrics["Train R2"] || 0).toFixed(4)}</td>
                  <td style={{ color: isProduction ? 'var(--color-vibrant-green)' : 'inherit', fontWeight: isProduction ? '700' : '400' }}>
                    {(metrics["Test R2"] || 0).toFixed(4)}
                  </td>
                  <td>{(metrics["Test RMSE"] || 0).toFixed(4)}</td>
                  <td>{(metrics["Test MAE"] || 0).toFixed(4)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: '1rem', fontSize: '0.8rem', color: 'var(--color-light-green-subheading)' }}>
        Support Vector Regressor (SVR) selected for production due to superior holdout generalization and zero overfitting on time-series DAP split.
      </div>
    </section>
  );
}
