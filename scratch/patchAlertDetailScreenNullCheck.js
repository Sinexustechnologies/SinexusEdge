const fs = require('fs');

const files = [
    'C:\\Users\\admin\\Downloads\\synxeus_fontend\\lib\\screens\\alert_detail_screen.dart',
    'C:\\Users\\admin\\Downloads\\sin-front-main\\lib\\screens\\alert_detail_screen.dart'
];

files.forEach(filePath => {
    if (!fs.existsSync(filePath)) {
        console.log(`❌ File not found: ${filePath}`);
        return;
    }

    let content = fs.readFileSync(filePath, 'utf8');
    let modified = false;

    // 1. Replace 'time': alert.completedAt!
    const targetCompleted = "'time': alert.completedAt!";
    const replacementCompleted = "'time': alert.completedAt ?? alert.submittedAt ?? alert.updatedAt ?? alert.createdAt";

    if (content.includes(targetCompleted)) {
        content = content.replaceAll(targetCompleted, replacementCompleted);
        modified = true;
        console.log(`✅ Patched alert.completedAt! in ${filePath}`);
    }

    // 2. Replace 'time': alert.verifiedAt!
    const targetVerified = "'time': alert.verifiedAt!";
    const replacementVerified = "'time': alert.verifiedAt ?? alert.resolvedAt ?? alert.completedAt ?? alert.updatedAt ?? alert.createdAt";

    if (content.includes(targetVerified)) {
        content = content.replaceAll(targetVerified, replacementVerified);
        modified = true;
        console.log(`✅ Patched alert.verifiedAt! in ${filePath}`);
    }

    if (modified) {
        fs.writeFileSync(filePath, content, 'utf8');
        console.log(`💾 Saved changes to ${filePath}`);
    } else {
        console.log(`ℹ️ No target strings found in ${filePath}`);
    }
});
