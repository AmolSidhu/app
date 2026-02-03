import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/mtg/requests/viewScraperHistoryRequest.dart';

class ViewScraperHistoryPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Scraper History')),
      body: Center(child: ViewScraperHistoryRequest()),
    );
  }
}
