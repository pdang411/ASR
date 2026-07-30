// Minimal CI/CD service
const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => {
  res.json({ 
    status: 'healthy',
    service: 'ARS CI/CD Bootstrap',
    message: 'CI/CD service is running'
  });
});

app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

app.listen(port, '0.0.0.0', () => {
  console.log(`ARS CI/CD service listening at http://0.0.0.0:${port}`);
});