import React, { useState } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid
} from 'recharts';

export default function ModelBenchmarks({ resultsData }) {
  const [activeNutrientTab, setActiveNutrientTab] = useState('K');

  const nutrientsData = resultsData.nutrients || {};
  const currentNutrientData = nutrientsData[activeNutrientTab] || {};
  const modelsMap = currentNutrientData.models || {};
  const selectedModel = currentNutrientData.selected_prototype_model || 'SVR';

  // Format dataset for Recharts bar chart
  const chartData = Object.entries(modelsMap).map(([mName, metrics]) => ({
    name: mName,
    'Train R²': Number((metrics['Train R2'] || 0).toFixed(3)),
    'Test R²': Number(Math.max(0, metrics['Test R2'] || 0).toFixed(3)),
    'Test RMSE': Number((metrics['Test RMSE'] || 0).toFixed(2))
  }));

  return (
    <section className="dark-panel">
      <div className="lighter-green-subheading">BENCHMARK PERFORMANCE & MODEL COMPARISON (PAPER FIG. 4)</div>
      <h3 style={{ fontFamily: 'var(--font-heading)', color: '#ffffff', marginBottom: '0.5rem', fontSize: '1.25rem' }}>
        Model Accuracy ($R^2$) & Error Metrics Comparison
      </h3>
      <p style={{ color: '#c4d4c0', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
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

      {/* Model Benchmark Visual Bar Chart */}
      <div style={{ width: '100%', height: 260, marginBottom: '2rem' }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#38592f" opacity={0.4} />
            <XAxis dataKey="name" stroke="#8aa384" tick={{ fill: '#ffffff', fontSize: 13, fontFamily: 'var(--font-heading)' }} />
            <YAxis stroke="#8aa384" tick={{ fill: '#8aa384', fontSize: 12 }} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1b3317',
                borderColor: '#38592f',
                borderRadius: '8px',
                color: '#ffffff',
                fontFamily: 'var(--font-heading)'
              }}
            />
            <Legend wrapperStyle={{ fontFamily: 'var(--font-heading)', fontSize: '12px' }} />
            <Bar dataKey="Train R²" fill="#7ea373" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Test R²" fill="#8cc63f" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Test RMSE" fill="#e5e0d1" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Data Table */}
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
