import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/auth/forms/loginForm.dart';

class LoginPage extends StatelessWidget {
  const LoginPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Login')),
      body: Padding(padding: const EdgeInsets.all(16.0), child: LoginForm()),
    );
  }
}
