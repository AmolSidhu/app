import 'dart:typed_data';
import 'dart:html' as html;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_frontend/static/constants.dart';

class MagicCardImagePopup extends StatefulWidget {
  final String cardId;
  final String cardName;

  const MagicCardImagePopup({
    super.key,
    required this.cardId,
    required this.cardName,
  });

  @override
  State<MagicCardImagePopup> createState() => _MagicCardImagePopupState();
}

class _MagicCardImagePopupState extends State<MagicCardImagePopup> {
  final FlutterSecureStorage secureStorage = const FlutterSecureStorage();

  bool isLoading = true;
  String statusMessage = '';

  Uint8List? frontImage;
  Uint8List? backImage;

  String? frontUrl;
  String? backUrl;

  @override
  void initState() {
    super.initState();
    fetchFrontImage();
  }

  @override
  void dispose() {
    if (frontUrl != null) html.Url.revokeObjectUrl(frontUrl!);
    if (backUrl != null) html.Url.revokeObjectUrl(backUrl!);
    super.dispose();
  }

  Future<void> fetchFrontImage() async {
    try {
      final token = await secureStorage.read(key: 'token');
      if (token == null) {
        setState(() {
          isLoading = false;
          statusMessage = 'No auth token found.';
        });
        return;
      }

      final url =
          "$server/get/magic_card_image/${widget.cardId}/?card_back=false";

      final response = await http.get(
        Uri.parse(url),
        headers: {"Authorization": token},
      );

      if (response.statusCode != 200) {
        setState(() {
          isLoading = false;
          statusMessage = "Error: ${response.body}";
        });
        return;
      }

      frontImage = response.bodyBytes;
      frontUrl = html.Url.createObjectUrlFromBlob(html.Blob([frontImage!]));

      final backExistsHeader = response.headers["back-exists"];

      final backExists = backExistsHeader == "true";

      if (backExists) {
        await fetchBackImage(token);
      } else {}

      setState(() {
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        isLoading = false;
        statusMessage = "Exception: $e";
      });
    }
  }

  Future<void> fetchBackImage(String token) async {
    final url = "$server/get/magic_card_image/${widget.cardId}/?card_back=true";

    final response = await http.get(
      Uri.parse(url),
      headers: {"Authorization": token},
    );

    if (response.statusCode != 200) {
      return;
    }

    backImage = response.bodyBytes;
    backUrl = html.Url.createObjectUrlFromBlob(html.Blob([backImage!]));
  }

  Widget buildImage(String? url) {
    if (url == null) {
      return const SizedBox(width: 300, height: 420);
    }

    return Image.network(url, width: 300, height: 420, fit: BoxFit.contain);
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('Images for ${widget.cardName}'),
      content: SizedBox(
        width: 650,
        child: isLoading
            ? const Center(child: CircularProgressIndicator())
            : Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (statusMessage.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: Text(statusMessage),
                    ),

                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      buildImage(frontUrl),
                      const SizedBox(width: 20),
                      buildImage(backUrl),
                    ],
                  ),
                ],
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
