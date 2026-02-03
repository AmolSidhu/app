import 'package:flutter/material.dart';
import 'package:flutter_frontend/pages/auth/loginPage.dart';
import 'package:flutter_frontend/pages/auth/registrationPage.dart';
import 'package:flutter_frontend/pages/auth/verificationPage.dart';

class LoginNavbar extends StatefulWidget {
  const LoginNavbar({super.key});

  @override
  State<LoginNavbar> createState() => _LoginNavbarState();
}

class _LoginNavbarState extends State<LoginNavbar>
    with TickerProviderStateMixin {
  late final TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Test App'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(icon: Icon(Icons.login), text: 'Login'),
            Tab(icon: Icon(Icons.verified), text: 'Verification'),
            Tab(icon: Icon(Icons.app_registration), text: 'Register'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [LoginPage(), VerificationPage(), RegistrationPage()],
      ),
    );
  }
}
