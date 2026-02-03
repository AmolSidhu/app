import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/analytics/switch/dataSourceSwitch.dart';

class UploadDataSourcePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Upload Data Source')),
      body: Center(child: DataSourceSwitch()),
    );
  }
}
