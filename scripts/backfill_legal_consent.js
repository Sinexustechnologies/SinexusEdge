require('dotenv').config();
const mongoose = require('mongoose');
const User = require('../models/User');

const backfillConsent = async () => {
    try {
        const mongoUri = process.env.MONGODB_URI;
        if (!mongoUri) {
            console.error('❌ MONGODB_URI not found in environment.');
            process.exit(1);
        }
        await mongoose.connect(mongoUri);
        console.log('✅ Connected to MongoDB.');

        const now = new Date();
        const result = await User.updateMany(
            { $or: [{ termsAccepted: { $ne: true } }, { termsAccepted: { $exists: false } }] },
            {
                $set: {
                    termsAccepted: true,
                    termsAcceptedAt: now,
                    termsVersion: 'legacy-backfill',
                    privacyAccepted: true,
                    privacyAcceptedAt: now
                }
            }
        );

        console.log(`🎉 Migration backfill completed successfully. Updated ${result.modifiedCount} user records.`);
        process.exit(0);
    } catch (err) {
        console.error('❌ Migration failed:', err);
        process.exit(1);
    }
};

backfillConsent();
