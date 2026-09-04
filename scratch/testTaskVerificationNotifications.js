require("dotenv").config();
const mongoose = require("mongoose");
const User = require("../models/User");
const Device = require("../models/Device");
const Alert = require("../models/Alert");
const Task = require("../models/Task");
const Notification = require("../models/Notification");
const notificationService = require("../services/notificationService");

async function runTest() {
    try {
        console.log("🔄 Connecting to MongoDB...");
        await mongoose.connect(process.env.MONGO_URI || "mongodb://localhost:27017/sensordb");
        console.log("✅ DB Connected");

        // 1. Create/find Admin
        let admin = await User.findOne({ role: "admin", email: "test_admin_verify@example.com" });
        if (!admin) {
            admin = await User.create({
                userId: "ADM_V01",
                role: "admin",
                name: "Test Admin Verifier",
                email: "test_admin_verify@example.com",
                mobile: "9999999001",
                password: "hashedpassword123"
            });
        }

        // 2. Create/find Staff
        let staff = await User.findOne({ role: "staff", email: "test_staff_verify@example.com" });
        if (!staff) {
            staff = await User.create({
                userId: "STF_V01",
                role: "staff",
                name: "Test Staff Verifier",
                email: "test_staff_verify@example.com",
                mobile: "8888888001",
                empId: "EMPV01",
                password: "hashedpassword123",
                fcmToken: "mock_fcm_token_staff_verify_123"
            });
        }

        // 3. Create/find Device
        let device = await Device.findOne({ device_uid: "DEV_VERIFY_TEST_01" });
        if (!device) {
            device = await Device.create({
                device_uid: "DEV_VERIFY_TEST_01",
                deviceId: "TestLoc-V1",
                adminId: admin._id,
                assignedStaff: staff._id,
                location: "Test Restroom Block V",
                floor: "2nd Floor"
            });
        }

        // 4. Create Alert & Task
        const alert = await Alert.create({
            device: device._id,
            device_uid: device.device_uid,
            deviceId: device.deviceId,
            alertType: "CRITICAL_FEEDBACK",
            status: "OPEN",
            assignedStaff: staff._id
        });

        const task = await Task.create({
            taskName: "Clean Restroom Block V",
            alert: alert._id,
            device: device._id,
            staff: staff._id,
            status: "SUBMITTED",
            submittedAt: new Date()
        });

        console.log(`🚀 Triggering sendTaskVerifiedNotification for task ${task._id}...`);
        await notificationService.sendTaskVerifiedNotification(task, staff, admin, device);

        // 5. Verify Notification created in DB
        const createdNotifications = await Notification.find({ recipient: staff._id, type: "TASK_VERIFIED" })
            .sort({ createdAt: -1 })
            .limit(5);

        console.log(`\n📊 --- TEST RESULTS ---`);
        console.log(`Found ${createdNotifications.length} TASK_VERIFIED notifications for staff:`);
        createdNotifications.forEach((n, idx) => {
            console.log(`\nNotification #${idx + 1}:`);
            console.log(`- ID: ${n._id}`);
            console.log(`- Recipient: ${n.recipient}`);
            console.log(`- Type: ${n.type}`);
            console.log(`- Title: ${n.title}`);
            console.log(`- Message: ${n.message}`);
            console.log(`- Read: ${n.read}`);
        });

        if (createdNotifications.length > 0) {
            console.log("\n✅ Test Passed: Notification record created successfully!");
        } else {
            console.log("\n❌ Test Failed: No notification record created.");
        }

        // Cleanup test data
        await Notification.deleteMany({ recipient: staff._id });
        await Task.findByIdAndDelete(task._id);
        await Alert.findByIdAndDelete(alert._id);

        process.exit(0);
    } catch (err) {
        console.error("❌ Test error:", err);
        process.exit(1);
    }
}

runTest();
