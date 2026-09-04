const fs = require('fs');

const file = 'C:\\Users\\admin\\Downloads\\synxeus_fontend\\lib\\screens\\alert_detail_screen.dart';
if (fs.existsSync(file)) {
    const lines = fs.readFileSync(file, 'utf8').split('\n');
    console.log(lines.slice(200, 300).map((l, i) => `${i + 201}: ${l}`).join('\n'));
}
