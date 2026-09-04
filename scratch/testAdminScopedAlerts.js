const mongoose = require("mongoose");
const Device = require("../models/Device");
const Alert = require("../models/Alert");
const Task = require("../models/Task");
const { getAlerts } = require("../controllers/alertController");

console.log("==========================================");
console.log("🧪 UNIT TESTING getAlerts ADMIN DEVICE SCOPING");
console.log("==========================================");

function createMockRes() {
    let statusCode = 200;
    let jsonData = null;
    return {
        status: function(code) {
            statusCode = code;
            return this;
        },
        json: function(data) {
            jsonData = data;
            return data;
        },
        getData: function() { return jsonData; },
        getCode: function() { return statusCode; }
    };
}

async function runTests() {
    // 1. Mock Device.find to simulate Admin A having 0 devices
    Device.find = function(query) {
        console.log("📱 Device.find query received:", JSON.stringify(query));
        return {
            populate: function() {
                return {
                    select: function() {
                        return {
                            lean: async function() {
                                // Return empty array for admin with 0 devices
                                if (query.$or && query.$or.some(q => q.adminId === "admin_with_no_devices")) {
                                    return [];
                                }
                                // Return 1 device for admin_with_1_device
                                if (query.$or && query.$or.some(q => q.adminId === "admin_with_1_device")) {
                                    return [{
                                        _id: new mongoose.Types.ObjectId("60d5ec123456789012345601"),
                                        device_uid: "DEV_ADMIN_1",
                                        deviceId: "DEV_ADMIN_1",
                                        location: "Terminal A",
                                        floor: "1",
                                        adminId: "admin_with_1_device"
                                    }];
                                }
                                return [];
                            }
                        };
                    }
                };
            }
        };
    };

    // 2. Mock Alert.find
    Alert.find = function(query) {
        console.log("🚨 Alert.find query received:", JSON.stringify(query));
        return {
            sort: function() {
                return {
                    lean: async function() {
                        return [{
                            _id: new mongoose.Types.ObjectId("60d5ec123456789012345701"),
                            device_uid: "DEV_ADMIN_1",
                            deviceId: "DEV_ADMIN_1",
                            alertCategory: "Critical",
                            alertType: "CRITICAL",
                            status: "OPEN"
                        }];
                    }
                };
            }
        };
    };

    // 3. Mock Task.find
    Task.find = function() {
        return {
            populate: function() {
                return {
                    populate: function() {
                        return {
                            sort: function() {
                                return {
                                    lean: async function() { return []; }
                                };
                            }
                        };
                    }
                };
            }
        };
    };

    // --- TEST 1: Admin with 0 devices ---
    console.log("\n--- TEST 1: Admin with 0 devices ---");
    const req1 = { user: { id: "admin_with_no_devices", role: "admin" }, query: {} };
    const res1 = createMockRes();
    await getAlerts(req1, res1);
    const data1 = res1.getData();
    console.log("Result 1:", JSON.stringify(data1));

    if (data1 && data1.success === true && data1.count === 0 && data1.alerts.length === 0) {
        console.log("✅ TEST 1 PASSED: Admin with 0 devices returned 0 alerts.");
    } else {
        console.error("❌ TEST 1 FAILED!");
        process.exit(1);
    }

    // --- TEST 2: Admin with 1 device ---
    console.log("\n--- TEST 2: Admin with 1 device ---");
    const req2 = { user: { id: "admin_with_1_device", role: "admin" }, query: {} };
    const res2 = createMockRes();
    await getAlerts(req2, res2);
    const data2 = res2.getData();
    console.log("Result 2:", JSON.stringify(data2));

    if (data2 && data2.success === true && data2.count === 1 && data2.alerts[0].device_uid === "DEV_ADMIN_1") {
        console.log("✅ TEST 2 PASSED: Admin with 1 device returned only their own device alert.");
    } else {
        console.error("❌ TEST 2 FAILED!");
        process.exit(1);
    }

    console.log("\n🎉 ALL TESTS PASSED SUCCESSFULLY!");
}

runTests().catch(err => {
    console.error("Test execution error:", err);
    process.exit(1);
});
