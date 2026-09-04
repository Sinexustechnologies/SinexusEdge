const fs = require('fs');
const path = require('path');

const possiblePaths = [
    'C:\\Users\\admin\\Downloads\\synxeus_fontend\\lib\\screens\\alert_detail_screen.dart',
    'C:\\Users\\admin\\Downloads\\sin-front-main\\lib\\screens\\alert_detail_screen.dart',
    'C:\\Users\\admin\\Downloads\\synxeus_frontend\\lib\\screens\\alert_detail_screen.dart'
];

possiblePaths.forEach(p => {
    console.log(`Checking ${p}: ${fs.existsSync(p)}`);
});
