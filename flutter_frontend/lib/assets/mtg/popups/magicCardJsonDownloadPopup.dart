import 'dart:convert';
import 'dart:html' as html;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_frontend/static/constants.dart';

class MagicCardJsonDownloadPopup extends StatefulWidget {
  final String cardId;
  final String cardName;

  const MagicCardJsonDownloadPopup({
    super.key,
    required this.cardId,
    required this.cardName,
  });

  @override
  State<MagicCardJsonDownloadPopup> createState() =>
      _MagicCardJsonDownloadPopupState();
}

class _MagicCardJsonDownloadPopupState
    extends State<MagicCardJsonDownloadPopup> {
  final FlutterSecureStorage secureStorage = const FlutterSecureStorage();

  bool isLoading = false;
  String statusMessage = '';

  Future<void> downloadJson() async {
    setState(() {
      isLoading = true;
      statusMessage = '';
    });

    try {
      final token = await secureStorage.read(key: 'token');

      if (token == null) {
        setState(() {
          isLoading = false;
          statusMessage = 'No auth token found.';
        });
        return;
      }

      final url = "$server/get/magic_card_json/${widget.cardId}/";

      final response = await http.get(
        Uri.parse(url),
        headers: {"Authorization": token, "Content-Type": "application/json"},
      );

      if (response.statusCode == 200) {
        final decoded = jsonDecode(response.body);

        if (!decoded.containsKey("data")) {
          setState(() {
            isLoading = false;
            statusMessage = "Invalid JSON response.";
          });
          return;
        }

        final jsonData = jsonEncode(decoded["data"]);

        final bytes = utf8.encode(jsonData);
        final blob = html.Blob([bytes], 'application/json');
        final urlBlob = html.Url.createObjectUrlFromBlob(blob);

        final anchor = html.AnchorElement(href: urlBlob)
          ..setAttribute("download", "${widget.cardId}.json")
          ..click();

        html.Url.revokeObjectUrl(urlBlob);

        setState(() {
          isLoading = false;
          statusMessage = "Download complete.";
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

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('Download JSON for ${widget.cardName}'),
      content: SizedBox(
        width: 420,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (isLoading) const CircularProgressIndicator(),
            if (statusMessage.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 12),
                child: Text(statusMessage),
              ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: isLoading ? null : downloadJson,
          child: const Text('Download JSON'),
        ),
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Close'),
        ),
      ],
    );
  }
}
