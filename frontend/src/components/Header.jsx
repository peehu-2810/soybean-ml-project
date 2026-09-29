import React from 'react';
import { ArrowDown } from 'lucide-react';

export default function Header() {
  const scrollToCalculator = () => {
    const calc = document.getElementById('calculator-section');
    if (calc) calc.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <header>
      {/* Top Navigation Bar */}
      <div className="header-nav">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div className="brand-logo-circle">
            <img src="/soybean-logo.jpg" alt="Soybean Plant Logo" className="brand-logo-img" />
          </div>
          <div>
            <div className="brand-title-right" style={{ textAlign: 'left' }}>SOYBEAN INTELLIGENCE</div>
            <div className="lighter-green-subheading" style={{ fontSize: '0.7rem', marginBottom: 0 }}>HYDROPONIC ML ANALYTICS PLATFORM</div>
          </div>
        </div>
      </div>

      {/* Clean 1px accent line */}
      <div className="header-line"></div>

      {/* Main Hero Banner Container */}
      <div className="hero-container">
        <div className="hero-content-flex">
          <div className="hero-text-side">
            <h1 className="hero-title">
              HARNESSING DATA<br />FOR A SUSTAINABLE<br />
              <span className="hero-title-highlight">YIELD</span>
            </h1>
            <p className="hero-subtitle">
              We seek innovation in eco-friendly farming techniques, hydroponic water-nutrient balancing, and ML-driven yield prediction.
            </p>
            <div style={{ marginTop: '1.75rem' }}>
              <button className="pill-outline-btn" onClick={scrollToCalculator}>
                Discover Pipeline
              </button>
            </div>
          </div>
        </div>

        {/* Downward Connector Line with Arrow matching screenshot */}
        <div className="hero-down-connector">
          <button className="down-arrow-circle" onClick={scrollToCalculator} aria-label="Scroll down">
            <ArrowDown size={16} />
          </button>
        </div>
      </div>
    </header>
  );
}
