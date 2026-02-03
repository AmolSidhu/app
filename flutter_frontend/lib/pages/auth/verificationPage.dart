import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/auth/forms/verificationForm.dart';

class VerificationPage extends StatelessWidget {
  const VerificationPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Verification')),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: VerificationForm(),
        ),
      ),
    );
  }
}
