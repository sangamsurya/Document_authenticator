import React, { useState, useRef } from "react";
import shortid from "shortid";
import "./Receiver.css";

export const Receiver = () => {
  return (
    <div>
      <App />
    </div>
  );
};

const App = () => {
  const [stegoImage, setStegoImage] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showMatchModal, setShowMatchModal] = useState(false);
  const imageInputRef = useRef(null);

  const filesizes = (bytes, decimals = 2) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.type.match(/image\/(png|jpeg|jpg)/)) {
        setError('Image must be PNG or JPG format');
        return;
      }
      setStegoImage(file);
      setError(null);
      setResult(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!stegoImage) {
      setError('Please select a stego image');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('image', stegoImage);

    try {
      const response = await fetch('http://localhost:5000/extract', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        if (response.status === 0) {
          throw new Error('Failed to connect to server. Please make sure the server is running.');
        }
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to extract audio');
      }

      const data = await response.json();
      setResult(data);
      if (data.match_result !== undefined) {
        setShowMatchModal(true);
      }
    } catch (error) {
      console.error('Error:', error);
      if (error.message.includes('Failed to fetch')) {
        setError('Failed to connect to server. Please make sure the server is running at http://localhost:5000');
      } else {
        setError(error.message || 'Error extracting audio');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleMatchModalClose = () => {
    setShowMatchModal(false);
    setResult(null);
    setStegoImage(null);
    if (imageInputRef.current) imageInputRef.current.value = "";
  };

  return (
    <div className="fileupload-view">
      <div className="row justify-content-center m-0">
        <div className="col-md-8">
          <div className="card mt-5">
            <div className="card-body">
              <div className="kb-data-box">
                <div className="kb-modal-data-title">
                  <div className="kb-data-title">
                    <h6>Extract Audio from Image</h6>
                  </div>
                </div>
                {error && (
                  <div className="alert alert-danger" role="alert">
                    {error}
                  </div>
                )}
                <form onSubmit={handleSubmit}>
                  <div className="upload-section">
                    <div className="file-upload-box">
                      <label>Select Stego Image</label>
                      <input
                        type="file"
                        accept="image/png,image/jpeg"
                        onChange={handleImageChange}
                        ref={imageInputRef}
                      />
                    </div>
                    {stegoImage && (
                      <div className="file-preview">
                        <p>Selected: {stegoImage.name} ({filesizes(stegoImage.size)})</p>
                      </div>
                    )}
                  </div>

                  <div className="kb-buttons-box mt-3">
                    <button 
                      type="submit" 
                      className="btn btn-primary form-submit"
                      disabled={loading}
                    >
                      {loading ? 'Processing...' : 'Extract Audio'}
                    </button>
                  </div>
                </form>

                {result && (
                  <div className="result-section mt-4">
                    <h6>Result</h6>
                    {result.extracted_audio && (
                      <div className="audio-player">
                        <h6>Extracted Audio:</h6>
                        <audio 
                          controls 
                          src={`data:audio/wav;base64,${result.extracted_audio}`}
                          className="w-100"
                        />
                        <div className="mt-3">
                          <a 
                            href={`data:audio/wav;base64,${result.extracted_audio}`}
                            download="extracted_audio.wav"
                            className="btn btn-success"
                          >
                            Download Audio
                          </a>
                        </div>
                      </div>
                    )}
                    {result.match_result !== undefined && (
                      <div className="match-result mt-3">
                        <h6>Match Result:</h6>
                        <p className={result.match_result ? 'text-success' : 'text-danger'}>
                          {result.match_result ? `Match Found (${result.match_result.toFixed(2)}%)` : 'No Match'}
                        </p>
                      </div>
                    )}
                  </div>
                )}

                {/* Match Result Modal */}
                {showMatchModal && result && result.match_result !== undefined && (
                  <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    width: '100vw',
                    height: '100vh',
                    background: 'rgba(0,0,0,0.4)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 9999
                  }}>
                    <div style={{
                      background: '#fff',
                      borderRadius: '8px',
                      padding: '32px 24px',
                      boxShadow: '0 4px 24px rgba(0,0,0,0.15)',
                      minWidth: '320px',
                      textAlign: 'center',
                      position: 'relative'
                    }}>
                      <button
                        onClick={handleMatchModalClose}
                        style={{
                          position: 'absolute',
                          top: 12,
                          right: 16,
                          background: 'none',
                          border: 'none',
                          fontSize: '1.5rem',
                          color: '#888',
                          cursor: 'pointer'
                        }}
                        aria-label="Close"
                      >
                        &times;
                      </button>
                      <div style={{ fontSize: '1.2rem', color: result.match_result ? '#388e3c' : '#c62828', marginBottom: '8px', fontWeight: 600 }}>
                        {result.match_result ? `Match Found (${result.match_result.toFixed(2)}%)` : 'No Match'}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

