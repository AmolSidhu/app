import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_frontend/static/constants.dart';

class MagicCardLegalitiesPopup extends StatefulWidget {
  final String cardId;
  final String cardName;

  const MagicCardLegalitiesPopup({
    super.key,
    required this.cardId,
    required this.cardName,
  });

  @override
  State<MagicCardLegalitiesPopup> createState() =>
      _MagicCardLegalitiesPopupState();
}

class _MagicCardLegalitiesPopupState extends State<MagicCardLegalitiesPopup> {
  final FlutterSecureStorage secureStorage = const FlutterSecureStorage();

  bool isLoading = true;
  String statusMessage = '';
  Map<String, dynamic> legalities = {};

  @override
  void initState() {
    super.initState();
    fetchLegalities();
  }

  Future<void> fetchLegalities() async {
    try {
      final token = await secureStorage.read(key: 'token');

      if (token == null) {
        setState(() {
          isLoading = false;
          statusMessage = 'No auth token found.';
        });
        return;
      }

      final url = "$server/get/magic_card_legalities/${widget.cardId}/";

      final response = await http.get(
        Uri.parse(url),
        headers: {"Authorization": token, "Content-Type": "application/json"},
      );

      if (response.statusCode == 200) {
        final decoded = jsonDecode(response.body);
        setState(() {
          legalities = decoded["data"];
          isLoading = false;
        });
      } else {
        setState(() {
          isLoading = false;
          statusMessage = "Error: ${response.body}";
        });
      }
    } catch (e) {
      setState(() {
        isLoading = false;
        statusMessage = "Exception: $e";
      });
    }
  }

  Widget legalityRow(String name, bool value) {
    return Row(
      children: [
        Icon(Icons.circle, size: 14, color: value ? Colors.green : Colors.red),
        const SizedBox(width: 8),
        Text(name, style: const TextStyle(fontSize: 14)),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('Legalities for ${widget.cardName}'),
      content: SizedBox(
        width: 420,
        child: isLoading
            ? const Center(child: CircularProgressIndicator())
            : legalities.isEmpty
            ? Text(statusMessage)
            : Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: legalities.entries.map((entry) {
                  return Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: legalityRow(entry.key, entry.value),
                  );
                }).toList(),
              ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Close'),
        ),
      ],
    );
  }
}
