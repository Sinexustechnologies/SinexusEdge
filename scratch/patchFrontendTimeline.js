const fs = require('fs');
const path = require('path');

const alertDetailPath = 'C:\\Users\\admin\\Downloads\\sin-front-main\\lib\\screens\\alert_detail_screen.dart';
const timelineDialogPath = 'C:\\Users\\admin\\Downloads\\sin-front-main\\lib\\widgets\\dialogs\\task_timeline_dialog.dart';

// 1. Patch alert_detail_screen.dart
if (fs.existsSync(alertDetailPath)) {
    let content = fs.readFileSync(alertDetailPath, 'utf8');
    const target1 = 'if (isRejected || isReassigned || alert.adminRemarks.isNotEmpty) {';
    const replace1 = 'if (isRejected) {';
    
    if (content.includes(target1)) {
        content = content.replace(target1, replace1);
        fs.writeFileSync(alertDetailPath, content, 'utf8');
        console.log('✅ Patched alert_detail_screen.dart successfully');
    } else {
        console.log('⚠️ Target string not found in alert_detail_screen.dart');
    }
} else {
    console.log('❌ alert_detail_screen.dart not found at ' + alertDetailPath);
}

// 2. Patch task_timeline_dialog.dart
if (fs.existsSync(timelineDialogPath)) {
    let content = fs.readFileSync(timelineDialogPath, 'utf8');
    const target2 = 'if (isRejected || isReassigned || task.adminRemarks.isNotEmpty) {';
    const replace2 = 'if (isRejected) {';
    
    if (content.includes(target2)) {
        content = content.replace(target2, replace2);
        fs.writeFileSync(timelineDialogPath, content, 'utf8');
        console.log('✅ Patched task_timeline_dialog.dart successfully');
    } else {
        console.log('⚠️ Target string not found in task_timeline_dialog.dart');
    }
} else {
    console.log('❌ task_timeline_dialog.dart not found at ' + timelineDialogPath);
}
