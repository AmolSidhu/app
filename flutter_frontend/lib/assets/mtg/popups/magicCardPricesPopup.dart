import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_frontend/static/constants.dart';

class MagicCardPricesPopup extends StatefulWidget {
  final String cardId;
  final String cardName;

  const MagicCardPricesPopup({
    super.key,
    required this.cardId,
    required this.cardName,
  });

  @override
  State<MagicCardPricesPopup> createState() => _MagicCardPricesPopupState();
}

class _MagicCardPricesPopupState extends State<MagicCardPricesPopup> {
  final FlutterSecureStorage secureStorage = const FlutterSecureStorage();

  bool isLoading = true;
  String statusMessage = '';
  Map<String, dynamic> prices = {};

  @override
  void initState() {
    super.initState();
    fetchPrices();
  }

  Future<void> fetchPrices() async {
    try {
      final token = await secureStorage.read(key: 'token');

      if (token == null) {
        setState(() {
          isLoading = false;
          statusMessage = 'No auth token found.';
        });
        return;
      }

      final url = "$server/get/magic_card_prices/${widget.cardId}/";

      final response = await http.get(
        Uri.parse(url),
        headers: {"Authorization": token, "Content-Type": "application/json"},
      );

      if (response.statusCode == 200) {
        final decoded = jsonDecode(response.body);
        setState(() {
          prices = decoded["data"];
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

  Widget priceRow(String label, dynamic value) {
    final formatted = value == null ? "N/A" : value.toString();

    return Row(
      children: [
        const Icon(Icons.attach_money, size: 16, color: Colors.blue),
        const SizedBox(width: 8),
        Text("$label: $formatted", style: const TextStyle(fontSize: 14)),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('Prices for ${widget.cardName}'),
      content: SizedBox(
        width: 420,
        child: isLoading
            ? const Center(child: CircularProgressIndicator())
            : prices.isEmpty
            ? Text(statusMessage)
            : Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: prices.entries.map((entry) {
                  return Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: priceRow(entry.key, entry.value),
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
