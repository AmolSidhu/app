import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/auth/forms/loginForm.dart';

class LoginPage extends StatelessWidget {
  const LoginPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(child: LoginForm());
  }
}
