import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_frontend/static/mainNavbar.dart';
import 'package:flutter_frontend/static/constants.dart';
import 'package:flutter_frontend/assets/admin/requests/adminCheckRequest.dart';

class LoginForm extends StatefulWidget {
  const LoginForm({Key? key}) : super(key: key);

  @override
  State<LoginForm> createState() => _LoginFormState();
}

class _LoginFormState extends State<LoginForm> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  Future<void> _login() async {
    if (!_formKey.currentState!.validate()) return;

    final response = await http.patch(
      Uri.parse('$server/login/'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'email': _emailController.text,
        'password': _passwordController.text,
      }),
    );

    if (response.statusCode == 200) {
      final token = jsonDecode(response.body)['token'];

      const secureStorage = FlutterSecureStorage();
      await secureStorage.write(key: 'token', value: token);

      final bool isAdmin = await AdminCheckRequest.adminCheckRequest();

      if (!mounted) return;

      Navigator.of(context, rootNavigator: true).pushReplacement(
        MaterialPageRoute(builder: (_) => MainNavbar(isAdmin: isAdmin)),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(jsonDecode(response.body)['message'])),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        children: [
          TextFormField(
            controller: _emailController,
            decoration: const InputDecoration(labelText: 'Email'),
            validator: (value) => value == null || value.isEmpty
                ? 'Please enter your email'
                : null,
          ),
          TextFormField(
            controller: _passwordController,
            decoration: const InputDecoration(labelText: 'Password'),
            obscureText: true,
            validator: (value) => value == null || value.isEmpty
                ? 'Please enter your password'
                : null,
          ),
          ElevatedButton(onPressed: _login, child: const Text('Login')),
        ],
      ),
    );
  }
}
