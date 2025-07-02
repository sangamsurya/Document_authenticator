import React from "react";
import "./ProjectContributor.css"; // Import a CSS file for styling

export const ProjectContributor = () => {
  const mentor = {
    name: "Dr. Sudipta Roy",
    image: "/sudipta_mam.jpg",
    description: "Project Mentor & Guide",
    designation: "Assistant Professor, Department of Information Technology",
    socials: {
      linkedin: "https://www.linkedin.com/in/sudipta-roy-1255203b/"
    }
  };

  const contributors = [
    {
      name: "Surya Sangam",
      image: "/surya.jpg",
      description: "Full Stack Developer. Loves React and Python.",
      socials: {
        github: "https://github.com/sangamsurya",
        linkedin: "https://linkedin.com/in/sangamsurya"
      }
    },
    {
      name: "Shreya Gupta",
      image: "/shreya.jpg",
      description: "UI/UX Designer. Passionate about user experience.",
      socials: {
        github: "https://github.com/ShreyaGupta1234",
        linkedin: "https://www.linkedin.com/in/shreya-gupta-378513240/"
      }
    },
    {
      name: "Sumit Sashmal",
      image: "/sumit.jpg",
      description: "Backend Engineer. API and database specialist.",
      socials: {
        github: "https://github.com/sumitsashmal",
        linkedin: "https://www.linkedin.com/in/sumit-sasmal-272559256/"
      }
    },
    {
      name: "Anshika Das",
      image: "/Anshika.jpg",
      description: "QA Lead. Ensures quality and reliability.",
      socials: {
        github: "https://github.com/anshikadas",
        linkedin: "https://www.linkedin.com/in/anshika-das-958170236/"
      }
    }
  ];

  return (
    <div className="contributor-container" style={{ maxWidth: 900, margin: '0 auto', padding: 32 }}>
      {/* Mentor Section */}
      <div style={{ marginBottom: 48 }}>
        <h1 style={{ textAlign: 'center', marginBottom: 32 }}>Project Mentor</h1>
        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <div style={{ textAlign: 'center', width: 280, background: '#f8f9fa', borderRadius: 12, padding: 24, boxShadow: '0 2px 8px rgba(0,0,0,0.07)' }}>
            <img
              src={mentor.image}
              alt={mentor.name}
              style={{ width: 150, height: 150, borderRadius: '50%', objectFit: 'cover', marginBottom: 16, border: '3px solid #4caf50' }}
            />
            <div style={{ fontWeight: 600, fontSize: 24 }}>{mentor.name}</div>
            <div style={{ fontSize: 16, color: '#555', marginTop: 8 }}>{mentor.designation}</div>
            <div style={{ fontSize: 14, color: '#666', marginTop: 8 }}>{mentor.description}</div>
            <div style={{ marginTop: 16 }}>
              {mentor.socials && (
                <a href={mentor.socials.linkedin} target="_blank" rel="noopener noreferrer" style={{ margin: '0 8px', color: '#0077b5', fontSize: 24 }}>
                  <i className="fab fa-linkedin"></i>
                </a>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Contributors Section */}
      <h1 style={{ textAlign: 'center', marginBottom: 32 }}>Project Contributors</h1>
      <div style={{ display: 'flex', justifyContent: 'space-around', flexWrap: 'wrap', gap: 32 }}>
        {contributors.map((contrib, idx) => (
          <div key={idx} style={{ textAlign: 'center', width: 180, background: '#f8f9fa', borderRadius: 12, padding: 20, boxShadow: '0 2px 8px rgba(0,0,0,0.07)' }}>
            <img
              src={contrib.image}
              alt={contrib.name}
              style={{ width: 100, height: 100, borderRadius: '50%', objectFit: 'cover', marginBottom: 16, border: '3px solid #4caf50' }}
            />
            <div style={{ fontWeight: 600, fontSize: 18 }}>{contrib.name}</div>
            <div style={{ fontSize: 14, color: '#555', marginTop: 8 }}>{contrib.description}</div>
            <div style={{ marginTop: 12 }}>
              {contrib.socials && (
                <>
                  <a href={contrib.socials.github} target="_blank" rel="noopener noreferrer" style={{ margin: '0 8px', color: '#333', fontSize: 22 }}>
                    <i className="fab fa-github"></i>
                  </a>
                  <a href={contrib.socials.linkedin} target="_blank" rel="noopener noreferrer" style={{ margin: '0 8px', color: '#0077b5', fontSize: 22 }}>
                    <i className="fab fa-linkedin"></i>
                  </a>
                </>
              )}
            </div>
          </div>
        ))}
      </div>

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
      {/* ... rest of the existing code ... */}
    </div>
  );
};
