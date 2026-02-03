import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_frontend/static/constants.dart';

class AdminCheckRequest {
  static Future<bool> adminCheckRequest() async {
    const storage = FlutterSecureStorage();

    final userToken = await storage.read(key: 'token');
    if (userToken == null) return false;

    try {
      final res = await http.get(
        Uri.parse('$server/admins/check/'),
        headers: {
          'Authorization': userToken,
          'Content-Type': 'application/json',
        },
      );

      if (res.statusCode == 200) {
        final Map<String, dynamic> json = jsonDecode(res.body);

        if (json['admin_token'] != null) {
          await storage.write(key: 'adminToken', value: json['admin_token']);
        }

        return true;
      }

      return false;
    } catch (_) {
      return false;
    }
  }
}
