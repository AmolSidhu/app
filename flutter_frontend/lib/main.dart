import 'package:flutter/material.dart';
import 'package:flutter_frontend/authGate.dart';
import 'package:flutter_frontend/static/mainNavbar.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      builder: (context, child) {
        return Navigator(
          key: MainNavbar.rootNav,
          onGenerateRoute: (_) => MaterialPageRoute(builder: (_) => child!),
        );
      },
      home: const AuthGate(),
    );
  }
}
