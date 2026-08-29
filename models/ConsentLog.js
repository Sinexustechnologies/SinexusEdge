const mongoose = require("mongoose");

const consentLogSchema = new mongoose.Schema(
{
    userId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: "User",
        required: true
    },
    userType: {
        type: String,
        enum: ["admin", "staff"],
        default: "admin"
    },
    termsVersion: {
        type: String,
        required: true
    },
    termsAcceptedAt: {
        type: Date,
        default: Date.now
    },
    privacyAcceptedAt: {
        type: Date,
        default: Date.now
    },
    ipAddress: {
        type: String,
        default: null
    },
    userAgent: {
        type: String,
        default: null
    }
},
{
    timestamps: true
});

module.exports = mongoose.model("ConsentLog", consentLogSchema);
