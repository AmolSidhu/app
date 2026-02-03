import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_frontend/static/loginNavbar.dart';
import 'package:flutter_frontend/static/mainNavbar.dart';

class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  String? _token;
  bool _isAdmin = false;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadAuth();
  }

  Future<void> _loadAuth() async {
    final token = await _storage.read(key: 'token');
    final adminToken = await _storage.read(key: 'adminToken');

    setState(() {
      _token = token;
      _isAdmin = adminToken != null;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    if (_token == null) {
      return const LoginNavbar();
    }

    return MainNavbar(isAdmin: _isAdmin);
  }
}
