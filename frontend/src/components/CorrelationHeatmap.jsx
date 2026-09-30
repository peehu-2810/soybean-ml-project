import React, { useState } from 'react';

const CORRELATION_MATRIX = {
  features: ["Ca", "Na", "SO4", "NO3-N", "P", "Alkalinity", "TDS", "Mn", "Uptake"],
  matrix: [
    [ 1.00,  0.42,  0.68,  0.31, -0.12,  0.54,  0.78,  0.25,  0.45],
    [ 0.42,  1.00,  0.35,  0.48,  0.05,  0.38,  0.62,  0.18,  0.38],
    [ 0.68,  0.35,  1.00,  0.22, -0.08,  0.46,  0.71,  0.30,  0.52],
    [ 0.31,  0.48,  0.22,  1.00,  0.25,  0.29,  0.55,  0.12,  0.64],
    [-0.12,  0.05, -0.08,  0.25,  1.00,  0.15,  0.32, -0.05,  0.72],
    [ 0.54,  0.38,  0.46,  0.29,  0.15,  1.00,  0.81,  0.40,  0.58],
    [ 0.78,  0.62,  0.71,  0.55,  0.32,  0.81,  1.00,  0.38,  0.84],
    [ 0.25,  0.18,  0.30,  0.12, -0.05,  0.40,  0.38,  1.00,  0.79],
    [ 0.45,  0.38,  0.52,  0.64,  0.72,  0.58,  0.84,  0.79,  1.00]
  ]
};

export default function CorrelationHeatmap() {
  const [hoveredCell, setHoveredCell] = useState(null);

  const getCellColor = (val) => {
    if (val === 1.0) return 'rgba(140, 198, 63, 0.4)';
    if (val > 0.6) return 'rgba(140, 198, 63, 0.75)';
    if (val > 0.3) return 'rgba(140, 198, 63, 0.45)';
    if (val >= 0) return 'rgba(140, 198, 63, 0.2)';
    return 'rgba(217, 119, 6, 0.4)'; // Negative correlation amber
  };

  return (
    <section className="dark-panel">
      <div className="lighter-green-subheading">CHEMICAL CORRELATION MATRIX</div>
      <h3 style={{ fontFamily: 'var(--font-heading)', color: '#ffffff', marginBottom: '0.5rem', fontSize: '1.25rem' }}>
        Pearson Feature Correlation Heatmap Grid
      </h3>
      <p style={{ color: '#c4d4c0', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
        Bivariate correlation coefficients ($r$) quantifying pairwise relationships between hydroponic ionic concentrations and Soybean Water Uptake.
      </p>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ borderCollapse: 'separate', borderSpacing: '4px', margin: '0 auto', fontSize: '0.82rem' }}>
          <thead>
            <tr>
              <th style={{ padding: '8px', color: 'var(--color-light-green-subheading)', fontFamily: 'var(--font-heading)' }}></th>
              {CORRELATION_MATRIX.features.map(f => (
                <th key={f} style={{ padding: '8px 10px', color: 'var(--color-vibrant-green)', fontFamily: 'var(--font-heading)', textAlign: 'center' }}>
                  {f}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {CORRELATION_MATRIX.features.map((rowFeat, rIdx) => (
              <tr key={rowFeat}>
                <th style={{ padding: '8px 12px', color: 'var(--color-vibrant-green)', fontFamily: 'var(--font-heading)', textAlign: 'right' }}>
                  {rowFeat}
                </th>
                {CORRELATION_MATRIX.features.map((colFeat, cIdx) => {
                  const val = CORRELATION_MATRIX.matrix[rIdx][cIdx];
                  const isHovered = hoveredCell && hoveredCell.r === rIdx && hoveredCell.c === cIdx;

                  return (
                    <td
                      key={`${rowFeat}-${colFeat}`}
                      onMouseEnter={() => setHoveredCell({ r: rIdx, c: cIdx, rowFeat, colFeat, val })}
                      onMouseLeave={() => setHoveredCell(null)}
                      style={{
                        backgroundColor: getCellColor(val),
                        color: '#ffffff',
                        fontFamily: 'var(--font-heading)',
                        fontWeight: '700',
                        textAlign: 'center',
                        padding: '10px 12px',
                        borderRadius: '6px',
                        border: isHovered ? '1.5px solid #ffffff' : '1px solid rgba(56, 89, 47, 0.4)',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease'
                      }}
                    >
                      {val.toFixed(2)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {hoveredCell && (
        <div style={{ marginTop: '1rem', padding: '0.75rem 1rem', background: '#142410', borderRadius: '8px', border: '1px solid var(--border-green)', fontSize: '0.85rem' }}>
          <strong style={{ color: 'var(--color-vibrant-green)' }}>{hoveredCell.rowFeat}</strong> ↔ <strong style={{ color: 'var(--color-vibrant-green)' }}>{hoveredCell.colFeat}</strong> :
          <span style={{ marginLeft: '0.5rem', color: '#ffffff' }}>Pearson Correlation coefficient r = <strong>{hoveredCell.val.toFixed(2)}</strong></span>
        </div>
      )}
    </section>
  );
}
