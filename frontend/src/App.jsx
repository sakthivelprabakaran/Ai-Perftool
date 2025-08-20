import React, { useState } from 'react';
import axios from 'axios';
import {
  Container, Typography, TextField, Button, Box,
  FormControl, FormLabel, RadioGroup, FormControlLabel, Radio,
  CircularProgress, Alert
} from '@mui/material';

function App() {
  const [url, setUrl] = useState('http://books.toscrape.com/');
  const [format, setFormat] = useState('jmeter');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleGenerate = async () => {
    setLoading(true);
    setError('');
    setResult(null);

    try {
      // Updated to point to the FastAPI server's port
      const response = await axios.post('http://localhost:8000/api/analyze', {
        url,
        format,
      });
      setResult(response.data);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'An unexpected error occurred.';
      const errorDetails = err.response?.data?.details || '';
      setError(`${errorMessage} ${errorDetails}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        AI-Powered Performance Test Case Generator
      </Typography>

      <Box component="form" noValidate autoComplete="off" sx={{ mt: 3 }}>
        <TextField
          fullWidth
          label="Web Application URL"
          variant="outlined"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          sx={{ mb: 2 }}
        />

        <FormControl component="fieldset" sx={{ mb: 2 }}>
          <FormLabel component="legend">Output Format</FormLabel>
          <RadioGroup
            row
            aria-label="format"
            name="format"
            value={format}
            onChange={(e) => setFormat(e.target.value)}
          >
            <FormControlLabel value="jmeter" control={<Radio />} label="JMeter (.jmx)" />
            <FormControlLabel value="loadrunner" control={<Radio />} label="LoadRunner (script)" />
          </RadioGroup>
        </FormControl>

        <Box sx={{ position: 'relative' }}>
          <Button
            variant="contained"
            size="large"
            onClick={handleGenerate}
            disabled={!url || loading}
            fullWidth
          >
            Generate Script
          </Button>
          {loading && (
            <CircularProgress
              size={24}
              sx={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                marginTop: '-12px',
                marginLeft: '-12px',
              }}
            />
          )}
        </Box>
      </Box>

      {result && (
        <Alert severity="success" sx={{ mt: 3 }}>
          <strong>{result.message}</strong>
          <br />
          File saved to: {result.outputFile}
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mt: 3 }}>
          {error}
        </Alert>
      )}
    </Container>
  );
}

export default App;
