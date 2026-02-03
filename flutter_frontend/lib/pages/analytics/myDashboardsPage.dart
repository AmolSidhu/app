import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/analytics/requests/viewDasahboardsRequest.dart';
import 'package:flutter_frontend/assets/analytics/popups/createDashboardPopup.dart';

class MyDashboardsPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Dashboards'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            tooltip: 'Create Dashboard',
            onPressed: () {
              showDialog(
                context: context,
                barrierDismissible: false,
                builder: (_) => CreateDashboardPopup(
                  onClose: () => Navigator.of(context).pop(),
                ),
              );
            },
          ),
        ],
      ),
      body: ViewDashboardsRequest(),
    );
  }
}
