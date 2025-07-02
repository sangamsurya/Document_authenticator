import React, { useState, useRef } from "react";
import shortid from "shortid";
import "./Sender.css";

export const Sender = () => {
  return (
    <div>
      <App />
    </div>
  );
};


const App = () => {
  const [imageFile, setImageFile] = useState(null);
  const [audioFile, setAudioFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const imageInputRef = useRef(null);
  const audioInputRef = useRef(null);

  const filesizes = (bytes, decimals = 2) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
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
      setImageFile(file);
      setError(null);
    }
  };

  const handleAudioChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.type.match(/audio\/wav/)) {
        setError('Audio must be WAV format');
        return;
      }
      setAudioFile(file);
      setError(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!imageFile || !audioFile) {
      setError('Please select both image and audio files');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('audio', audioFile);

    try {
      const response = await fetch('http://localhost:5000/embed', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        if (response.status === 0) {
          throw new Error('Failed to connect to server. Please make sure the server is running.');
        }
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to embed audio');
      }

      const data = await response.json();
      console.log('Backend response data:', data);
      setResult(data);
      setSuccess(true);
    } catch (error) {
      console.error('Error:', error);
      if (error.message.includes('Failed to fetch')) {
        setError('Failed to connect to server. Please make sure the server is running at http://localhost:5000');
      } else {
        setError(error.message || 'Error embedding audio');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSuccessClose = () => {
    setImageFile(null);
    setAudioFile(null);
    setResult(null);
    setSuccess(false);
    if (imageInputRef.current) imageInputRef.current.value = "";
    if (audioInputRef.current) audioInputRef.current.value = "";
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
                    <h6>Embed Audio in Image</h6>
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
                      <label>Select Image (PNG/JPG)</label>
                      <input
                        type="file"
                        accept="image/png,image/jpeg"
                        onChange={handleImageChange}
                        ref={imageInputRef}
                      />
                    </div>
                    {imageFile && (
                      <div className="file-preview">
                        <p>Selected: {imageFile.name} ({filesizes(imageFile.size)})</p>
                      </div>
                    )}
                  </div>

                  <div className="upload-section">
                    <div className="file-upload-box">
                      <label>Select Audio (WAV)</label>
                      <input
                        type="file"
                        accept="audio/wav"
                        onChange={handleAudioChange}
                        ref={audioInputRef}
                      />
                    </div>
                    {audioFile && (
                      <div className="file-preview">
                        <p>Selected: {audioFile.name} ({filesizes(audioFile.size)})</p>
                      </div>
                    )}
                  </div>

                  <div className="kb-buttons-box mt-3">
                    <button 
                      type="submit" 
                      className="btn btn-primary form-submit"
                      disabled={loading}
                    >
                      {loading ? 'Processing...' : 'Embed Audio'}
                    </button>
                  </div>
                </form>

                {/* Success Modal */}
                {success && (
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
                        onClick={handleSuccessClose}
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
                      <div style={{ fontSize: '1.2rem', color: '#388e3c', marginBottom: '8px', fontWeight: 600 }}>
                        Audio embedded successfully!
                      </div>
                    </div>
                  </div>
                )}

                {result && result.stego_image && (
                  <div className="result-section mt-4">
                    <h6>Result</h6>
                    <div className="stego-image">
                      <img 
                        src={`data:image/png;base64,${result.stego_image}`} 
                        alt="Stego Image" 
                        className="img-fluid"
                      />
                    </div>
                    <div className="mt-3">
                      <a 
                        href={`data:image/png;base64,${result.stego_image}`}
                        download="stego_image.png"
                        className="btn btn-success"
                      >
                        Download Stego Image
                      </a>
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
