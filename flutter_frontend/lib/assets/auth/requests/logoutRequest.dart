import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_frontend/static/constants.dart';

final FlutterSecureStorage secureStorage = const FlutterSecureStorage();

Future<void> logoutRequest() async {
  final response = await http.patch(Uri.parse('$server/logout/'));

  if (response.statusCode >= 200 && response.statusCode < 300) {
    await secureStorage.delete(key: 'token');
  }
}
