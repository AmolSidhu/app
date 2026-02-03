import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/mtg/requests/viewAllScrapersRequest.dart';

class ViewScraperPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('View Scraper Page')),
      body: Center(child: ViewAllScraperRequest()),
    );
  }
}
