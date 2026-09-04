const fs = require('fs');

const files = [
    'C:\\Users\\admin\\Downloads\\synxeus_fontend\\lib\\screens\\alert_detail_screen.dart',
    'C:\\Users\\admin\\Downloads\\sin-front-main\\lib\\screens\\alert_detail_screen.dart'
];

files.forEach(file => {
    if (fs.existsSync(file)) {
        console.log(`\n=== File: ${file} ===`);
        const content = fs.readFileSync(file, 'utf8');
        const lines = content.split('\n');
        lines.forEach((line, idx) => {
            if (line.includes('!') && !line.includes('!=') && !line.includes('!is') && !line.includes('!_') && !line.includes('!alert') && !line.includes('!mounted')) {
                console.log(`Line ${idx + 1}: ${line.trim()}`);
            }
        });
    }
});
