import React from 'react';

export default function FooterStats() {
  return (
    <footer className="footer-stats-banner">
      <div className="stat-item">
        <div className="stat-number">1000+</div>
        <div className="stat-desc">Hydroponic Data Points</div>
      </div>
      <div className="stat-item">
        <div className="stat-number">10+</div>
        <div className="stat-desc">Years Agronomic Research</div>
      </div>
      <div className="stat-item">
        <div className="stat-number">3</div>
        <div className="stat-desc">Nutrient ML Pipelines</div>
      </div>
      <div className="stat-item">
        <div className="stat-number">98.5%</div>
        <div className="stat-desc">Baseline Train R² Score</div>
      </div>
    </footer>
  );
}
