const functions = require('firebase-functions');
const express = require('express');
const cors = require('cors')({origin: true});
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();

app.use(cors);

const apiProxy = createProxyMiddleware('/api', {
   target: 'http://127.0.0.1:5000',
   changeOrigin: true,
});
app.use('/api', apiProxy);

exports.flaskApp = functions.https.onRequest(app);
