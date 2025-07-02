import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./Home.css";

export const Home = () => {
  const navigate = useNavigate();
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  const images = [
    "/1.bmp",
    "/2.png",
    "/3.png"
    
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImageIndex((prevIndex) => 
        prevIndex === images.length - 1 ? 0 : prevIndex + 1
      );
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const handleStartAuth = () => {
    navigate('/sender');
  };

  return (
    <div className="home-container">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1>Secure Document Authentication</h1>
          <p className="hero-subtitle">
            Advanced audio steganography technology for secure document verification
          </p>
          <div className="image-carousel">
            {images.map((image, index) => (
              <img
                key={index}
                src={image}
                alt={`Security Feature ${index + 1}`}
                className={`carousel-image ${index === currentImageIndex ? 'active' : ''}`}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <h2>Advanced Security Features</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🎵</div>
            <h3>Audio Steganography</h3>
            <p>Embed voice recordings within images for covert authentication</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🔒</div>
            <h3>Voice Biometrics</h3>
            <p>Advanced voice fingerprinting for secure verification</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Multi-factor Authentication</h3>
            <p>Combine image and voice verification for enhanced security</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🔍</div>
            <h3>Advanced Analysis</h3>
            <p>MFCC and spectral analysis for precise voice matching</p>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works">
        <h2>How It Works</h2>
        <div className="steps-container">
          <div className="step">
            <div className="step-number">1</div>
            <h3>Upload Document</h3>
            <p>Upload your document for authentication</p>
          </div>
          <div className="step">
            <div className="step-number">2</div>
            <h3>Record Voice</h3>
            <p>Provide voice sample for verification</p>
          </div>
          <div className="step">
            <div className="step-number">3</div>
            <h3>Process</h3>
            <p>System analyzes and verifies authenticity</p>
          </div>
          <div className="step">
            <div className="step-number">4</div>
            <h3>Get Results</h3>
            <p>Receive detailed verification report</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-content">
          <h2>Ready to Secure Your Documents?</h2>
          <p>Start using our advanced authentication system today</p>
          <button className="cta-button" onClick={handleStartAuth}>
            Start Authentication
          </button>
        </div>
      </section>

      {/* Contact Us Section */}
      <section className="contact-section">
        <div className="contact-content">
          <h2>Contact Us</h2>
          <div className="contact-grid">
            <div className="contact-info">
              <h3>Get in Touch</h3>
              <p>Have questions? We'd love to hear from you.</p>
              <div className="contact-details">
                <div className="contact-item">
                  <i className="fas fa-envelope"></i>
                  <span>support@documentauth.com</span>
                </div>
                <div className="contact-item">
                  <i className="fas fa-phone"></i>
                  <span>+1 (555) 123-4567</span>
                </div>
                <div className="contact-item">
                  <i className="fas fa-map-marker-alt"></i>
                  <span>Vip Road, Kaikhali Kolkata</span>
                </div>
              </div>
            </div>
            <div className="contact-form">
              <form>
                <div className="form-group">
                  <input type="text" placeholder="Your Name" required />
                </div>
                <div className="form-group">
                  <input type="email" placeholder="Your Email" required />
                </div>
                <div className="form-group">
                  <textarea placeholder="Your Message" rows="4" required></textarea>
                </div>
                <button type="submit" className="submit-button">Send Message</button>
              </form>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="home-footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4>Document Authenticator</h4>
            <p>Advanced security through audio steganography</p>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2025 Document Authenticator. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};
