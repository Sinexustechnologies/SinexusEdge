const rateLimit = require("express-rate-limit");

// General limiter for APIs (e.g. 100 requests per 10 minutes)
const apiLimiter = rateLimit({
    windowMs: 10 * 60 * 1000,
    max: 100,
    message: {
        success: false,
        message: "Too many requests from this IP, please try again after 10 minutes"
    },
    standardHeaders: true,
    legacyHeaders: false,
});

// Stricter limiter for Auth/Login routes (10 attempts per 10 minutes)
const authLimiter = rateLimit({
    windowMs: 10 * 60 * 1000,
    max: 10,
    message: {
        success: false,
        message: "Too many login attempts from this IP, please try again after 10 minutes"
    },
    standardHeaders: true,
    legacyHeaders: false,
});

// Stricter limiter for OTP generation routes (15 requests per 10 minutes)
const otpLimiter = rateLimit({
    windowMs: 10 * 60 * 1000,
    max: 15,
    message: {
        success: false,
        message: "Too many OTP requests from this IP, please try again after 10 minutes"
    },
    standardHeaders: true,
    legacyHeaders: false,
});

module.exports = {
    apiLimiter,
    authLimiter,
    otpLimiter
};
