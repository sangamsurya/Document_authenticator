import React, { useState, useRef } from 'react';
import axios from 'axios';
import { Box, Button, Typography, Paper, CircularProgress, Alert, Tabs, Tab } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import MicIcon from '@mui/icons-material/Mic';
import StopIcon from '@mui/icons-material/Stop';
import './VoiceChecker.css';

const VoiceChecker = () => {
    const [file1, setFile1] = useState(null);
    const [file2, setFile2] = useState(null);
    const [isRecording, setIsRecording] = useState(false);
    const [recordedAudio, setRecordedAudio] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [secondAudioTab, setSecondAudioTab] = useState(0);

    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];

            mediaRecorder.ondataavailable = (event) => {
                audioChunksRef.current.push(event.data);
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
                const audioUrl = URL.createObjectURL(audioBlob);
                setRecordedAudio({ blob: audioBlob, url: audioUrl });
            };

            mediaRecorder.start();
            setIsRecording(true);
        } catch (err) {
            setError('Error accessing microphone: ' + err.message);
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
            setIsRecording(false);
        }
    };

    const handleFileUpload = async () => {
        if (!file1 || (!file2 && !recordedAudio)) {
            setError('Please select both audio files or record audio for comparison');
            return;
        }

        setLoading(true);
        setError(null);
        setResult(null);

        const formData = new FormData();
        formData.append('audio1', file1);
        
        if (file2) {
            formData.append('audio2', file2);
        } else {
            formData.append('audio2', recordedAudio.blob, 'recording.wav');
        }

        try {
            const response = await axios.post('http://localhost:5000/compare_audio', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            console.log('API Response:', response.data); // Debug log

            // Validate and process the response data
            if (!response.data) {
                throw new Error('No data received from server');
            }

            // Ensure all required fields are present
            const processedData = {
                ...response.data,
                feature_similarities: response.data.feature_similarities || {},
                feature_differences: response.data.feature_differences || {},
                feature_thresholds: response.data.feature_thresholds || {},
                overall_similarity: response.data.overall_similarity || 0,
                is_same_speaker: response.data.is_same_speaker || false,
                spectrum_plot: response.data.spectrum_plot || null
            };

            console.log('Processed Data:', processedData); // Debug log
            setResult(processedData);
        } catch (err) {
            console.error('Error in handleFileUpload:', err); // Debug log
            setError(err.response?.data?.message || 'Error comparing audio files');
            setResult(null);
        } finally {
            setLoading(false);
        }
    };

    const handleTabChange = (event, newValue) => {
        setSecondAudioTab(newValue);
        // Clear the other input when switching tabs
        if (newValue === 0) {
            setRecordedAudio(null);
        } else {
            setFile2(null);
        }
    };

    return (
        <Box className="audio-comparison">
            <Typography variant="h4" gutterBottom>
                Voice Comparison
            </Typography>
            
            {/* File Upload Section */}
            <Paper className="file-upload" sx={{ maxWidth: 500, mx: 'auto', mt: 4, mb: 4, p: 3 }}>
                {/* First Audio File */}
                <Box className="upload-group">
                    <Typography variant="subtitle1" gutterBottom>First Audio File:</Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
                        <Button
                            variant="contained"
                            component="label"
                            startIcon={<CloudUploadIcon />}
                            size="large"
                            sx={{
                                px: 7,
                                py: 1.5,
                                fontSize: '1rem',
                                borderRadius: '4px',
                                boxShadow: 1,
                                textTransform: 'none',
                            }}
                        >
                            Upload File
                            <input
                                type="file"
                                hidden
                                accept=".wav,.mp3,.webm,.ogg,.m4a"
                                onChange={(e) => {
                                    setFile1(e.target.files[0]);
                                    setError(null);
                                    setResult(null);
                                }}
                            />
                        </Button>
                    </Box>
                    {file1 && (
                        <Typography variant="body2" color="textSecondary" align="center">
                            Selected: {file1.name}
                        </Typography>
                    )}
                </Box>

                {/* Second Audio Section */}
                <Box className="upload-group">
                    <Typography variant="subtitle1" gutterBottom>Second Audio:</Typography>
                    <Tabs value={secondAudioTab} onChange={handleTabChange} centered sx={{ mb: 2 }}>
                        <Tab label="Upload File" />
                        <Tab label="Record Audio" />
                    </Tabs>

                    {secondAudioTab === 0 ? (
                        // Upload File Tab
                        <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
                            <Button
                                variant="contained"
                                component="label"
                                startIcon={<CloudUploadIcon />}
                                size="large"
                                sx={{
                                    px: 7,
                                    py: 1.5,
                                    fontSize: '1rem',
                                    borderRadius: '4px',
                                    boxShadow: 1,
                                    textTransform: 'none',
                                }}
                            >
                                Upload File
                                <input
                                    type="file"
                                    hidden
                                    accept=".wav,.mp3,.webm,.ogg,.m4a"
                                    onChange={(e) => {
                                        setFile2(e.target.files[0]);
                                        setError(null);
                                        setResult(null);
                                    }}
                                />
                            </Button>
                        </Box>
                    ) : (
                        // Record Audio Tab
                        <Box sx={{ textAlign: 'center' }}>
                            <Button
                                variant="contained"
                                color={isRecording ? "error" : "primary"}
                                onClick={isRecording ? stopRecording : startRecording}
                                startIcon={isRecording ? <StopIcon /> : <MicIcon />}
                                sx={{ mb: 2 }}
                            >
                                {isRecording ? 'Stop Recording' : 'Start Recording'}
                            </Button>
                        </Box>
                    )}

                    {/* Display selected file or recorded audio */}
                    {file2 && secondAudioTab === 0 && (
                        <Typography variant="body2" color="textSecondary" align="center">
                            Selected: {file2.name}
                        </Typography>
                    )}
                    {recordedAudio && secondAudioTab === 1 && (
                        <Box sx={{ mt: 2 }}>
                            <Typography variant="body2">Recorded audio:</Typography>
                            <audio controls src={recordedAudio.url} />
                        </Box>
                    )}
                </Box>

                <Button
                    variant="contained"
                    color="primary"
                    onClick={handleFileUpload}
                    disabled={loading || !file1 || (!file2 && !recordedAudio)}
                    sx={{ mt: 2 }}
                >
                    {loading ? <CircularProgress size={24} /> : 'Compare Audio Files'}
                </Button>
            </Paper>

            {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                </Alert>
            )}

            {loading && (
                <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
                    <CircularProgress />
                </Box>
            )}

            {result && (
                <Box className="results" sx={{ mt: 4 }}>
                    {/* Debug info - remove in production */}
                    <pre style={{ display: 'none' }}>
                        {JSON.stringify(result, null, 2)}
                    </pre>

                    {/* Main Scores */}
                    <Box className="main-scores">
                        <Paper className="score-card">
                            <Typography variant="h6">Overall Similarity</Typography>
                            <Typography variant="h3" className="score" sx={{ 
                                color: result.overall_similarity >= 80 ? '#4caf50' : 
                                       result.overall_similarity >= 60 ? '#ff9800' : '#f44336'
                            }}>
                                {result.overall_similarity.toFixed(2)}%
                            </Typography>
                        </Paper>
                        <Paper className="score-card">
                            <Typography variant="h6">Voice Match Result</Typography>
                            <Typography variant="h3" className="score" sx={{ 
                                color: result.is_same_speaker ? '#4caf50' : '#f44336'
                            }}>
                                {result.is_same_speaker ? 'Match' : 'No Match'}
                            </Typography>
                        </Paper>
                    </Box>

                    {/* Feature Analysis */}
                    <Paper className="features-section" sx={{ mt: 4 }}>
                        <Typography variant="h6" gutterBottom>
                            {result.is_same_speaker ? 'Feature Similarities' : 'Feature Differences'}
                        </Typography>
                        <Box className="features-grid">
                            {Object.entries(result.is_same_speaker ? 
                                result.feature_similarities : 
                                result.feature_differences
                            ).map(([feature, value]) => (
                                <Box key={feature} className="feature">
                                    <Typography variant="body1" className="feature-name">
                                        {feature.replace('_', ' ').toUpperCase()}
                                    </Typography>
                                    <Box className="progress-bar">
                                        <Box 
                                            className="progress" 
                                            sx={{ 
                                                width: `${result.is_same_speaker ? value : (value * 100)}%`,
                                                backgroundColor: result.is_same_speaker ? 
                                                    (value >= 80 ? '#4caf50' : value >= 60 ? '#ff9800' : '#f44336') :
                                                    (value <= result.feature_thresholds[feature] ? '#4caf50' : '#f44336')
                                            }}
                                        />
                                    </Box>
                                    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                                        <Typography variant="body2" className="feature-score">
                                            {result.is_same_speaker ? 
                                                `${value.toFixed(2)}%` : 
                                                value.toFixed(4)}
                                        </Typography>
                                        <Typography variant="caption" color="textSecondary">
                                            Threshold: {result.feature_thresholds[feature]}
                                        </Typography>
                                    </Box>
                                </Box>
                            ))}
                        </Box>
                    </Paper>

                    {/* Spectrum Visualization */}
                    {result.spectrum_plot && (
                        <Paper className="spectrum-section" sx={{ mt: 4 }}>
                            <Typography variant="h6" gutterBottom>Spectrum Comparison</Typography>
                            <Box className="spectrum-plot">
                                <img 
                                    src={`data:image/png;base64,${result.spectrum_plot}`}
                                    alt="Audio Spectrum Comparison"
                                    onError={(e) => {
                                        console.error('Error loading spectrum plot:', e); // Debug log
                                        e.target.style.display = 'none';
                                        setError('Error loading spectrum visualization');
                                    }}
                                />
                            </Box>
                        </Paper>
                    )}
                </Box>
            )}
        </Box>
    );
};

export default VoiceChecker;