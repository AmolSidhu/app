import 'package:flutter/material.dart';
import 'package:flutter_frontend/assets/mtg/requests/viewAllMagicCardsRequest.dart';
import 'package:flutter_frontend/assets/mtg/popups/magicCardsColumnPopup.dart';
import 'package:flutter_frontend/assets/mtg/popups/magicCardsFilterPopup.dart';

class ViewAllMagicCardsPage extends StatefulWidget {
  const ViewAllMagicCardsPage({Key? key}) : super(key: key);

  @override
  State<ViewAllMagicCardsPage> createState() => _ViewAllMagicCardsPageState();
}

class _ViewAllMagicCardsPageState extends State<ViewAllMagicCardsPage> {
  final GlobalKey<ViewAllMagicCardsRequestState> _tableKey =
      GlobalKey<ViewAllMagicCardsRequestState>();

  void _openColumnPopup() {
    showDialog(
      context: context,
      builder: (context) => MagicColumnsViewOptionsPopup(
        onSaved: () {
          _tableKey.currentState?.refresh();
        },
      ),
    );
  }

  void _openFilterPopup() {
    showDialog(
      context: context,
      builder: (context) => MagicCardFilterPopup(
        onSaved: () {
          _tableKey.currentState?.refresh();
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('View All Magic Cards'),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_alt),
            tooltip: "Filter Options",
            onPressed: _openFilterPopup,
          ),
          IconButton(
            icon: const Icon(Icons.view_column),
            tooltip: "Column Options",
            onPressed: _openColumnPopup,
          ),
        ],
      ),
      body: ViewAllMagicCardsRequest(key: _tableKey),
    );
  }
}
