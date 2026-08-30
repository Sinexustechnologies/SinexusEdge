const mongoose = require("mongoose");
const Device = require("../models/Device");
const SensorData = require("../models/SensorData");
const LatestDeviceStatus = require("../models/LatestDeviceStatus");
const User = require("../models/User");
const Alert = require("../models/Alert");
const Task = require("../models/Task");
const ParticularRating = require("../models/ParticularRating");
const DailyRating = require("../models/DailyRating");
const Assignment = require("../models/Assignment");
const { calculateParticularRating, calculateParticularRatingDetails } = require("../services/ratingService");
const Settings = require("../models/Settings");
const { classifyTelemetry } = require("../services/alertClassifier");

// Date Range Validation (Max 1 Month = ~31 Days)
const parseAndValidateReportDateRange = (reqQuery) => {
    const { from, till, to, fromDate: qFrom, toDate: qTo } = reqQuery;
    const now = new Date();
    
    let rawFrom = from || qFrom;
    let rawTill = till || to || qTo;

    let fromDate = rawFrom ? new Date(rawFrom) : new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    let tillDate = rawTill ? new Date(rawTill) : new Date(now);

    if (isNaN(fromDate.getTime())) fromDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    if (isNaN(tillDate.getTime())) tillDate = new Date(now);

    if (typeof rawFrom === "string" && rawFrom.length === 10) {
        fromDate.setHours(0, 0, 0, 0);
    }
    if (typeof rawTill === "string" && rawTill.length === 10) {
        tillDate.setHours(23, 59, 59, 999);
    }

    if (fromDate > tillDate) {
        const temp = fromDate;
        fromDate = tillDate;
        tillDate = temp;
    }

    const diffMs = tillDate.getTime() - fromDate.getTime();
    const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays > 32) {
        return { error: "Report date range cannot exceed 1 month." };
    }

    return { fromDate, tillDate, diffDays };
};

// Admin Scoped Helper
const getReportUserInfo = async (userObj) => {
    let generatedBy = "Admin";
    let userId = "N/A";
    if (userObj && userObj.id) {
        const dbUser = await User.findById(userObj.id).lean();
        if (dbUser) {
            generatedBy = dbUser.name || dbUser.contactPerson || dbUser.companyName || dbUser.email || "Admin";
            if (dbUser.role === "admin") {
                userId = dbUser.userId || dbUser.empId || "N/A";
            } else if (dbUser.adminId) {
                const adminUser = await User.findById(dbUser.adminId).lean();
                userId = adminUser ? (adminUser.userId || adminUser.empId || "N/A") : (dbUser.userId || "N/A");
            } else {
                userId = dbUser.userId || dbUser.empId || "N/A";
            }
        } else {
            userId = userObj.id;
        }
    }
    return { generatedBy, userId };
};

const getAdminDeviceScope = async (userObj) => {
    let query = {};
    if (userObj && userObj.role === "staff") {
        const staffUser = await User.findById(userObj.id);
        const assignedDevId = staffUser ? staffUser.assignedDevice : null;
        query.$or = [
            { assignedStaff: userObj.id },
            ...(assignedDevId ? [{ _id: assignedDevId }] : [])
        ];
    } else if (userObj && userObj.id) {
        query.adminId = userObj.id;
    }
    const devices = await Device.find(query).populate("assignedStaff").lean();
    const deviceIds = devices.map(d => d._id);
    const deviceUids = devices.map(d => d.device_uid);
    return { devices, deviceIds, deviceUids };
};

// 1. Daily Report
const getDailyReport = async (req, res) => {
    try {
        const { devices, deviceIds, deviceUids } = await getAdminDeviceScope(req.user);
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const alerts = await Alert.countDocuments({
            device_uid: { $in: deviceUids },
            createdAt: { $gte: today }
        });

        const resolvedAlerts = await Alert.countDocuments({
            device_uid: { $in: deviceUids },
            status: "RESOLVED",
            createdAt: { $gte: today }
        });

        const tasks = await Task.countDocuments({
            device: { $in: deviceIds },
            createdAt: { $gte: today }
        });

        const completedTasks = await Task.countDocuments({
            device: { $in: deviceIds },
            status: { $in: ["VERIFIED", "COMPLETED", "RESOLVED"] },
            createdAt: { $gte: today }
        });

        res.status(200).json({
            success: true,
            report: {
                date: today,
                totalToilets: devices.length,
                alerts,
                resolvedAlerts,
                tasks,
                completedTasks
            }
        });
    } catch (error) {
        console.error(error);
        res.status(500).json({ success: false, message: "Server Error" });
    }
};

// 2. Weekly Report
const getWeeklyReport = async (req, res) => {
    try {
        const { deviceIds, deviceUids } = await getAdminDeviceScope(req.user);
        const start = new Date();
        start.setDate(start.getDate() - 7);

        const alerts = await Alert.countDocuments({
            device_uid: { $in: deviceUids },
            createdAt: { $gte: start }
        });

        const tasks = await Task.countDocuments({
            device: { $in: deviceIds },
            createdAt: { $gte: start }
        });

        const completed = await Task.countDocuments({
            device: { $in: deviceIds },
            status: { $in: ["VERIFIED", "COMPLETED", "RESOLVED"] },
            createdAt: { $gte: start }
        });

        res.status(200).json({
            success: true,
            report: { alerts, tasks, completed }
        });
    } catch (error) {
        console.error(error);
        res.status(500).json({ success: false, message: "Server Error" });
    }
};

// 3. Monthly Report
const getMonthlyReport = async (req, res) => {
    try {
        const { deviceIds, deviceUids } = await getAdminDeviceScope(req.user);
        const start = new Date();
        start.setMonth(start.getMonth() - 1);

        const alerts = await Alert.countDocuments({
            device_uid: { $in: deviceUids },
            createdAt: { $gte: start }
        });

        const tasks = await Task.countDocuments({
            device: { $in: deviceIds },
            createdAt: { $gte: start }
        });

        const completed = await Task.countDocuments({
            device: { $in: deviceIds },
            status: { $in: ["VERIFIED", "COMPLETED", "RESOLVED"] },
            createdAt: { $gte: start }
        });

        res.status(200).json({
            success: true,
            report: { alerts, tasks, completed }
        });
    } catch (error) {
        console.error(error);
        res.status(500).json({ success: false, message: "Server Error" });
    }
};

// 4. Report Stats
const getReportStats = async (req, res) => {
    try {
        const { devices, deviceIds, deviceUids } = await getAdminDeviceScope(req.user);

        const totalAlertsCount = await Alert.countDocuments({ device_uid: { $in: deviceUids } });
        const resolvedAlertsCount = await Alert.countDocuments({
            device_uid: { $in: deviceUids },
            status: "RESOLVED"
        });
        const resolvedTasksCount = await Task.countDocuments({
            device: { $in: deviceIds },
            status: { $in: ["VERIFIED", "COMPLETED", "RESOLVED"] }
        });

        const effectiveResolvedAlerts = Math.max(resolvedAlertsCount, resolvedTasksCount);
        const pendingAlerts = Math.max(0, totalAlertsCount - effectiveResolvedAlerts);

        const latestStatuses = await LatestDeviceStatus.find({ device_uid: { $in: deviceUids } }).lean();
        let sumRating = 0;
        let ratingCount = 0;
        for (const s of latestStatuses) {
            if (s.feedback !== undefined && s.feedback !== null) {
                sumRating += calculateParticularRating(s.Counter, s.OdorSensVal, s.feedback);
                ratingCount++;
            }
        }
        const avgRatingVal = ratingCount > 0 ? parseFloat((sumRating / ratingCount).toFixed(1)) : "N/A";

        const completedTasksList = await Task.find({
            device: { $in: deviceIds },
            status: { $in: ["COMPLETED", "VERIFIED", "RESOLVED"] }
        }).select("createdAt completedAt verifiedAt startedAt assignedAt").lean();

        let avgResponseStr = "N/A";
        if (completedTasksList.length > 0) {
            let totalDiffMs = 0;
            let validTaskCount = 0;
            for (const t of completedTasksList) {
                const startTime = t.assignedAt || t.startedAt || t.createdAt;
                const endTime = t.completedAt || t.verifiedAt;
                if (startTime && endTime) {
                    const diff = new Date(endTime) - new Date(startTime);
                    if (diff > 0) {
                        totalDiffMs += diff;
                        validTaskCount++;
                    }
                }
            }
            if (validTaskCount > 0) {
                const avgMinutes = Math.round(totalDiffMs / validTaskCount / (1000 * 60));
                avgResponseStr = avgMinutes + "m";
            }
        }

        const stats = {
            total_reports: devices.length,
            avg_rating: avgRatingVal,
            total_alerts: totalAlertsCount,
            resolved_alerts: effectiveResolvedAlerts,
            pending_alerts: pendingAlerts,
            avg_response_time: avgResponseStr
        };
        res.status(200).json(stats);
    } catch (error) {
        console.error("Error in getReportStats:", error);
        res.status(500).json({ success: false, message: "Server Error" });
    }
};

// 5. Reports List
const getReportsList = async (req, res) => {
    try {
        const { devices } = await getAdminDeviceScope(req.user);
        const reports = devices.map(d => ({
            id: "rep_" + d._id,
            title: (d.deviceId || d.device_uid || "Device") + " Performance Report",
            date: new Date().toISOString().split("T")[0],
            status: "ready",
            deviceId: d.deviceId || d.device_uid || "N/A",
            location: d.location || "N/A"
        }));
        res.status(200).json({ success: true, reports });
    } catch (error) {
        res.status(500).json({ success: false, message: "Server Error" });
    }
};

// 6. Generate Report trigger
const generateReport = async (req, res) => {
    try {
        res.status(200).json({ success: true, message: "Report generation completed" });
    } catch (error) {
        res.status(500).json({ success: false, message: "Server Error" });
    }
};

// Compile Report Dataset Function
const compileReportDataset = async (req) => {
    const dateRangeResult = parseAndValidateReportDateRange(req.query);
    if (dateRangeResult.error) {
        return { error: dateRangeResult.error };
    }
    const { fromDate, tillDate } = dateRangeResult;
    const { deviceId } = req.query;

    const formatDateStr = (d) => {
        if (!d) return "";
        const date = new Date(d);
        if (isNaN(date.getTime())) return String(d).split("T")[0];
        const parts = new Intl.DateTimeFormat("en-IN", { timeZone: "Asia/Kolkata", year: "numeric", month: "2-digit", day: "2-digit" }).formatToParts(date);
        const day = parts.find(p => p.type === "day").value;
        const month = parts.find(p => p.type === "month").value;
        const year = parts.find(p => p.type === "year").value;
        return `${year}-${month}-${day}`;
    };

    const formatTimeStr = (d) => {
        if (!d) return "N/A";
        const date = new Date(d);
        if (isNaN(date.getTime())) return "N/A";
        return date.toLocaleString("en-IN", {
            timeZone: "Asia/Kolkata",
            day: "2-digit",
            month: "short",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
            hour12: true
        });
    };

    const { generatedBy, userId } = await getReportUserInfo(req.user);
    const { devices: userDevices } = await getAdminDeviceScope(req.user);

    let targetDevices = userDevices;
    if (deviceId) {
        targetDevices = userDevices.filter(d => 
            d.deviceId === deviceId || d.device_uid === deviceId || d._id.toString() === deviceId
        );
    }

    if (targetDevices.length === 0) {
        return {
            fromDate,
            tillDate,
            reportSummary: {
                period: formatDateStr(fromDate) + " till " + formatDateStr(tillDate),
                adminName: generatedBy,
                adminId: userId,
                totalDevices: 0,
                totalRatings: 0,
                averageRating: "N/A",
                totalAlerts: 0,
                criticalAlerts: 0,
                needAttentionAlerts: 0,
                totalCleaningTasks: 0,
                completedCleaningTasks: 0,
                totalUpdations: 0
            },
            reports: []
        };
    }

    const deviceIds = targetDevices.map(d => d._id);
    const deviceUids = targetDevices.map(d => d.device_uid);
    const deviceCustomIds = targetDevices.map(d => d.deviceId).filter(Boolean);
    const allIdentifiers = Array.from(new Set([...deviceUids, ...deviceCustomIds]));

    const getNum = (obj, keys, defaultVal = null) => {
        if (!obj) return defaultVal;
        for (const k of keys) {
            if (obj[k] !== undefined && obj[k] !== null && obj[k] !== "" && !isNaN(Number(obj[k]))) {
                return Number(obj[k]);
            }
        }
        return defaultVal;
    };

    // Query DB strictly within selected date range
    const [allSensorLogs, allParticularRatings, allAlerts, allTasks, allLatestStatuses] = await Promise.all([
        SensorData.find({
            $or: [
                { device_uid: { $in: allIdentifiers } },
                { deviceId: { $in: allIdentifiers } },
                { device: { $in: deviceIds } }
            ],
            $or: [
                { createdAt: { $gte: fromDate, $lte: tillDate } },
                { timestamp: { $gte: fromDate, $lte: tillDate } }
            ]
        }).sort({ createdAt: -1, timestamp: -1 }).lean(),

        ParticularRating.find({
            $or: [
                { device_uid: { $in: allIdentifiers } },
                { deviceId: { $in: allIdentifiers } },
                { device: { $in: deviceIds } }
            ],
            $or: [
                { createdAt: { $gte: fromDate, $lte: tillDate } },
                { timestamp: { $gte: fromDate, $lte: tillDate } }
            ]
        }).sort({ createdAt: -1, timestamp: -1 }).lean(),

        Alert.find({
            $or: [
                { device_uid: { $in: allIdentifiers } },
                { deviceId: { $in: allIdentifiers } },
                { device: { $in: deviceIds } }
            ],
            createdAt: { $gte: fromDate, $lte: tillDate }
        }).sort({ createdAt: -1 }).lean(),

        Task.find({
            $or: [
                { device: { $in: deviceIds } },
                { device_uid: { $in: allIdentifiers } },
                { deviceId: { $in: allIdentifiers } }
            ],
            $or: [
                { createdAt: { $gte: fromDate, $lte: tillDate } },
                { assignedAt: { $gte: fromDate, $lte: tillDate } },
                { submittedAt: { $gte: fromDate, $lte: tillDate } }
            ]
        }).populate("staff assignedBy timeline.updatedBy").sort({ createdAt: -1 }).lean(),

        LatestDeviceStatus.find({
            $or: [
                { device_uid: { $in: allIdentifiers } },
                { deviceId: { $in: allIdentifiers } },
                { device: { $in: deviceIds } }
            ]
        }).lean()
    ]);

    // Aggregate summary for all target devices within date range
    let overallTotalRatings = allParticularRatings.length;
    let overallSumRating = allParticularRatings.reduce((acc, r) => {
        const val = getNum(r, ["particularRating", "rating"], null);
        return val !== null ? acc + val : acc;
    }, 0);
    let validRatingCount = allParticularRatings.filter(r => getNum(r, ["particularRating", "rating"], null) !== null).length;
    let overallAverageRating = validRatingCount > 0 ? `${parseFloat((overallSumRating / validRatingCount).toFixed(2))} / 5.0` : "N/A";

    let totalAlertsCount = allAlerts.length;
    let criticalAlertsCount = allAlerts.filter(a => (a.alertCategory || a.alertType || "").toLowerCase().includes("critical")).length;
    let needAttentionAlertsCount = allAlerts.filter(a => (a.alertCategory || a.alertType || "").toLowerCase().includes("attention")).length;

    let totalCleaningTasksCount = allTasks.length;
    let completedCleaningTasksCount = allTasks.filter(t => ["COMPLETED", "VERIFIED", "RESOLVED"].includes(t.status)).length;
    let totalUpdations = allTasks.reduce((acc, t) => acc + (t.updateCount || 1), 0);

    const reports = targetDevices.map(device => {
        const devUid = device.device_uid;
        const devCustomId = device.deviceId;
        const devId = device._id.toString();

        const isDevMatch = (item) => {
            if (!item) return false;
            if (item.device && item.device.toString() === devId) return true;
            if (item.device_uid && (item.device_uid === devUid || item.device_uid === devCustomId)) return true;
            if (item.deviceId && (item.deviceId === devUid || item.deviceId === devCustomId)) return true;
            return false;
        };

        const devLogs = allSensorLogs.filter(isDevMatch);
        const devParticularRatings = allParticularRatings.filter(isDevMatch);
        const devAlerts = allAlerts.filter(isDevMatch);
        const devTasks = allTasks.filter(isDevMatch);

        const latestDevStatus = allLatestStatuses.find(s => isDevMatch(s));

        // Key Telemetry Summary (24H vs Entire Period)
        const now = new Date();
        const twentyFourHoursAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);

        const logs24h = devLogs.filter(l => {
            const d = new Date(l.timestamp || l.createdAt);
            return !isNaN(d.getTime()) && d >= twentyFourHoursAgo;
        });

        const ratings24h = devParticularRatings.filter(r => {
            const d = new Date(r.timestamp || r.createdAt);
            return !isNaN(d.getTime()) && d >= twentyFourHoursAgo;
        });

        // 24H Telemetry Summary
        let avgRating24h = "N/A";
        if (ratings24h.length > 0) {
            const validRatings = ratings24h.map(r => getNum(r, ["particularRating", "rating"], null)).filter(v => v !== null);
            if (validRatings.length > 0) {
                const sum = validRatings.reduce((acc, v) => acc + v, 0);
                avgRating24h = `${parseFloat((sum / validRatings.length).toFixed(2))} / 5.0`;
            }
        }

        let avgOdor24h = "N/A";
        if (logs24h.length > 0) {
            const validOdors = logs24h.map(l => getNum(l, ["OdorSensVal", "odorValue", "OdorLevel", "odor"], null)).filter(v => v !== null);
            if (validOdors.length > 0) {
                const sum = validOdors.reduce((acc, v) => acc + v, 0);
                avgOdor24h = `${Math.round(sum / validOdors.length)} PPM`;
            }
        }

        let totalUsage24h = "N/A";
        if (logs24h.length > 0) {
            const counters = logs24h.map(l => getNum(l, ["Counter", "counterValue", "CounterValue", "counter"], null)).filter(v => v !== null);
            if (counters.length > 0) {
                const minC = Math.min(...counters);
                const maxC = Math.max(...counters);
                totalUsage24h = `${Math.max(0, maxC - minC)} Entries`;
            }
        }

        // Entire Period Telemetry Summary
        let periodAvgRating = "N/A";
        if (devParticularRatings.length > 0) {
            const validRatings = devParticularRatings.map(r => getNum(r, ["particularRating", "rating"], null)).filter(v => v !== null);
            if (validRatings.length > 0) {
                const sum = validRatings.reduce((acc, v) => acc + v, 0);
                periodAvgRating = `${parseFloat((sum / validRatings.length).toFixed(2))} / 5.0`;
            }
        }

        let periodAvgOdor = "N/A";
        if (devLogs.length > 0) {
            const validOdors = devLogs.map(l => getNum(l, ["OdorSensVal", "odorValue", "OdorLevel", "odor"], null)).filter(v => v !== null);
            if (validOdors.length > 0) {
                const sum = validOdors.reduce((acc, v) => acc + v, 0);
                periodAvgOdor = `${Math.round(sum / validOdors.length)} PPM`;
            }
        }

        let periodTotalUsage = "N/A";
        if (devLogs.length > 0) {
            const counters = devLogs.map(l => getNum(l, ["Counter", "counterValue", "CounterValue", "counter"], null)).filter(v => v !== null);
            if (counters.length > 0) {
                const minC = Math.min(...counters);
                const maxC = Math.max(...counters);
                periodTotalUsage = `${Math.max(0, maxC - minC)} Entries`;
            }
        }

        // Assigned Staff
        let assignedStaffStr = "N/A";
        if (device.assignedStaff) {
            const sName = device.assignedStaff.name || device.assignedStaff.contactPerson;
            const sEmp = device.assignedStaff.empId || device.assignedStaff.userId;
            if (sName && sEmp) assignedStaffStr = `${sName} (${sEmp})`;
            else if (sName) assignedStaffStr = sName;
        }

        // Last Cleaned Timestamp
        let lastCleanedTimestamp = "N/A";
        const completedTask = devTasks.find(t => ["VERIFIED", "COMPLETED", "RESOLVED"].includes(t.status) && (t.completedAt || t.verifiedAt || t.submittedAt));
        if (completedTask) {
            lastCleanedTimestamp = formatTimeStr(completedTask.completedAt || completedTask.verifiedAt || completedTask.submittedAt);
        } else if (latestDevStatus && (latestDevStatus.lastCleanedAt || latestDevStatus.updatedAt)) {
            lastCleanedTimestamp = formatTimeStr(latestDevStatus.lastCleanedAt || latestDevStatus.updatedAt);
        }

        // Daily Telemetry & Maintenance History Table
        const dateMap = new Map();
        let dIter1 = new Date(fromDate);
        const dEnd1 = new Date(tillDate);
        dIter1.setHours(0, 0, 0, 0);
        dEnd1.setHours(0, 0, 0, 0);
        while (dIter1 <= dEnd1) {
            const dStr = formatDateStr(dIter1);
            if (dStr && !dateMap.has(dStr)) {
                dateMap.set(dStr, { totalRatings: 0, sumPR: 0 });
            }
            dIter1.setDate(dIter1.getDate() + 1);
        }

        devParticularRatings.forEach(r => {
            const dateKey = r.date || formatDateStr(r.timestamp || r.createdAt);
            if (!dateKey || !dateMap.has(dateKey)) return;
            const pRating = getNum(r, ["particularRating", "rating"], null);
            if (pRating !== null) {
                const dayObj = dateMap.get(dateKey);
                dayObj.totalRatings++;
                dayObj.sumPR += pRating;
            }
        });

        const usageMap = new Map();
        devLogs.forEach(l => {
            const dateKey = l.date || formatDateStr(l.timestamp || l.createdAt);
            if (!dateKey) return;
            const cVal = getNum(l, ["Counter", "counterValue", "CounterValue", "counter"], null);
            if (cVal !== null) {
                if (!usageMap.has(dateKey)) {
                    usageMap.set(dateKey, { min: cVal, max: cVal });
                } else {
                    const uObj = usageMap.get(dateKey);
                    if (cVal < uObj.min) uObj.min = cVal;
                    if (cVal > uObj.max) uObj.max = cVal;
                }
            }
        });

        const dailyRatingTable = Array.from(dateMap.entries()).map(([dateStr, dObj]) => {
            const devDayLogs = devLogs.filter(l => (l.date || formatDateStr(l.timestamp || l.createdAt)) === dateStr);
            let dayOdorPpm = "N/A";
            if (devDayLogs.length > 0) {
                const odorVals = devDayLogs.map(l => getNum(l, ["OdorSensVal", "odorValue", "OdorLevel", "odor"], null)).filter(v => v !== null);
                if (odorVals.length > 0) {
                    const odorSum = odorVals.reduce((acc, v) => acc + v, 0);
                    dayOdorPpm = `${Math.round(odorSum / odorVals.length)} PPM`;
                }
            }

            const dayUsage = usageMap.get(dateStr);
            const usageCounter = dayUsage ? Math.max(0, dayUsage.max - dayUsage.min) : "N/A";

            const avgStar = dObj.totalRatings > 0 ? parseFloat((dObj.sumPR / dObj.totalRatings).toFixed(2)) : "N/A";

            const dayTasks = devTasks.filter(t => formatDateStr(t.createdAt || t.assignedAt || t.submittedAt) === dateStr && ["COMPLETED", "VERIFIED", "RESOLVED"].includes(t.status));

            return {
                date: dateStr,
                averageParticularRating: avgStar,
                odorPpm: dayOdorPpm,
                usageCounter,
                cleaningCount: dayTasks.length
            };
        });

        // Staff Cleaning Audit Trail
        const staffCleaningAuditTrail = [];
        devTasks.forEach(t => {
            const sName = t.staff ? (t.staff.name || t.staff.contactPerson) : (device.assignedStaff ? device.assignedStaff.name : "N/A");
            const sUserId = t.staff ? (t.staff.userId || t.staff._id?.toString()) : (device.assignedStaff ? device.assignedStaff.userId : "N/A");
            const sEmpId = t.staff ? (t.staff.empId || t.staff.userId) : (device.assignedStaff ? device.assignedStaff.empId : "N/A");
            const assignedTime = formatTimeStr(t.assignedAt || t.createdAt);
            const completionTime = formatTimeStr(t.completedAt || t.verifiedAt || t.submittedAt);
            
            staffCleaningAuditTrail.push({
                staffName: sName || "N/A",
                systemUserId: sUserId || "N/A",
                empId: sEmpId || "N/A",
                assignedTime,
                completionTime
            });
        });

        // Daily Task Submission & Admin Verification Summary
        const taskDateMap = new Map();
        let dIter2 = new Date(fromDate);
        const dEnd2 = new Date(tillDate);
        dIter2.setHours(0, 0, 0, 0);
        dEnd2.setHours(0, 0, 0, 0);
        while (dIter2 <= dEnd2) {
            const dStr = formatDateStr(dIter2);
            if (dStr && !taskDateMap.has(dStr)) {
                taskDateMap.set(dStr, []);
            }
            dIter2.setDate(dIter2.getDate() + 1);
        }

        devTasks.forEach(t => {
            const dateKey = formatDateStr(t.createdAt || t.assignedAt || t.submittedAt);
            if (dateKey && taskDateMap.has(dateKey)) {
                taskDateMap.get(dateKey).push(t);
            }
        });

        const dailyTaskSummary = Array.from(taskDateMap.entries()).map(([dateStr, tList]) => {
            const submitted = tList.filter(t => ["SUBMITTED", "VERIFIED", "COMPLETED", "RESOLVED"].includes(t.status)).length;
            const verified = tList.filter(t => ["VERIFIED", "RESOLVED"].includes(t.status)).length;
            const pending = tList.filter(t => ["ASSIGNED", "IN_PROGRESS", "SUBMITTED"].includes(t.status) && !["VERIFIED", "RESOLVED"].includes(t.status)).length;

            const staffCounts = {};
            tList.forEach(t => {
                const name = t.staff ? (t.staff.name || t.staff.contactPerson) : "N/A";
                staffCounts[name] = (staffCounts[name] || 0) + 1;
            });
            const staffBreakdownStr = Object.keys(staffCounts).length > 0 
                ? Object.entries(staffCounts).map(([s, c]) => `${s}: ${c} tasks`).join("; ")
                : "N/A";

            return {
                date: dateStr,
                submitted,
                verified,
                pending,
                staffBreakdown: staffBreakdownStr
            };
        });

        let totalStaffSubmittedTasks = 0;
        let totalAdminVerifiedTasks = 0;
        let totalRejectedTasks = 0;
        let pendingVerification = 0;

        devTasks.forEach(t => {
            if (["VERIFIED", "RESOLVED", "COMPLETED"].includes(t.status)) {
                totalAdminVerifiedTasks++;
            }
            if (["ASSIGNED", "IN_PROGRESS", "SUBMITTED"].includes(t.status) && !["VERIFIED", "RESOLVED", "COMPLETED"].includes(t.status)) {
                pendingVerification++;
            }

            // Count submissions & rejections from timeline attempts
            if (t.timeline && Array.isArray(t.timeline) && t.timeline.length > 0) {
                const subSteps = t.timeline.filter(step => step.status === "SUBMITTED").length;
                const rejSteps = t.timeline.filter(step => step.status === "REJECTED").length;
                totalStaffSubmittedTasks += subSteps > 0 ? subSteps : 1;
                totalRejectedTasks += rejSteps;
            } else {
                if (["SUBMITTED", "VERIFIED", "COMPLETED", "RESOLVED"].includes(t.status)) totalStaffSubmittedTasks++;
                if (t.status === "REJECTED") totalRejectedTasks++;
            }
        });

        // Alert & Task Lifecycle Timestamp Audit Trail with Rich Attempts & Rejection History
        const alertTaskAuditTrail = [];
        devAlerts.forEach(a => {
            const matchedTask = devTasks.find(t => t.alert && t.alert.toString() === a._id.toString());
            const cat = (a.alertCategory || a.alertType || "ALERT").toUpperCase();
            let titleDesc = a.description || a.title || "Alert Triggered";
            const updatesStr = `${a.updateCount || (matchedTask ? matchedTask.updateCount : 0) || 0} Updates`;

            let sName = "N/A";
            let startedTime = "N/A";
            let submittedTime = "N/A";
            let verifiedTime = "N/A";
            let rejectionReasonStr = "";
            let lifecycleTimeline = [];

            if (matchedTask) {
                if (matchedTask.staff) {
                    sName = `${matchedTask.staff.name || matchedTask.staff.contactPerson || 'Staff'} (${matchedTask.staff.empId || matchedTask.staff.userId || 'N/A'})`;
                }
                startedTime = formatTimeStr(matchedTask.startedAt);
                submittedTime = formatTimeStr(matchedTask.submittedAt);
                verifiedTime = formatTimeStr(matchedTask.verifiedAt || matchedTask.completedAt);

                // Build rich attempt & reassignment lifecycle details dynamically from DB
                if (matchedTask.timeline && Array.isArray(matchedTask.timeline) && matchedTask.timeline.length > 0) {
                    matchedTask.timeline.forEach(step => {
                        const stepTime = formatTimeStr(step.timestamp);
                        const notes = step.notes || "";
                        const attemptNum = step.attemptNumber || 1;

                        if (step.status === "REJECTED") {
                            rejectionReasonStr += `[Attempt ${attemptNum} Rejected @ ${stepTime}]: ${notes || 'Rejected by Admin'} | `;
                        } else if (step.status === "REASSIGNED") {
                            rejectionReasonStr += `[Reassigned @ ${stepTime}]: ${notes || 'Task Reassigned'} | `;
                        } else if (step.status === "VERIFIED" && notes) {
                            rejectionReasonStr += `[Verified @ ${stepTime}]: ${notes} | `;
                        }

                        lifecycleTimeline.push({
                            status: step.status,
                            timestamp: stepTime,
                            notes: notes,
                            attempt: attemptNum
                        });
                    });
                }
            }

            const finalStatusStr = matchedTask ? matchedTask.status : (a.status || "N/A");

            alertTaskAuditTrail.push({
                date: formatDateStr(a.createdAt),
                category: cat,
                title: titleDesc,
                created: formatTimeStr(a.createdAt),
                started: startedTime,
                submitted: submittedTime,
                verified: verifiedTime,
                staff: sName,
                updates: updatesStr,
                status: finalStatusStr,
                rejectionReason: rejectionReasonStr.trim() || "N/A",
                timeline: lifecycleTimeline
            });
        });

        devTasks.forEach(t => {
            if (!t.alert) {
                const devLocation = device.location || "N/A";
                const cat = "CLEANING TASK";
                const titleDesc = t.taskName || t.title || (devLocation !== "N/A" ? `Cleaning Task at ${devLocation}` : "Cleaning Task");
                const sName = t.staff ? `${t.staff.name || t.staff.contactPerson || 'Staff'} (${t.staff.empId || t.staff.userId || 'N/A'})` : "N/A";
                const updatesStr = `${t.updateCount || 0} Updates`;

                let rejectionReasonStr = "";
                let lifecycleTimeline = [];

                if (t.timeline && Array.isArray(t.timeline) && t.timeline.length > 0) {
                    t.timeline.forEach(step => {
                        const stepTime = formatTimeStr(step.timestamp);
                        const notes = step.notes || "";
                        const attemptNum = step.attemptNumber || 1;

                        if (step.status === "REJECTED") {
                            rejectionReasonStr += `[Attempt ${attemptNum} Rejected @ ${stepTime}]: ${notes || 'Rejected by Admin'} | `;
                        } else if (step.status === "REASSIGNED") {
                            rejectionReasonStr += `[Reassigned @ ${stepTime}]: ${notes || 'Task Reassigned'} | `;
                        } else if (step.status === "VERIFIED" && notes) {
                            rejectionReasonStr += `[Verified @ ${stepTime}]: ${notes} | `;
                        }

                        lifecycleTimeline.push({
                            status: step.status,
                            timestamp: stepTime,
                            notes: notes,
                            attempt: attemptNum
                        });
                    });
                }

                alertTaskAuditTrail.push({
                    date: formatDateStr(t.createdAt || t.assignedAt),
                    category: cat,
                    title: titleDesc,
                    created: formatTimeStr(t.createdAt || t.assignedAt),
                    started: formatTimeStr(t.startedAt),
                    submitted: formatTimeStr(t.submittedAt),
                    verified: formatTimeStr(t.verifiedAt || t.completedAt),
                    staff: sName,
                    updates: updatesStr,
                    status: t.status || "N/A",
                    rejectionReason: rejectionReasonStr.trim() || "N/A",
                    timeline: lifecycleTimeline
                });
            }
        });

        const devStatusStr = device.status || (latestDevStatus ? latestDevStatus.status : "N/A");

        return {
            deviceInfo: {
                id: devId,
                deviceId: devCustomId || devUid || "N/A",
                location: device.location || "N/A",
                status: devStatusStr
            },
            keyTelemetrySummary: {
                avgRating24h,
                avgOdor24h,
                totalUsage24h,
                periodAvgRating,
                periodAvgOdor,
                periodTotalUsage,
                assignedStaff: assignedStaffStr,
                lastCleaned: lastCleanedTimestamp
            },
            dailyRatingTable,
            staffCleaningAuditTrail,
            taskVerificationSummaryCounters: {
                submitted: totalStaffSubmittedTasks,
                verified: totalAdminVerifiedTasks,
                rejected: totalRejectedTasks,
                pending: pendingVerification
            },
            dailyTaskSummary,
            alertTaskAuditTrail
        };
    });

    const reportSummary = {
        period: formatDateStr(fromDate) + " till " + formatDateStr(tillDate),
        adminName: generatedBy,
        adminId: userId,
        totalDevices: targetDevices.length,
        totalRatings: overallTotalRatings,
        averageRating: overallAverageRating,
        totalAlerts: totalAlertsCount,
        criticalAlerts: criticalAlertsCount,
        needAttentionAlerts: needAttentionAlertsCount,
        totalCleaningTasks: totalCleaningTasksCount,
        completedCleaningTasks: completedCleaningTasksCount,
        totalUpdations
    };

    return {
        fromDate,
        tillDate,
        reportSummary,
        reports
    };
};

// 7. Comprehensive Device Reports API
const getDeviceReports = async (req, res) => {
    try {
        const dataset = await compileReportDataset(req);
        if (dataset.error) {
            return res.status(400).json({ success: false, message: dataset.error });
        }
        res.status(200).json({
            success: true,
            reportSummary: dataset.reportSummary,
            reports: dataset.reports
        });
    } catch (error) {
        console.error("Error in getDeviceReports:", error);
        res.status(500).json({ success: false, message: "Server Error" });
    }
};

// 8. Download Report CSV (Includes All 6 Operational Audit Sections)
const downloadReportCsv = async (req, res) => {
    try {
        const dataset = await compileReportDataset(req);
        const {
            incScope = "true",
            incTelemetrySummary = "true",
            incDailyTelemetry = "true",
            incStaffAudit = "true",
            incTaskSummary = "true",
            incAlertAudit = "true"
        } = req.query;

        const showScope = incScope !== "false";
        const showTelemetrySummary = incTelemetrySummary !== "false";
        const showDailyTelemetry = incDailyTelemetry !== "false";
        const showStaffAudit = incStaffAudit !== "false";
        const showTaskSummary = incTaskSummary !== "false";
        const showAlertAudit = incAlertAudit !== "false";
        if (dataset.error) {
            return res.status(400).json({ success: false, message: dataset.error });
        }
        const { reportSummary, reports } = dataset;
        const r = reports.length > 0 ? reports[0] : null;

        let csvRows = [];

        // Section 1: Scope
        csvRows.push(["=== REPORT DETAILS & SCOPE ==="]);
        csvRows.push(["Report Selected Period", reportSummary.period]);
        csvRows.push(["Generated By Admin", `${reportSummary.adminName} (ID: ${reportSummary.adminId})`]);
        csvRows.push(["Restroom / Device Unit", r ? `${r.deviceInfo.location} (ID: ${r.deviceInfo.deviceId})` : "N/A"]);
        csvRows.push(["Current Device Status", r ? r.deviceInfo.status : "N/A"]);
        csvRows.push(["Report Generated Time", new Date().toISOString()]);
        csvRows.push([]);

        // Section 2: Key Telemetry
        csvRows.push(["=== KEY TELEMETRY & OPERATIONAL SUMMARY ==="]);
        if (r) {
            csvRows.push(["24H Avg Rating", r.keyTelemetrySummary.avgRating24h]);
            csvRows.push(["24H Avg Odor", r.keyTelemetrySummary.avgOdor24h]);
            csvRows.push(["24H Total Usage", r.keyTelemetrySummary.totalUsage24h]);
            csvRows.push(["Period Avg Rating", r.keyTelemetrySummary.periodAvgRating]);
            csvRows.push(["Period Avg Odor", r.keyTelemetrySummary.periodAvgOdor]);
            csvRows.push(["Period Total Usage", r.keyTelemetrySummary.periodTotalUsage]);
            csvRows.push(["Assigned Staff Member", r.keyTelemetrySummary.assignedStaff]);
            csvRows.push(["Last Cleaned Timestamp", r.keyTelemetrySummary.lastCleaned]);
        }
        csvRows.push([]);

        // Section 3: Daily History
        csvRows.push(["=== DAILY TELEMETRY & MAINTENANCE HISTORY ==="]);
        csvRows.push(["Date", "Avg Star Rating", "Odor Level", "Usage Counter", "Cleaning Frequency"]);
        if (r && r.dailyRatingTable && r.dailyRatingTable.length > 0) {
            r.dailyRatingTable.forEach(d => {
                const starStr = d.averageParticularRating !== "N/A" ? `${d.averageParticularRating} / 5.0` : "N/A";
                const odorStr = d.odorPpm !== "N/A" ? d.odorPpm : "N/A";
                const usageStr = d.usageCounter !== "N/A" ? d.usageCounter : "N/A";
                csvRows.push([d.date, starStr, odorStr, usageStr, `${d.cleaningCount} Times`]);
            });
        } else {
            csvRows.push(["No telemetry or rating data recorded for the selected period"]);
        }
        csvRows.push([]);

        // Section 4: Staff Audit Trail
        csvRows.push(["=== STAFF CLEANING AUDIT TRAIL ==="]);
        csvRows.push(["Staff Name", "System User ID", "Emp ID", "Assigned Time", "Completion Time"]);
        if (r && r.staffCleaningAuditTrail && r.staffCleaningAuditTrail.length > 0) {
            r.staffCleaningAuditTrail.forEach(s => {
                csvRows.push([s.staffName, s.systemUserId, s.empId, s.assignedTime, s.completionTime]);
            });
        } else {
            csvRows.push(["No staff audit trail data recorded for the selected period"]);
        }
        csvRows.push([]);

        // Section 5: Task Submission & Verification Summary
        csvRows.push(["=== DAILY TASK SUBMISSION & ADMIN VERIFICATION SUMMARY ==="]);
        if (r && r.taskVerificationSummaryCounters) {
            csvRows.push(["Staff Submitted Tasks", r.taskVerificationSummaryCounters.submitted]);
            csvRows.push(["Admin Verified Tasks", r.taskVerificationSummaryCounters.verified]);
            csvRows.push(["Pending Verification", r.taskVerificationSummaryCounters.pending]);
        }
        csvRows.push(["Date", "Submitted", "Verified", "Pending", "Staff Breakdown"]);
        if (r && r.dailyTaskSummary && r.dailyTaskSummary.length > 0) {
            r.dailyTaskSummary.forEach(ts => {
                csvRows.push([ts.date, `${ts.submitted} Tasks`, `${ts.verified} Tasks`, `${ts.pending} Tasks`, ts.staffBreakdown]);
            });
        } else {
            csvRows.push(["No task submission summary data for the selected period"]);
        }
        csvRows.push([]);

        // Section 6: Alert & Task Lifecycle Timestamp Audit Trail
        csvRows.push(["=== DATE-WISE ALERT & TASK LIFECYCLE TIMESTAMP AUDIT TRAIL ==="]);
        csvRows.push(["Date", "Category & Title", "Created", "Started", "Submitted", "Verified", "Staff", "Updates", "Status"]);
        if (r && r.alertTaskAuditTrail && r.alertTaskAuditTrail.length > 0) {
            r.alertTaskAuditTrail.forEach(al => {
                csvRows.push([al.date, `${al.category}: ${al.title}`, al.created, al.started, al.submitted, al.verified, al.staff, al.updates, al.status]);
            });
        } else {
            csvRows.push(["No alert or task audit trail data recorded for the selected period"]);
        }

        const csvContent = csvRows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(",")).join("\n");
        res.setHeader("Content-Type", "text/csv; charset=utf-8");
        res.setHeader("Content-Disposition", `attachment; filename="sinexus_operational_report_${Date.now()}.csv"`);
        return res.status(200).send(csvContent);
    } catch (error) {
        console.error("Error generating CSV report:", error);
        return res.status(500).json({ success: false, message: "Server Error generating CSV report" });
    }
};

// 9. Download Report PDF (Matches Executive Restroom Audit Trail Visual Layout)
const downloadReportPdf = async (req, res) => {
    try {
        const dataset = await compileReportDataset(req);
        const {
            incScope = "true",
            incTelemetrySummary = "true",
            incDailyTelemetry = "true",
            incStaffAudit = "true",
            incTaskSummary = "true",
            incAlertAudit = "true"
        } = req.query;

        const showScope = incScope !== "false";
        const showTelemetrySummary = incTelemetrySummary !== "false";
        const showDailyTelemetry = incDailyTelemetry !== "false";
        const showStaffAudit = incStaffAudit !== "false";
        const showTaskSummary = incTaskSummary !== "false";
        const showAlertAudit = incAlertAudit !== "false";
        if (dataset.error) {
            return res.status(400).json({ success: false, message: dataset.error });
        }

        const { reportSummary, reports } = dataset;
        const r = reports.length > 0 ? reports[0] : null;

        const PDFDocument = require("pdfkit");
        const doc = new PDFDocument({ margin: 36, size: "A4", bufferPages: true });
        res.setHeader("Content-Type", "application/pdf");
        res.setHeader("Content-Disposition", `attachment; filename="sinexus_performance_report_${Date.now()}.pdf"`);
        doc.pipe(res);

        const margin = 36;
        const pageWidth = 595.28;
        const contentWidth = pageWidth - margin * 2; // 523.28 pt

        const drawHeaderBanner = () => {
            doc.roundedRect(margin, 36, contentWidth, 56, 6).fill("#111827");
            
            doc.fillColor("#FFFFFF").fontSize(15).font("Helvetica-Bold")
               .text("SINEXUS EDGE IOT PLATFORM", margin + 14, 46);
            doc.fillColor("#9CA3AF").fontSize(8.5).font("Helvetica")
               .text("Executive Restroom Telemetry & Operational Audit Report", margin + 14, 66);
            
            const badgeW = 95;
            const badgeH = 20;
            const badgeX = margin + contentWidth - badgeW - 14;
            const badgeY = 54;
            doc.roundedRect(badgeX, badgeY, badgeW, badgeH, 4).fill("#F59E0B");
            doc.fillColor("#000000").fontSize(8.5).font("Helvetica-Bold")
               .text("CONFIDENTIAL", badgeX, badgeY + 5, { width: badgeW, align: "center" });
        };

        const drawSectionHeader = (title, yPos) => {
            doc.rect(margin, yPos, 4, 15).fill("#2563EB");
            doc.fillColor("#1E293B").fontSize(11.5).font("Helvetica-Bold")
               .text(title, margin + 10, yPos + 1);
            return yPos + 22;
        };

        const renderCardRow = (cards, startY) => {
            const gap = 8;
            const numCards = cards.length;
            const cardW = (contentWidth - gap * (numCards - 1)) / numCards;
            const cardH = 44;

            cards.forEach((card, idx) => {
                const cardX = margin + idx * (cardW + gap);
                doc.roundedRect(cardX, startY, cardW, cardH, 5).fill("#F8FAFC");
                doc.roundedRect(cardX, startY, cardW, cardH, 5).strokeColor("#E2E8F0").lineWidth(0.5).stroke();
                
                doc.fillColor("#64748B").fontSize(7).font("Helvetica-Bold")
                   .text(card.label.toUpperCase(), cardX + 8, startY + 8, { width: cardW - 16 });
                doc.fillColor("#0F172A").fontSize(11.5).font("Helvetica-Bold")
                   .text(String(card.value), cardX + 8, startY + 22, { width: cardW - 16 });
            });
            return startY + cardH + 8;
        };

        // PAGE 1 BUILD
        drawHeaderBanner();
        let y = 106;

        // Section 1: Scope
        y = drawSectionHeader("Report Details & Scope", y);

        const scopeHeaders = ["Parameter", "Details / Metadata"];
        doc.rect(margin, y, contentWidth, 20).fill("#1E293B");
        doc.fillColor("#FFFFFF").fontSize(8.5).font("Helvetica-Bold");
        doc.text(scopeHeaders[0], margin + 8, y + 5);
        doc.text(scopeHeaders[1], margin + 138, y + 5);
        y += 20;

        const scopeRows = [
            ["Report Selected Period", reportSummary.period],
            ["Generated By Admin", `${reportSummary.adminName} (ID: ${reportSummary.adminId})`],
            ["Restroom / Device Unit", r ? `${r.deviceInfo.location} (ID: ${r.deviceInfo.deviceId})` : "N/A"],
            ["Current Device Status", r ? r.deviceInfo.status : "N/A"],
            ["Report Generated Time", new Date().toLocaleString("en-IN", { timeZone: "Asia/Kolkata", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false }).replace(",", "")]
        ];

        scopeRows.forEach((row, idx) => {
            const rowBg = idx % 2 === 1 ? "#F8FAFC" : "#FFFFFF";
            doc.rect(margin, y, contentWidth, 18).fill(rowBg);
            doc.rect(margin, y, contentWidth, 18).strokeColor("#E2E8F0").lineWidth(0.5).stroke();
            doc.fillColor("#334155").fontSize(8).font("Helvetica-Bold").text(row[0], margin + 8, y + 4);
            doc.fillColor("#1E293B").fontSize(8).font("Helvetica").text(row[1], margin + 138, y + 4);
            y += 18;
        });

        y += 12;

        // Section 2: Key Telemetry Summary
        y = drawSectionHeader("Key Telemetry & Operational Summary", y);

        const kt = r ? r.keyTelemetrySummary : {
            avgRating24h: "N/A", avgOdor24h: "N/A", totalUsage24h: "N/A",
            periodAvgRating: "N/A", periodAvgOdor: "N/A", periodTotalUsage: "N/A",
            assignedStaff: "N/A", lastCleaned: "N/A"
        };

        y = renderCardRow([
            { label: "24H AVG RATING", value: kt.avgRating24h },
            { label: "24H AVG ODOR", value: kt.avgOdor24h },
            { label: "24H TOTAL USAGE", value: kt.totalUsage24h }
        ], y);

        y = renderCardRow([
            { label: "PERIOD AVG RATING", value: kt.periodAvgRating },
            { label: "PERIOD AVG ODOR", value: kt.periodAvgOdor },
            { label: "PERIOD TOTAL USAGE", value: kt.periodTotalUsage }
        ], y);

        y = renderCardRow([
            { label: "ASSIGNED STAFF MEMBER", value: kt.assignedStaff },
            { label: "LAST CLEANED TIMESTAMP", value: kt.lastCleaned }
        ], y);

        y += 10;

        // Section 3: Daily Telemetry & Maintenance History
        y = drawSectionHeader("Daily Telemetry & Maintenance History", y);

        const dailyTableHeaders = ["Date", "Avg Star Rating", "Odor Level", "Usage Counter", "Cleaning Frequency"];
        const dailyTableWidths = [95, 105, 105, 105, contentWidth - 410];

        doc.rect(margin, y, contentWidth, 18).fill("#1E293B");
        doc.fillColor("#FFFFFF").fontSize(8).font("Helvetica-Bold");
        let dx = margin;
        dailyTableHeaders.forEach((h, idx) => {
            doc.text(h, dx + 8, y + 5, { width: dailyTableWidths[idx] });
            dx += dailyTableWidths[idx];
        });
        y += 18;

        const dailyRows = r ? r.dailyRatingTable : [];
        if (dailyRows.length > 0) {
            dailyRows.forEach((row, idx) => {
                const rowBg = idx % 2 === 1 ? "#F8FAFC" : "#FFFFFF";
                doc.rect(margin, y, contentWidth, 18).fill(rowBg);
                doc.rect(margin, y, contentWidth, 18).strokeColor("#E2E8F0").lineWidth(0.5).stroke();
                
                let x = margin;
                doc.fillColor("#334155").fontSize(7.5).font("Helvetica");
                doc.text(row.date, x + 8, y + 5, { width: dailyTableWidths[0] }); x += dailyTableWidths[0];
                
                const starStr = row.averageParticularRating !== "N/A" ? `${row.averageParticularRating} / 5.0` : "N/A";
                const odorStr = row.odorPpm !== "N/A" ? row.odorPpm : "N/A";
                const usageStr = row.usageCounter !== "N/A" ? String(row.usageCounter) : "N/A";

                doc.text(starStr, x + 8, y + 5, { width: dailyTableWidths[1] }); x += dailyTableWidths[1];
                doc.text(odorStr, x + 8, y + 5, { width: dailyTableWidths[2] }); x += dailyTableWidths[2];
                doc.text(usageStr, x + 8, y + 5, { width: dailyTableWidths[3] }); x += dailyTableWidths[3];
                doc.text(`${row.cleaningCount} Times`, x + 8, y + 5, { width: dailyTableWidths[4] });
                y += 18;
            });
        } else {
            doc.rect(margin, y, contentWidth, 18).fill("#FFFFFF");
            doc.rect(margin, y, contentWidth, 18).strokeColor("#E2E8F0").lineWidth(0.5).stroke();
            doc.fillColor("#64748B").fontSize(7.5).font("Helvetica").text("No telemetry or rating records found for the selected date range", margin + 8, y + 5);
            y += 18;
        }

        // PAGE 2 BUILD: Staff Cleaning Audit Trail
        doc.addPage();
        y = 36;
        y = drawSectionHeader("Staff Cleaning Audit Trail", y);

        const staffAuditHeaders = ["Staff Name", "System User ID", "Emp ID", "Assigned Time", "Completion Time"];
        const staffAuditWidths = [125, 95, 85, 110, contentWidth - 415];

        doc.rect(margin, y, contentWidth, 18).fill("#1E293B");
        doc.fillColor("#FFFFFF").fontSize(8).font("Helvetica-Bold");
        let sx = margin;
        staffAuditHeaders.forEach((h, idx) => {
            doc.text(h, sx + (idx === 0 ? 8 : 0), y + 5, { width: staffAuditWidths[idx] });
            sx += staffAuditWidths[idx];
        });
        y += 18;

        const staffRows = r ? r.staffCleaningAuditTrail : [];
        if (staffRows.length > 0) {
            staffRows.forEach((sr, idx) => {
                const rowBg = idx % 2 === 1 ? "#F8FAFC" : "#FFFFFF";
                doc.rect(margin, y, contentWidth, 18).fill(rowBg);
                doc.rect(margin, y, contentWidth, 18).strokeColor("#E2E8F0").lineWidth(0.5).stroke();
                
                let x = margin;
                doc.fillColor("#334155").fontSize(7.5).font("Helvetica");
                doc.text(sr.staffName, x + 8, y + 5, { width: staffAuditWidths[0] }); x += staffAuditWidths[0];
                doc.text(sr.systemUserId, x, y + 5, { width: staffAuditWidths[1] }); x += staffAuditWidths[1];
                doc.text(sr.empId, x, y + 5, { width: staffAuditWidths[2] }); x += staffAuditWidths[2];
                doc.text(sr.assignedTime, x, y + 5, { width: staffAuditWidths[3] }); x += staffAuditWidths[3];
                doc.text(sr.completionTime, x, y + 5, { width: staffAuditWidths[4] });
                y += 18;
            });
        } else {
            doc.rect(margin, y, contentWidth, 18).fill("#FFFFFF");
            doc.rect(margin, y, contentWidth, 18).strokeColor("#E2E8F0").lineWidth(0.5).stroke();
            doc.fillColor("#64748B").fontSize(7.5).font("Helvetica").text("No staff cleaning audit trail records found for the selected date range", margin + 8, y + 5);
            y += 18;
        }

        // PAGE 3 BUILD: Task Submission & Verification Summary + Audit Trail
        doc.addPage();
        y = 36;
        y = drawSectionHeader("Daily Task Submission & Admin Verification Summary", y);

        const taskCounters = r ? r.taskVerificationSummaryCounters : { submitted: 0, verified: 0, rejected: 0, pending: 0 };
        
        y = renderCardRow([
            { label: "STAFF SUBMITTED TASKS", value: String(taskCounters.submitted) },
            { label: "ADMIN VERIFIED TASKS", value: String(taskCounters.verified) },
            { label: "REJECTED TASKS", value: String(taskCounters.rejected || 0) },
            { label: "PENDING VERIFICATION", value: String(taskCounters.pending) }
        ], y);

        y += 4;
        doc.fillColor("#1E293B").fontSize(9).font("Helvetica-Bold").text("Date-Wise Task Submissions & Admin Verifications:", margin, y);
        y += 14;

        const subHeaders = ["Date", "Submitted", "Verified", "Rejected", "Pending", "Staff Breakdown"];
        const subWidths = [70, 65, 65, 65, 65, contentWidth - 330];

        doc.rect(margin, y, contentWidth, 18).fill("#1E293B");
        doc.fillColor("#FFFFFF").fontSize(8).font("Helvetica-Bold");
        let bx = margin;
        subHeaders.forEach((h, idx) => {
            doc.text(h, bx + 8, y + 5, { width: subWidths[idx] });
            bx += subWidths[idx];
        });
        y += 18;

        const subRows = r ? r.dailyTaskSummary : [];
        if (subRows.length > 0) {
            subRows.forEach((tr, idx) => {
                const rowBg = idx % 2 === 1 ? "#F8FAFC" : "#FFFFFF";
                doc.rect(margin, y, contentWidth, 18).fill(rowBg);
                doc.rect(margin, y, contentWidth, 18).strokeColor("#E2E8F0").lineWidth(0.5).stroke();
                
                let x = margin;
                doc.fillColor("#334155").fontSize(7.5).font("Helvetica");
                doc.text(tr.date, x + 8, y + 5, { width: subWidths[0] }); x += subWidths[0];
                doc.text(`${tr.submitted} Tasks`, x + 8, y + 5, { width: subWidths[1] }); x += subWidths[1];
                doc.text(`${tr.verified} Tasks`, x + 8, y + 5, { width: subWidths[2] }); x += subWidths[2];
                doc.text(`${tr.rejected || 0} Tasks`, x + 8, y + 5, { width: subWidths[3] }); x += subWidths[3];
                doc.text(`${tr.pending} Tasks`, x + 8, y + 5, { width: subWidths[4] }); x += subWidths[4];
                doc.text(tr.staffBreakdown, x + 8, y + 5, { width: subWidths[5] });
                y += 18;
            });
        } else {
            doc.rect(margin, y, contentWidth, 18).fill("#FFFFFF");
            doc.rect(margin, y, contentWidth, 18).strokeColor("#E2E8F0").lineWidth(0.5).stroke();
            doc.fillColor("#64748B").fontSize(7.5).font("Helvetica").text("No task submission records found for the selected date range", margin + 8, y + 5);
            y += 18;
        }

        y += 16;

        // Section 6: Alert & Task Lifecycle Timestamp Audit Trail
        y = drawSectionHeader("Date-Wise Alert & Task Lifecycle Timestamp Audit Trail", y);

        const auditTrailHeaders = ["Date", "Category & Title", "Created", "Started", "Submitted", "Verified", "Staff", "Updates", "Status"];
        const auditTrailWidths = [58, 157, 52, 45, 48, 48, 47, 35, 33];

        doc.rect(margin, y, contentWidth, 18).fill("#1E293B");
        doc.fillColor("#FFFFFF").fontSize(7.5).font("Helvetica-Bold");
        let ax = margin;
        auditTrailHeaders.forEach((h, idx) => {
            doc.text(h, ax + (idx === 0 ? 4 : 2), y + 5, { width: auditTrailWidths[idx] });
            ax += auditTrailWidths[idx];
        });
        y += 18;

        const alertRows = r ? r.alertTaskAuditTrail : [];
        if (alertRows.length > 0) {
            alertRows.forEach((ar, idx) => {
                if (y > 740) {
                    doc.addPage();
                    y = 36;
                    y = drawSectionHeader("Date-Wise Alert & Task Lifecycle Timestamp Audit Trail (Contd.)", y);
                    
                    doc.rect(margin, y, contentWidth, 18).fill("#1E293B");
                    doc.fillColor("#FFFFFF").fontSize(7.5).font("Helvetica-Bold");
                    let tx = margin;
                    auditTrailHeaders.forEach((h, hidx) => {
                        doc.text(h, tx + (hidx === 0 ? 4 : 2), y + 5, { width: auditTrailWidths[hidx] });
                        tx += auditTrailWidths[hidx];
                    });
                    y += 18;
                }

                const rowBg = idx % 2 === 1 ? "#F8FAFC" : "#FFFFFF";
                const titleLen = (ar.title || "").length;
                const baseRowH = Math.max(24, Math.ceil(titleLen / 36) * 10 + 12);
                const hasRejectionNotes = ar.rejectionReason && ar.rejectionReason !== "N/A";
                const subRowH = hasRejectionNotes ? 16 : 0;
                const totalH = baseRowH + subRowH;

                doc.rect(margin, y, contentWidth, totalH).fill(rowBg);
                doc.rect(margin, y, contentWidth, totalH).strokeColor("#E2E8F0").lineWidth(0.5).stroke();

                let x = margin;
                doc.fillColor("#334155").fontSize(7).font("Helvetica");
                doc.text(ar.date, x + 4, y + 4, { width: auditTrailWidths[0] }); x += auditTrailWidths[0];
                
                doc.font("Helvetica-Bold").text(ar.category, x + 2, y + 4, { width: auditTrailWidths[1] });
                doc.font("Helvetica").text(ar.title, x + 2, y + 13, { width: auditTrailWidths[1] }); x += auditTrailWidths[1];
                
                doc.text(ar.created, x + 2, y + 4, { width: auditTrailWidths[2] }); x += auditTrailWidths[2];
                doc.text(ar.started, x + 2, y + 4, { width: auditTrailWidths[3] }); x += auditTrailWidths[3];
                doc.text(ar.submitted, x + 2, y + 4, { width: auditTrailWidths[4] }); x += auditTrailWidths[4];
                doc.text(ar.verified, x + 2, y + 4, { width: auditTrailWidths[5] }); x += auditTrailWidths[5];
                doc.text(ar.staff, x + 2, y + 4, { width: auditTrailWidths[6] }); x += auditTrailWidths[6];
                doc.text(ar.updates, x + 2, y + 4, { width: auditTrailWidths[7] }); x += auditTrailWidths[7];

                const statusColor = ar.status === "VERIFIED" || ar.status === "RESOLVED" ? "#16A34A" :
                                   (ar.status === "CRITICAL" ? "#DC2626" : "#2563EB");
                doc.fillColor(statusColor).font("Helvetica-Bold").text(ar.status, x + 2, y + 4, { width: auditTrailWidths[8] });

                if (hasRejectionNotes) {
                    const subY = y + baseRowH - 2;
                    doc.rect(margin + 4, subY, contentWidth - 8, 14).fill("#FFFBEB");
                    doc.rect(margin + 4, subY, contentWidth - 8, 14).strokeColor("#FCD34D").lineWidth(0.5).stroke();
                    doc.fillColor("#B45309").fontSize(6.5).font("Helvetica-Bold")
                       .text("Rejection & Reassignment History: ", margin + 8, subY + 3, { continued: true })
                       .font("Helvetica")
                       .text(ar.rejectionReason, { width: contentWidth - 24 });
                }

                y += totalH;
            });
        } else {
            doc.rect(margin, y, contentWidth, 18).fill("#FFFFFF");
            doc.rect(margin, y, contentWidth, 18).strokeColor("#E2E8F0").lineWidth(0.5).stroke();
            doc.fillColor("#64748B").fontSize(7.5).font("Helvetica").text("No alert or task audit trail records found for the selected date range", margin + 4, y + 5);
            y += 18;
        }

        // FOOTER WRAPPER FOR ALL PAGES
        const range = doc.bufferedPageRange();
        for (let i = range.start; i < range.start + range.count; i++) {
            doc.switchToPage(i);
            doc.moveTo(margin, 804).lineTo(margin + contentWidth, 804).strokeColor("#CBD5E1").lineWidth(0.5).stroke();
            doc.fillColor("#94A3B8").fontSize(7.5).font("Helvetica")
               .text("Confidential report automatically compiled by Sinexus Edge IoT Platform", margin, 810, { lineBreak: false });
            doc.text(`Page ${i + 1} of ${range.count}`, margin, 810, { width: contentWidth, align: "right", lineBreak: false });
        }

        doc.end();
    } catch (error) {
        console.error("Error generating PDF report:", error);
        return res.status(500).json({ success: false, message: "Server Error generating PDF report" });
    }
};

module.exports = {
    getDailyReport,
    getWeeklyReport,
    getMonthlyReport,
    getReportStats,
    getReportsList,
    generateReport,
    getDeviceReports,
    downloadReportCsv,
    downloadReportPdf
};
