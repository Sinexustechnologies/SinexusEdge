const rateLimit = require("express-rate-limit");

// Custom Key Generator: Key by User JWT Token if authenticated, else IP
const keyGenerator = (req) => {
    const authHeader = req.headers.authorization;
    if (authHeader && authHeader.startsWith("Bearer ")) {
        return authHeader.split(" ")[1]; // Unique key per logged-in user session
    }
    // Fall back to client IP (handling X-Forwarded-For if behind proxy)
    return req.ip || req.headers["x-forwarded-for"] || req.socket.remoteAddress || "unknown-ip";
};

// General limiter for APIs (e.g. 3000 requests per 15 minutes per user/IP)
const apiLimiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: process.env.RATE_LIMIT_MAX ? parseInt(process.env.RATE_LIMIT_MAX) : 3000,
    keyGenerator: keyGenerator,
    message: {
        success: false,
        message: "Too many requests from this device/IP, please try again after a few minutes"
    },
    standardHeaders: true,
    legacyHeaders: false,
    skip: (req) => {
        // Skip rate limiting for health check endpoint
        return req.path === "/" || req.path === "/health" || req.path === "/api/health";
    }
});

// Stricter limiter for Auth/Login routes (100 attempts per 15 minutes)
const authLimiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 100,
    keyGenerator: keyGenerator,
    message: {
        success: false,
        message: "Too many login attempts from this device/IP, please try again after a few minutes"
    },
    standardHeaders: true,
    legacyHeaders: false,
});

// Stricter limiter for OTP generation routes (50 requests per 15 minutes)
const otpLimiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 50,
    keyGenerator: keyGenerator,
    message: {
        success: false,
        message: "Too many OTP requests from this device/IP, please try again after a few minutes"
    },
    standardHeaders: true,
    legacyHeaders: false,
});

module.exports = {
    apiLimiter,
    authLimiter,
    otpLimiter
};

