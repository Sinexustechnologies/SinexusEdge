const fs = require('fs');

const alertDetailPath = 'C:\\Users\\admin\\Downloads\\sin-front-main\\lib\\screens\\alert_detail_screen.dart';
const alertsPath = 'C:\\Users\\admin\\Downloads\\sin-front-main\\lib\\screens\\alerts_screen.dart';

// 1. Fix alert_detail_screen.dart
if (fs.existsSync(alertDetailPath)) {
    let content = fs.readFileSync(alertDetailPath, 'utf8');

    // Replace nested Row inside Wrap for Device UID Badge in alert_detail_screen.dart
    const regexDetailBadge = /child:\s*Wrap\([\s\S]*?children:\s*\[\s*Row\(\s*mainAxisSize:\s*MainAxisSize\.min,\s*children:\s*\[\s*const\s+Icon\(Icons\.developer_board_rounded[\s\S]*?Text\(\s*'Device ID:\s*\$\{_alert\.deviceId\s*\?\?\s*"N\/A"\}'[\s\S]*?\),\s*\),\s*\],\s*\),/g;

    const replaceDetailBadge = `child: Wrap(
                                crossAxisAlignment: WrapCrossAlignment.center,
                                spacing: 6,
                                runSpacing: 4,
                                children: [
                                  const Icon(Icons.developer_board_rounded, color: AppColors.primary, size: 14),
                                  Text(
                                    'Device ID: \${_alert.deviceId ?? "N/A"}',
                                    style: const TextStyle(
                                      color: AppColors.primary,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 11.5,
                                    ),
                                  ),`;

    if (regexDetailBadge.test(content)) {
        content = content.replace(regexDetailBadge, replaceDetailBadge);
        console.log('✅ Replaced Device ID badge in alert_detail_screen.dart');
    } else {
        console.log('⚠️ regexDetailBadge pattern not matched in alert_detail_screen.dart');
    }

    // Top Row Spacer replacement in alert_detail_screen.dart
    const regexDetailTopRow = /\/\/\/\s*TOP ROW:\s*Status Badge & Device UID\s*Row\(\s*children:\s*\[\s*_buildStatusChip\(context,\s*_alert\),\s*const\s+Spacer\(\),/g;
    const replaceDetailTopRow = `/// TOP ROW: Status Badge & Device UID
                            Row(
                              crossAxisAlignment: CrossAxisAlignment.center,
                              children: [
                                Flexible(
                                  child: _buildStatusChip(context, _alert),
                                ),
                                const SizedBox(width: 8),`;

    if (regexDetailTopRow.test(content)) {
        content = content.replace(regexDetailTopRow, replaceDetailTopRow);
        console.log('✅ Replaced Top Row in alert_detail_screen.dart');
    } else {
        console.log('⚠️ regexDetailTopRow pattern not matched in alert_detail_screen.dart');
    }

    fs.writeFileSync(alertDetailPath, content, 'utf8');
}

// 2. Fix alerts_screen.dart
if (fs.existsSync(alertsPath)) {
    let content = fs.readFileSync(alertsPath, 'utf8');

    const regexAlertsBadge = /child:\s*Wrap\([\s\S]*?children:\s*\[\s*Row\(\s*mainAxisSize:\s*MainAxisSize\.min,\s*children:\s*\[\s*const\s+Icon\(Icons\.developer_board_rounded[\s\S]*?Text\(\s*'Device ID:\s*\$\{alert\.deviceId\s*\?\?\s*"N\/A"\}'[\s\S]*?\),\s*\),\s*\],\s*\),/g;

    const replaceAlertsBadge = `child: Wrap(
                                             crossAxisAlignment: WrapCrossAlignment.center,
                                             spacing: 6,
                                             runSpacing: 4,
                                             children: [
                                               const Icon(Icons.developer_board_rounded, color: AppColors.primary, size: 14),
                                               Text(
                                                 'Device ID: \${alert.deviceId ?? "N/A"}',
                                                 style: const TextStyle(
                                                   color: AppColors.primary,
                                                   fontWeight: FontWeight.bold,
                                                   fontSize: 11.5,
                                                 ),
                                               ),`;

    if (regexAlertsBadge.test(content)) {
        content = content.replace(regexAlertsBadge, replaceAlertsBadge);
        console.log('✅ Replaced Device ID badge in alerts_screen.dart');
    } else {
        console.log('⚠️ regexAlertsBadge pattern not matched in alerts_screen.dart');
    }

    fs.writeFileSync(alertsPath, content, 'utf8');
}
